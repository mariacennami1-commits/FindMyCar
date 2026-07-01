import traceback as _tb
from kivy.logger import Logger
from kivy.utils import platform


class _JSBridge:
    """Lazy holder for the PythonJavaClass JS interface."""
    _class = None

    @classmethod
    def get_class(cls):
        if cls._class is None:
            from jnius import PythonJavaClass, java_method
            class _JSI(PythonJavaClass):
                __javainterfaces__ = ['android/webkit/JavascriptInterface']
                def __init__(self, bridge):
                    super().__init__()
                    self._bridge = bridge
                @java_method('(Ljava/lang/String;)V')
                def onUrl(self, url):
                    self._bridge._handle_url(url)
                @java_method('()V')
                def onPageReady(self):
                    Logger.info("WebViewBridge: JS page ready")
                    if self._bridge._callback:
                        self._bridge._callback("page_loaded", None)
            cls._class = _JSI
        return cls._class


class _UIRunnable:
    """Lazy holder for the UI-thread Runnable PythonJavaClass."""
    _class = None

    @classmethod
    def get_class(cls):
        if cls._class is None:
            from jnius import PythonJavaClass, java_method
            class _R(PythonJavaClass):
                __javainterfaces__ = ['java/lang/Runnable']
                def __init__(self, func):
                    super().__init__()
                    self.func = func
                @java_method('()V', name='run')
                def run(self):
                    self.func()
            cls._class = _R
        return cls._class


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
            from android import mActivity
            Runnable = _UIRunnable.get_class()
            mActivity.runOnUiThread(Runnable(self._create_webview))
        except Exception as e:
            Logger.error("WebViewBridge: Setup failed - " + str(e))
            Logger.error(_tb.format_exc())

    def _create_webview(self):
        steps = []
        try:
            from jnius import autoclass
            from android import mActivity

            WebView = autoclass("android.webkit.WebView")
            steps.append("WebView autoclass OK")
            WebSettings = autoclass("android.webkit.WebSettings")
            steps.append("WebSettings autoclass OK")
            WebViewClient = autoclass("android.webkit.WebViewClient")
            steps.append("WebViewClient autoclass OK")
            RelativeLayout = autoclass("android.widget.RelativeLayout")
            ViewGroup = autoclass("android.view.ViewGroup")
            LayoutParams = autoclass("android.view.ViewGroup$LayoutParams")
            steps.append("Layout/View autoclass OK")

            activity = mActivity
            steps.append("Got activity")

            self._webview = WebView(activity)
            steps.append("WebView instance created")
            self._webview.setBackgroundColor(0x00131315)
            steps.append("Background set")

            settings = self._webview.getSettings()
            settings.setJavaScriptEnabled(True)
            settings.setDomStorageEnabled(True)
            settings.setCacheMode(WebSettings.LOAD_DEFAULT)
            settings.setAllowFileAccess(False)
            settings.setGeolocationEnabled(True)
            settings.setMixedContentMode(WebSettings.MIXED_CONTENT_ALWAYS_ALLOW)
            steps.append("Settings configured")

            # Use a plain WebViewClient instance (not subclassed — avoid pyjnius limitation)
            wvc = WebViewClient()
            self._webview.setWebViewClient(wvc)
            steps.append("WebViewClient set")

            # Add JS bridge interface for native communication
            JSI = _JSBridge.get_class()
            js_interface = JSI(self)
            self._webview.addJavascriptInterface(js_interface, "Android")
            steps.append("JS interface added")

            String = autoclass("java.lang.String")
            from .map_html import MAP_HTML
            self._webview.loadDataWithBaseURL(
                None,
                String(MAP_HTML),
                String("text/html"),
                String("UTF-8"),
                None,
            )
            steps.append("HTML loadDataWithBaseURL called")

            params = LayoutParams(
                LayoutParams.MATCH_PARENT,
                LayoutParams.MATCH_PARENT,
            )
            activity.mLayout.addView(self._webview, params)
            steps.append("WebView added to mLayout")
            Logger.info("WebViewBridge: Created and ready")
        except Exception as e:
            Logger.error("WebViewBridge: create error at step[" + str(len(steps)) + "]: " + str(steps[len(steps)-1] if steps else "start"))
            Logger.error("WebViewBridge: exception=" + str(e))
            Logger.error(_tb.format_exc())

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
            from jnius import PythonJavaClass, java_method
            class _EvaluateJSRunnable(PythonJavaClass):
                __javainterfaces__ = ['java/lang/Runnable']
                def __init__(self, wv, code):
                    super().__init__()
                    self.wv = wv
                    self.code = code
                @java_method('()V', name='run')
                def run(self):
                    self.wv.evaluateJavascript(self.code, None)
            mActivity.runOnUiThread(_EvaluateJSRunnable(self._webview, js_code))
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
