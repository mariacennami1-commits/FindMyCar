from os.path import join

from pythonforandroid.recipe import PyProjectRecipe


class PillowRecipe(PyProjectRecipe):
    version = '12.2.0'
    url = 'https://github.com/python-pillow/Pillow/archive/{version}.tar.gz'
    site_packages_name = 'PIL'
    patches = ["setup.py.patch"]
    depends = ['png', 'jpeg', 'freetype']
    hostpython_prerequisites = ["setuptools>=77"]
    opt_depends = ['libwebp']

    def get_recipe_env(self, arch, **kwargs):
        env = super().get_recipe_env(arch, **kwargs)

        env["LDFLAGS"] = env.get("LDFLAGS", "") + " -lm"

        jpeg = self.get_recipe('jpeg', self.ctx)
        jpeg_inc_dir = jpeg_lib_dir = jpeg.get_build_dir(arch.arch)
        env["JPEG_ROOT"] = "{}:{}".format(jpeg_lib_dir, jpeg_inc_dir)

        freetype = self.get_recipe('freetype', self.ctx)
        free_lib_dir = join(freetype.get_build_dir(arch.arch), 'objs', '.libs')
        free_inc_dir = join(freetype.get_build_dir(arch.arch), 'include')
        env["FREETYPE_ROOT"] = "{}:{}".format(free_lib_dir, free_inc_dir)

        harfbuzz = self.get_recipe('harfbuzz', self.ctx)
        harf_lib_dir = join(harfbuzz.get_build_dir(arch.arch), 'src', '.libs')
        harf_inc_dir = harfbuzz.get_build_dir(arch.arch)
        env["HARFBUZZ_ROOT"] = "{}:{}".format(harf_lib_dir, harf_inc_dir)

        env["ZLIB_ROOT"] = f"{arch.ndk_lib_dir_versioned}:{self.ctx.ndk.sysroot_include_dir}"

        if 'libwebp' in self.ctx.recipe_build_order:
            webp = self.get_recipe('libwebp', self.ctx)
            webp_install = join(
                webp.get_build_dir(arch.arch), 'installation'
            )
            env["WEBP_ROOT"] = f"{join(webp_install, 'lib')}:{join(webp_install, 'include')}"
        return env


recipe = PillowRecipe()
