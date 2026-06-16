import os


def prebuild(arch):
    dist_dir = arch.ctx.dist_dir

    # 1. Create custom theme resource
    values_dir = os.path.join(dist_dir, "src", "main", "res", "values")
    os.makedirs(values_dir, exist_ok=True)
    styles_xml = """<?xml version="1.0" encoding="utf-8"?>
<resources>
    <style name="AppTheme" parent="@android:style/Theme.NoTitleBar">
        <item name="android:windowBackground">@android:color/transparent</item>
        <item name="android:windowDisablePreview">true</item>
        <item name="android:windowSplashScreenBackground">@android:color/transparent</item>
    </style>
</resources>"""
    with open(os.path.join(values_dir, "styles.xml"), "w") as f:
        f.write(styles_xml.strip())
    from pythonforandroid.logger import info
    info("fix_black_screen: Created custom theme AppTheme")

    # 2. Patch AndroidManifest.xml to use custom theme
    manifest_path = os.path.join(dist_dir, "src", "main", "AndroidManifest.xml")
    if os.path.exists(manifest_path):
        with open(manifest_path, "r") as f:
            content = f.read()
        content = content.replace(
            'android:theme="@android:style/Theme.NoTitleBar.Fullscreen"',
            'android:theme="@style/AppTheme"'
        ).replace(
            'android:theme="@android:style/Theme.NoTitleBar"',
            'android:theme="@style/AppTheme"'
        )
        with open(manifest_path, "w") as f:
            f.write(content)
        info("fix_black_screen: Patched AndroidManifest theme -> AppTheme")

    # 3. Patch SDLActivity.java: defer surfaceDestroyed + handleNativeState NPE guard
    sdl_path = os.path.join(
        dist_dir, "src", "main", "java", "org", "libsdl", "app", "SDLActivity.java"
    )
    if os.path.exists(sdl_path):
        with open(sdl_path, "r") as f:
            source = f.read()

        # Patch surfaceDestroyed to not null mSurface during Python init
        old_sd = """    public void surfaceDestroyed(SurfaceHolder holder) {
        Log.v("SDL", "surfaceDestroyed()");
        if (mSurface != null) {
            SDLAudioManager.releaseAudioDevice();
            nativePause();
            mSurface = null;
        }
    }"""
        new_sd = """    public void surfaceDestroyed(SurfaceHolder holder) {
        Log.v("SDL", "surfaceDestroyed()");
        PythonActivity act = PythonActivity.mActivity;
        if (act != null && !act.mLoadFinished) {
            Log.v("SDL", "surfaceDestroyed() - DEFERRED (keeping surface alive for Python init)");
            return;
        }
        if (mSurface != null) {
            SDLAudioManager.releaseAudioDevice();
            nativePause();
            mSurface = null;
        }
    }"""
        if old_sd in source:
            source = source.replace(old_sd, new_sd)
            info("fix_black_screen: Patched SDLActivity.surfaceDestroyed()")
        else:
            info("fix_black_screen: WARNING - surfaceDestroyed() pattern not found in SDLActivity.java, trying alt")

            # Try alternative pattern (no null check on mSurface)
            alt_sd = """    public void surfaceDestroyed(SurfaceHolder holder) {
        Log.v("SDL", "surfaceDestroyed()");
        SDLAudioManager.releaseAudioDevice();
        nativePause();
        mSurface = null;
    }"""
            alt_new = """    public void surfaceDestroyed(SurfaceHolder holder) {
        Log.v("SDL", "surfaceDestroyed()");
        PythonActivity act = PythonActivity.mActivity;
        if (act != null && !act.mLoadFinished) {
            Log.v("SDL", "surfaceDestroyed() - DEFERRED (keeping surface alive for Python init)");
            return;
        }
        SDLAudioManager.releaseAudioDevice();
        nativePause();
        mSurface = null;
    }"""
            if alt_sd in source:
                source = source.replace(alt_sd, alt_new)
                info("fix_black_screen: Patched SDLActivity.surfaceDestroyed() (alt)")
            else:
                # Try another variant (p4a 1.6.0 SDL may have different indentation/style)
                alt_sd2 = """    @Override
    public void surfaceDestroyed(SurfaceHolder holder) {
        Log.v("SDL", "surfaceDestroyed()");
        SDLAudioManager.releaseAudioDevice();
        nativePause();
        mSurface = null;
    }"""
                alt_new2 = """    @Override
    public void surfaceDestroyed(SurfaceHolder holder) {
        Log.v("SDL", "surfaceDestroyed()");
        PythonActivity act = PythonActivity.mActivity;
        if (act != null && !act.mLoadFinished) {
            Log.v("SDL", "surfaceDestroyed() - DEFERRED (keeping surface alive for Python init)");
            return;
        }
        SDLAudioManager.releaseAudioDevice();
        nativePause();
        mSurface = null;
    }"""
                if alt_sd2 in source:
                    source = source.replace(alt_sd2, alt_new2)
                    info("fix_black_screen: Patched SDLActivity.surfaceDestroyed() (alt2)")
                else:
                    info("fix_black_screen: WARNING - no surfaceDestroyed() pattern matched")
                    info("fix_black_screen: SDLActivity.java content around surface:\n" + source[
                         source.find("surfaceDestroyed")-200:source.find("surfaceDestroyed")+500
                    ] if "surfaceDestroyed" in source else "NOT FOUND")

        # Also patch handleNativeState to null-guard mSurface (prevent NPE if refocus triggers it)
        old_hns = """    public void handleNativeState() {
        if (mSurface.mIsSurfaceReady) {"""
        new_hns = """    public void handleNativeState() {
        if (mSurface == null) {
            Log.v("SDL", "handleNativeState() - mSurface is null, skipping");
            return;
        }
        if (mSurface.mIsSurfaceReady) {"""
        if old_hns in source and new_hns not in source:
            source = source.replace(old_hns, new_hns)
            info("fix_black_screen: Patched SDLActivity.handleNativeState() NPE guard")

        with open(sdl_path, "w") as f:
            f.write(source)
    else:
        info("fix_black_screen: WARNING - SDLActivity.java not found at " + sdl_path)

    # 4. Patch PythonActivity.java to defer onStop super call during init
    java_path = os.path.join(
        dist_dir, "src", "main", "java", "org", "kivy", "android", "PythonActivity.java"
    )
    if os.path.exists(java_path):
        with open(java_path, "r") as f:
            source = f.read()

        old_onstop = """    @Override
    protected void onStop() {
        super.onStop();
        Log.v("PythonActivity", "onStop()");
        this.mActivity.mOpened = true;
        SDLActivity.onStop();
    }"""
        new_onstop = """    @Override
    protected void onStop() {
        Log.v("PythonActivity", "onStop()");
        this.mActivity.mOpened = true;
        if (this.mActivity.mLoadFinished) {
            super.onStop();
            SDLActivity.onStop();
            Log.v("PythonActivity", "onStop() - super called (post load)");
        } else {
            Log.v("PythonActivity", "onStop() - DEFERRED (pre load, keeping surface alive)");
        }
    }"""
        if old_onstop in source:
            source = source.replace(old_onstop, new_onstop)
            with open(java_path, "w") as f:
                f.write(source)
            info("fix_black_screen: Patched PythonActivity.onStop()")
        else:
            info("fix_black_screen: WARNING - onStop() pattern not found in PythonActivity.java")
            alt_onstop = """    @Override
    protected void onStop() {
        Log.v("PythonActivity", "onStop()");
        this.mActivity.mOpened = true;
    }"""
            alt_newstop = """    @Override
    protected void onStop() {
        Log.v("PythonActivity", "onStop()");
        this.mActivity.mOpened = true;
        if (this.mActivity.mLoadFinished) {
            super.onStop();
            Log.v("PythonActivity", "onStop() - super called (post load)");
        } else {
            Log.v("PythonActivity", "onStop() - DEFERRED (pre load, keeping surface alive)");
        }
    }"""
            if alt_onstop in source:
                source = source.replace(alt_onstop, alt_newstop)
                with open(java_path, "w") as f:
                    f.write(source)
                info("fix_black_screen: Patched PythonActivity.onStop() (alt)")
            else:
                info("fix_black_screen: WARNING - no onStop() pattern matched in PythonActivity.java")
                info("fix_black_screen: PythonActivity.java onStop:\n" + source[
                     source.find("onStop")-200:source.find("onStop")+400
                ] if "protected void onStop" in source else "onStop NOT FOUND")
    else:
        info("fix_black_screen: WARNING - PythonActivity.java not found at " + java_path)
