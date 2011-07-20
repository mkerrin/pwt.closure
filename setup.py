from setuptools import find_packages, setup

setup(
    name = "pwt.closure",
    version = "0.1",

    author = "Michael Kerrin",
    author_email = "michael.kerrin@gmail.com",
    license = "BSD",
    description = "",
    long_description = "",
    url = "https://github.com/mkerrin/pwt.jinja2js",

    packages = find_packages("src"),
    package_dir = {"": "src"},
    namespace_packages = ["pwt"],

    install_requires = [
        "setuptools",
        "WebOb",
        "Paste",
        ],

    extras_require = {
        "test": [
            "WebTest",
            ],
        },

    entry_points = {
        "paste.app_factory": [
            "main = pwt.closure.wsgi:paste_combined_closure",
            ],
        "console_scripts": [
            "closurebuilder = pwt.closure.cli:main",
            ],
        },

    include_package_data = True,
    zip_safe = False,
    )
