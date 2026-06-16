import os


def prebuild(arch):
    dist_dir = arch.ctx.dist_dir
    from pythonforandroid.logger import info

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

    # 3. Patch PythonActivity.java only (overrides SDLActivity lifecycle methods)
    java_path = os.path.join(
        dist_dir, "src", "main", "java", "org", "kivy", "android", "PythonActivity.java"
    )
    if not os.path.exists(java_path):
        info("fix_black_screen: WARNING - PythonActivity.java not found at " + java_path)
        return

    with open(java_path, "r") as f:
        source = f.read()

    # 3a. Patch onStop() - defer super.onStop until mLoadFinished
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
        info("fix_black_screen: Patched PythonActivity.onStop()")
    else:
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
            info("fix_black_screen: Patched PythonActivity.onStop() (alt)")
        else:
            info("fix_black_screen: WARNING - onStop() pattern not matched, appending override")

    # 3b. Override onStart() in PythonActivity - defer super.onStart (which calls handleNativeState)
    onstart_override = """

    @Override
    protected void onStart() {
        Log.v("PythonActivity", "onStart()");
        if (this.mActivity.mLoadFinished) {
            super.onStart();
            Log.v("PythonActivity", "onStart() - super called (post load)");
        } else {
            Log.v("PythonActivity", "onStart() - DEFERRED (pre load, keeping surface alive)");
        }
    }"""
    # Insert before the closing brace of the class
    if "onStart_OVERRIDE_INSERTED" not in source:
        if old_onstop in source:
            # Already replaced with new_onstop, insert after it
            source = source.replace(new_onstop, new_onstop + onstart_override)
            info("fix_black_screen: Inserted onStart() override (after onStop)")
        else:
            # Find the last } and insert before it
            class_end = source.rfind("\n}")
            if class_end != -1:
                source = source[:class_end] + onstart_override + "\n}"
                info("fix_black_screen: Inserted onStart() override (before class end)")
            else:
                info("fix_black_screen: WARNING - could not find class end for onStart override")

    # 3c. Override surfaceDestroyed() in PythonActivity - keep surface alive during init
    sd_override = """

    @Override
    public void surfaceDestroyed(SurfaceHolder holder) {
        Log.v("PythonActivity", "surfaceDestroyed()");
        if (this.mActivity.mLoadFinished) {
            super.surfaceDestroyed(holder);
            Log.v("PythonActivity", "surfaceDestroyed() - super called (post load)");
        } else {
            Log.v("PythonActivity", "surfaceDestroyed() - DEFERRED (pre load, keeping surface alive)");
        }
    }"""
    if "surfaceDestroyed_OVERRIDE_INSERTED" not in source:
        class_end = source.rfind("\n}")
        if class_end != -1:
            source = source[:class_end] + sd_override + "\n}"
            info("fix_black_screen: Inserted surfaceDestroyed() override (before class end)")
        else:
            info("fix_black_screen: WARNING - could not find class end for surfaceDestroyed override")

    with open(java_path, "w") as f:
        f.write(source)
    info("fix_black_screen: PythonActivity.java patched successfully")
