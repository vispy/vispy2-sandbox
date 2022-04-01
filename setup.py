from setuptools import find_packages, setup

setup(
    name="visp",
    version="0.0.1",
    packages=find_packages(
        exclude=["tests", "tests.*", "examples", "examples.*", "exp", "exp.*"]
    ),
    python_requires=">=3.7.0",
    install_requires= ["toml", "pyyaml"],
    license="BSD 2-Clause",
    zip_safe=True,
)
