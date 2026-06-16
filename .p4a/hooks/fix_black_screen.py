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

    # 3. Find PythonActivity.java - search recursively
    java_path = None
    for root, dirs, files in os.walk(dist_dir):
        if "PythonActivity.java" in files:
            java_path = os.path.join(root, "PythonActivity.java")
            break

    if not java_path:
        info("fix_black_screen: WARNING - PythonActivity.java not found anywhere under " + dist_dir)

        # Also try the buildozer cache path
        alt_base = os.path.expanduser("~/.buildozer/android/platform")
        if os.path.exists(alt_base):
            for root, dirs, files in os.walk(alt_base):
                if "PythonActivity.java" in files and "dists" in root:
                    java_path = os.path.join(root, "PythonActivity.java")
                    break
        if java_path:
            info("fix_black_screen: Found PythonActivity.java at " + java_path)
        else:
            info("fix_black_screen: WARNING - PythonActivity.java not found in buildozer cache either")
            return

    info("fix_black_screen: Found PythonActivity.java at " + java_path)

    with open(java_path, "r") as f:
        source = f.read()

    # 4. Add onStart() override if not already present (via our hook)
    if "fix_black_screen onStart" in source:
        info("fix_black_screen: onStart override already applied, skipping")
        return

    # Strategy: remove any existing onStop() method (by regex), then
    # insert both onStart() and onStop() overrides at end of class.
    # This avoids duplicate method errors.

    import re

    # Remove existing onStop() method if present (any body content)
    onstop_re = re.compile(
        r'@Override\s*\n\s*protected\s+void\s+onStop\s*\(\s*\)\s*\{.*?\n\s*\}',
        re.DOTALL
    )
    new_source, onstop_count = onstop_re.subn("", source)
    if onstop_count > 0:
        info("fix_black_screen: Removed existing onStop() method (count=" + str(onstop_count) + ")")
    else:
        info("fix_black_screen: No existing onStop() method found to remove")

    # Remove existing onStart() method if present
    onstart_re = re.compile(
        r'@Override\s*\n\s*protected\s+void\s+onStart\s*\(\s*\)\s*\{.*?\n\s*\}',
        re.DOTALL
    )
    new_source, onstart_count = onstart_re.subn("", new_source)
    if onstart_count > 0:
        info("fix_black_screen: Removed existing onStart() method (count=" + str(onstart_count) + ")")

    # Find class closing brace
    class_end = new_source.rfind("\n}")
    if class_end == -1:
        class_end = new_source.rfind("}")
        if class_end > 0:
            class_end = new_source.rfind("\n", 0, class_end)
            if class_end == -1:
                class_end = new_source.rfind("}")

    if class_end > 0:
        overrides = """

    // --- BEGIN fix_black_screen onStart ---
    @Override
    protected void onStart() {
        Log.v("PythonActivity", "fix_black_screen onStart()");
        if (this.mActivity != null && this.mActivity.mLoadFinished) {
            super.onStart();
            Log.v("PythonActivity", "fix_black_screen onStart() - super called (post load)");
        } else {
            Log.v("PythonActivity", "fix_black_screen onStart() - DEFERRED (pre load)");
        }
    }
    // --- END fix_black_screen onStart ---

    // --- BEGIN fix_black_screen onStop ---
    @Override
    protected void onStop() {
        Log.v("PythonActivity", "fix_black_screen onStop()");
        this.mActivity.mOpened = true;
        if (this.mActivity != null && this.mActivity.mLoadFinished) {
            super.onStop();
            Log.v("PythonActivity", "fix_black_screen onStop() - super called (post load)");
        } else {
            Log.v("PythonActivity", "fix_black_screen onStop() - DEFERRED (pre load)");
        }
    }
    // --- END fix_black_screen onStop ---
"""
        new_source = new_source[:class_end] + overrides + "\n}"
        info("fix_black_screen: Inserted onStart() and onStop() overrides at end of class")
    else:
        info("fix_black_screen: WARNING - could not find class closing brace")
        return

    with open(java_path, "w") as f:
        f.write(new_source)
    info("fix_black_screen: PythonActivity.java patched successfully")

    # 5. Also try to find SDLActivity.java and patch handleNativeState
    sdl_path = None
    for root, dirs, files in os.walk(dist_dir):
        if "SDLActivity.java" in files:
            sdl_path = os.path.join(root, "SDLActivity.java")
            break

    if sdl_path:
        info("fix_black_screen: Found SDLActivity.java at " + sdl_path)
        with open(sdl_path, "r") as f:
            sdl_source = f.read()

        # Patch handleNativeState to null-check mSurface
        handle_re = re.compile(
            r'(void\s+handleNativeState\s*\(\s*\)\s*\{)',
            re.DOTALL
        )
        if handle_re.search(sdl_source):
            sdl_source = handle_re.sub(
                r'\1\n'
                r'        try {\n'
                r'            if (mSurface == null) { Log.v("SDL", "handleNativeState() - mSurface is null, returning"); return; }\n'
                r'        } catch (Exception e) { Log.v("SDL", "handleNativeState() - null check exception: " + e.getMessage()); return; }',
                sdl_source
            )
            with open(sdl_path, "w") as f:
                f.write(sdl_source)
            info("fix_black_screen: Added null check in SDLActivity.handleNativeState()")
        else:
            info("fix_black_screen: WARNING - handleNativeState() not found in SDLActivity.java")
    else:
        info("fix_black_screen: SDLActivity.java not found (optional - not critical)")
