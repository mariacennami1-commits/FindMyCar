from pythonforandroid.recipe import PyProjectRecipe


class PillowRecipe(PyProjectRecipe):
    version = '12.2.0'
    url = 'https://github.com/python-pillow/Pillow/archive/{version}.tar.gz'
    site_packages_name = 'PIL'
    depends = ['png', 'jpeg', 'freetype']
    hostpython_prerequisites = ["setuptools>=77"]
    opt_depends = ['libwebp']


recipe = PillowRecipe()
