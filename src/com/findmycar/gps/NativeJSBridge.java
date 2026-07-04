package com.findmycar.gps;

import android.webkit.JavascriptInterface;

public class NativeJSBridge {
    private static volatile String sPendingUrl;
    private static volatile boolean sHasPendingUrl;

    @JavascriptInterface
    public void onUrl(String url) {
        if (url == null) return;
        sPendingUrl = url;
        sHasPendingUrl = true;
    }

    @JavascriptInterface
    public void onPageReady() {
        onUrl("app://page_loaded");
    }

    public static boolean hasPendingUrl() {
        return sHasPendingUrl;
    }

    public static String getPendingUrl() {
        sHasPendingUrl = false;
        String url = sPendingUrl;
        sPendingUrl = null;
        return url;
    }
}
