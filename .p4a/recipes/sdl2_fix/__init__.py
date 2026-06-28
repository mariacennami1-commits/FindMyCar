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
                if f == 'SDLActivity.java':
                    if self._patch_sdl_activity(path):
                        patched += 1

        if patched == 0:
            info("sdl2_fix: WARNING - no Java files found to patch")
        else:
            info("sdl2_fix: Patched " + str(patched) + " file(s)")

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
