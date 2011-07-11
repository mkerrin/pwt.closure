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

    include_package_data = True,
    zip_safe = False,
    )
