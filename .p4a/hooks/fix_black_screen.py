import os


def prebuild(arch):
    dist_dir = arch.ctx.dist_dir

    # 1. Create custom theme resource
    values_dir = os.path.join(dist_dir, "src", "main", "res", "values")
    os.makedirs(values_dir, exist_ok=True)
    styles_xml = '''<?xml version="1.0" encoding="utf-8"?>
<resources>
    <style name="AppTheme" parent="@android:style/Theme.NoTitleBar">
        <item name="android:windowBackground">@android:color/transparent</item>
        <item name="android:windowDisablePreview">true</item>
        <item name="android:windowSplashScreenBackground">@android:color/transparent</item>
    </style>
</resources>'''
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

    # 3. Patch PythonActivity.java to keep surface alive during startup
    java_path = os.path.join(
        dist_dir, "src", "main", "java", "org", "kivy", "android", "PythonActivity.java"
    )
    if os.path.exists(java_path):
        with open(java_path, "r") as f:
            source = f.read()
        # Replace onStop to not call super on first stop (keeps surface alive)
        old_onstop = '''    @Override
    protected void onStop() {
        super.onStop();
        Log.v("PythonActivity", "onStop()");
        this.mActivity.mOpened = true;
        SDLActivity.onStop();
    }'''
        new_onstop = '''    @Override
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
    }'''
        if old_onstop in source:
            source = source.replace(old_onstop, new_onstop)
            with open(java_path, "w") as f:
                f.write(source)
            info("fix_black_screen: Patched PythonActivity.onStop()")
        else:
            info("fix_black_screen: WARNING - onStop() pattern not found in PythonActivity.java")
    else:
        info("fix_black_screen: WARNING - PythonActivity.java not found at " + java_path)
