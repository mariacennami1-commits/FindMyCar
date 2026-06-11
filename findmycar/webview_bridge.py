from kivy.logger import Logger
from kivy.utils import platform

from .map_html import MAP_HTML


class WebViewBridge:
    _instance = None
    _webview = None

    def __init__(self):
        self._callback = None

    def setup(self, callback=None):
        self._callback = callback
        if platform != "android":
            Logger.info("WebViewBridge: Not on Android, skipping")
            return
        try:
            self._create_webview()
        except Exception as e:
            Logger.error("WebViewBridge: Setup failed - " + str(e))
            import traceback
            Logger.error(traceback.format_exc())

    def _create_webview(self):
        from jnius import autoclass
        from android import mActivity

        WebView = autoclass("android.webkit.WebView")
        WebSettings = autoclass("android.webkit.WebSettings")
        WebViewClient = autoclass("android.webkit.WebViewClient")
        RelativeLayout = autoclass("android.widget.RelativeLayout")
        ViewGroup = autoclass("android.view.ViewGroup")
        View = autoclass("android.view.View")

        PythonActivity = autoclass("org.kivy.android.PythonActivity")
        activity = PythonActivity.mActivity

        self._webview = WebView(activity)
        self._webview.setBackgroundColor(0x00131315)

        settings = self._webview.getSettings()
        settings.setJavaScriptEnabled(True)
        settings.setDomStorageEnabled(True)
        settings.setCacheMode(WebSettings.LOAD_DEFAULT)
        settings.setAllowFileAccess(False)
        settings.setGeolocationEnabled(True)

        self._webview.getSettings().setMixedContentMode(
            WebSettings().MIXED_CONTENT_ALWAYS_ALLOW
        )

        class BridgeClient(WebViewClient):
            def __init__(self, bridge):
                super().__init__()
                self._bridge = bridge

            def shouldOverrideUrlLoading(self, view, request):
                url = request.getUrl().toString()
                if url and url.startswith("app://"):
                    self._bridge._handle_url(url)
                    return True
                return False

            def onPageFinished(self, view, url):
                Logger.info("WebViewBridge: Page loaded: " + str(url))
                if self._bridge._callback:
                    self._bridge._callback("page_loaded", None)

        client = BridgeClient(self)
        self._webview.setWebViewClient(client)

        String = autoclass("java.lang.String")
        self._webview.loadDataWithBaseURL(
            None,
            String(MAP_HTML),
            String("text/html"),
            String("UTF-8"),
            None,
        )
        Logger.info("WebViewBridge: HTML loaded via loadDataWithBaseURL")

        params = RelativeLayout.LayoutParams(
            ViewGroup.LayoutParams.MATCH_PARENT,
            ViewGroup.LayoutParams.MATCH_PARENT,
        )
        activity.mLayout.addView(self._webview, params)
        self._webview.setVisibility(View.GONE)
        Logger.info("WebViewBridge: Created and hidden")

    def _handle_url(self, url):
        Logger.info("WebViewBridge: URL=" + str(url))
        try:
            parts = url.replace("app://", "", 1).split("/")
            command = parts[0]
            arg = parts[1] if len(parts) > 1 else None
            Logger.info("WebViewBridge: command=" + str(command) + " arg=" + str(arg))
            if self._callback:
                if command == "save":
                    self._callback("save", None)
                elif command == "navigate":
                    self._callback("navigate", arg)
                elif command == "open-drawer":
                    self._callback("open_drawer", None)
                elif command == "show-toast":
                    self._callback("toast", arg)
                else:
                    self._callback("unknown", command)
        except Exception as e:
            Logger.error("WebViewBridge: URL handler error - " + str(e))

    def show(self):
        if not self._webview:
            return
        try:
            from jnius import autoclass
            View = autoclass("android.view.View")
            self._webview.setVisibility(View.VISIBLE)
            Logger.info("WebViewBridge: Shown")
        except Exception as e:
            Logger.error("WebViewBridge: show error - " + str(e))

    def hide(self):
        if not self._webview:
            return
        try:
            from jnius import autoclass
            View = autoclass("android.view.View")
            self._webview.setVisibility(View.GONE)
            Logger.info("WebViewBridge: Hidden")
        except Exception as e:
            Logger.error("WebViewBridge: hide error - " + str(e))

    def send_js(self, js_code):
        if not self._webview:
            return
        try:
            from android import mActivity
            mActivity.runOnUiThread(lambda: self._webview.evaluateJavascript(js_code, None))
        except Exception as e:
            Logger.warning("WebViewBridge: send_js error - " + str(e))

    def destroy(self):
        try:
            from jnius import autoclass
            ViewGroup = autoclass("android.view.ViewGroup")
            from android import mActivity
            if self._webview:
                parent = self._webview.getParent()
                if parent:
                    parent.removeView(self._webview)
                self._webview.destroy()
                self._webview = None
            Logger.info("WebViewBridge: Destroyed")
        except Exception as e:
            Logger.warning("WebViewBridge: destroy error - " + str(e))
