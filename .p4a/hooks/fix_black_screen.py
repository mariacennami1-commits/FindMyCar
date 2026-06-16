import os
import re


def _find_and_patch_p4a_templates():
    from pythonforandroid.logger import info
    try:
        import pythonforandroid
    except Exception:
        info("fix_black_screen: could not import pythonforandroid")
        return

    p4a_root = os.path.dirname(pythonforandroid.__file__)
    info("fix_black_screen: p4a root = " + str(p4a_root))

    patched_count = 0
    for root, dirs, files in os.walk(p4a_root):
        for f in files:
            if f == "PythonActivity.java":
                path = os.path.join(root, f)
                if _patch_python_activity(path):
                    patched_count += 1
                    info("fix_black_screen: Patched PythonActivity.java template at " + path)
            elif f == "SDLActivity.java":
                path = os.path.join(root, f)
                if _patch_sdl_activity(path):
                    patched_count += 1
                    info("fix_black_screen: Patched SDLActivity.java template at " + path)

    if patched_count == 0:
        info("fix_black_screen: WARNING - no Java template files found to patch in p4a tree")
        all_javas = []
        for root, dirs, files in os.walk(p4a_root):
            for f in files:
                if f.endswith(".java"):
                    all_javas.append(os.path.join(root, f))
        info("fix_black_screen: All .java files found: " + str(all_javas))


def _patch_python_activity(path):
    with open(path, "r") as f:
        source = f.read()

    if "fix_black_screen onStart" in source:
        return False

    # Remove existing onStop()
    onstop_re = re.compile(
        r'@Override\s*\n\s*protected\s+void\s+onStop\s*\(\s*\)\s*\{.*?\n\s*\}',
        re.DOTALL
    )
    source, onstop_count = onstop_re.subn("", source)

    # Remove existing onStart()
    onstart_re = re.compile(
        r'@Override\s*\n\s*protected\s+void\s+onStart\s*\(\s*\)\s*\{.*?\n\s*\}',
        re.DOTALL
    )
    source, onstart_count = onstart_re.subn("", source)

    # Find class closing brace
    class_end = source.rfind("\n}")
    if class_end == -1:
        class_end = source.rfind("}")
        if class_end > 0:
            class_end = source.rfind("\n", 0, class_end)
            if class_end == -1:
                class_end = source.rfind("}")

    if class_end <= 0:
        return False

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
    source = source[:class_end] + overrides + "\n}"

    with open(path, "w") as f:
        f.write(source)
    return True


def _patch_sdl_activity(path):
    with open(path, "r") as f:
        source = f.read()

    handle_re = re.compile(
        r'(void\s+handleNativeState\s*\(\s*\)\s*\{)',
        re.DOTALL
    )
    if not handle_re.search(source):
        return False

    if "mSurface == null" in source:
        return False

    source = handle_re.sub(
        r'\1\n'
        r'        try {\n'
        r'            if (mSurface == null) { Log.v("SDL", "handleNativeState() - mSurface is null, returning"); return; }\n'
        r'        } catch (Exception e) { Log.v("SDL", "handleNativeState() - null check exception: " + e.getMessage()); return; }',
        source
    )

    with open(path, "w") as f:
        f.write(source)
    return True


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

    # 3. Patch p4a Java SOURCE TEMPLATES before SDL2 recipe copies them
    info("fix_black_screen: Searching for p4a Java template files to patch...")
    _find_and_patch_p4a_templates()
