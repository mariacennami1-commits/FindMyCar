import os

from pythonforandroid.recipe import Recipe
from pythonforandroid.logger import info


class PlyerFixRecipe(Recipe):
    version = '1.0'
    url = None
    depends = ['plyer']
    conflicts = []
    opt_depends = []

    def should_build(self, arch):
        return False

    def postbuild_arch(self, arch):
        super().postbuild_arch(arch)
        self._patch_gps_py(arch)

    def _patch_gps_py(self, arch):
        python_install = arch.ctx.get_python_install_dir(arch.arch)
        gps_path = os.path.join(
            python_install, 'plyer', 'platforms', 'android', 'gps.py'
        )
        info("plyer_fix: Patching " + gps_path)

        if not os.path.exists(gps_path):
            info("plyer_fix: WARNING - gps.py not found at " + gps_path)
            return

        with open(gps_path, 'r') as fh:
            source = fh.read()

        old = "@java_method('(Landroid/location/Location;)V')\n    def onLocationChanged(self, location):"
        new = (
            "@java_method('(Ljava/util/List;)V')\n"
            "    def onLocationChanged(self, locations):\n"
            "        if locations.size() > 0:\n"
            "            location = locations.get(locations.size() - 1)\n"
            "            self.root.on_location(\n"
            "                lat=location.getLatitude(),\n"
            "                lon=location.getLongitude(),\n"
            "                speed=location.getSpeed(),\n"
            "                bearing=location.getBearing(),\n"
            "                altitude=location.getAltitude(),\n"
            "                accuracy=location.getAccuracy())\n"
            "\n"
            "    @java_method('(Landroid/location/Location;)V')\n"
            "    def onLocationChanged(self, location):"
        )

        if old not in source:
            info("plyer_fix: gps.py already patched or unexpected format, skipping")
            return

        source = source.replace(old, new)

        with open(gps_path, 'w') as fh:
            fh.write(source)

        info("plyer_fix: Patched gps.py successfully")


recipe = PlyerFixRecipe()
