import os
import re

from pythonforandroid.recipe import Recipe
from pythonforandroid.logger import info


class SDL2FixRecipe(Recipe):
    version = '1.0'
    url = None
    depends = ['sdl2']
    conflicts = []
    opt_depends = []

    def should_build(self, arch):
        return False

    def prebuild_arch(self, arch):
        super().prebuild_arch(arch)
        self._patch_java_files(arch)

    def _patch_java_files(self, arch):
        dist_dir = arch.ctx.dist_dir
        java_root = os.path.join(dist_dir, 'src', 'main', 'java')
        info("sdl2_fix: Patching Java files under " + java_root)

        patched = 0
        for root, dirs, files in os.walk(java_root):
            for f in files:
                path = os.path.join(root, f)
                if f == 'PythonActivity.java':
                    if self._patch_python_activity(path):
                        patched += 1
                elif f == 'SDLActivity.java':
                    if self._patch_sdl_activity(path):
                        patched += 1

        if patched == 0:
            info("sdl2_fix: WARNING - no Java files found to patch")
            all_java = []
            for root, dirs, files in os.walk(java_root):
                for f in files:
                    if f.endswith('.java'):
                        all_java.append(os.path.join(root, f))
            info("sdl2_fix: All .java files: " + str(all_java))
        else:
            info("sdl2_fix: Patched " + str(patched) + " file(s)")

    def _patch_python_activity(self, path):
        with open(path, 'r') as fh:
            source = fh.read()

        if 'fix_black_screen' in source:
            info("sdl2_fix: PythonActivity.java already patched, skipping")
            return False

        onstop_re = re.compile(
            r'@Override\s*\n\s*protected\s+void\s+onStop\s*\(\s*\)\s*\{.*?\n\s*\}',
            re.DOTALL
        )
        source, stop_count = onstop_re.subn('', source)

        onstart_re = re.compile(
            r'@Override\s*\n\s*protected\s+void\s+onStart\s*\(\s*\)\s*\{.*?\n\s*\}',
            re.DOTALL
        )
        source, start_count = onstart_re.subn('', source)

        class_end = source.rfind('\n}')
        if class_end == -1:
            class_end = source.rfind('}')
            if class_end > 0:
                class_end = source.rfind('\n', 0, class_end)
                if class_end == -1:
                    class_end = source.rfind('}')

        if class_end <= 0:
            info("sdl2_fix: Cannot find class closing brace in PythonActivity.java")
            return False

        overrides = """

    // --- BEGIN fix_black_screen ---
    @Override
    protected void onStart() {
        android.util.Log.v("PythonActivity", "fix_black_screen onStart()");
        if (this.mActivity != null && this.mActivity.mLoadFinished) {
            super.onStart();
        } else {
            android.util.Log.v("PythonActivity", "fix_black_screen onStart() - DEFERRED (pre load)");
        }
    }

    @Override
    protected void onStop() {
        android.util.Log.v("PythonActivity", "fix_black_screen onStop()");
        this.mActivity.mOpened = true;
        if (this.mActivity != null && this.mActivity.mLoadFinished) {
            super.onStop();
        } else {
            android.util.Log.v("PythonActivity", "fix_black_screen onStop() - DEFERRED (pre load)");
        }
    }
    // --- END fix_black_screen ---
"""
        source = source[:class_end] + overrides + '\n}'

        with open(path, 'w') as fh:
            fh.write(source)

        info("sdl2_fix: Patched PythonActivity.java at " + path)
        return True

    def _patch_sdl_activity(self, path):
        with open(path, 'r') as fh:
            source = fh.read()

        handle_re = re.compile(
            r'(void\s+handleNativeState\s*\(\s*\)\s*\{)',
            re.DOTALL
        )
        if not handle_re.search(source):
            info("sdl2_fix: handleNativeState not found in SDLActivity.java")
            return False

        if 'mSurface == null' in source:
            info("sdl2_fix: SDLActivity.java already patched, skipping")
            return False

        source = handle_re.sub(
            r'\1\n'
            r'        try {\n'
            r'            if (mSurface == null) { android.util.Log.v("SDL", "handleNativeState() - mSurface null, returning"); return; }\n'
            r'        } catch (Exception e) { android.util.Log.v("SDL", "handleNativeState() - null check exception: " + e.getMessage()); return; }',
            source
        )

        with open(path, 'w') as fh:
            fh.write(source)

        info("sdl2_fix: Patched SDLActivity.java at " + path)
        return True


recipe = SDL2FixRecipe()
