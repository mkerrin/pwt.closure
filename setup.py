"""
pwt.closure is a tool to compile and manage JavaScript dependencies of your
web application.
"""
from setuptools import find_packages, setup

setup(
    name = "pwt.closure",
    version = "0.2",

    author = "Michael Kerrin",
    author_email = "michael.kerrin@gmail.com",
    license = "BSD",
    description = __doc__,
    long_description = open("README.txt").read(),
    url = "https://github.com/mkerrin/pwt.closure",

    packages = find_packages("src"),
    package_dir = {"": "src"},
    namespace_packages = ["pwt"],

    install_requires = [
        "setuptools",
        ],

    extras_require = {
        "test": [
            "WebTest",
            "Paste",
            "zc.buildout",
            ],
        # You must install this extra requirement so that I don't have to
        # worry about installing development versions of WebOb and Paste
        # during the installation of recipes in buildout.
        "web": [
            "WebOb",
            "Paste",
            ],
        },

    entry_points = {
        "paste.app_factory": [
            "main = pwt.closure.wsgi:paste_combined_closure",
            ],
        "console_scripts": [
            "closurebuilder = pwt.closure.cli:main",
            ],
        "zc.buildout": [
            "compile = pwt.closure.recipe:CompileRecipe",
            "deps = pwt.closure.recipe:DepsRecipe",
            ],
        },

    include_package_data = True,
    zip_safe = False,
    )
