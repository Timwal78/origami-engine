from setuptools import setup, find_packages
setup(
    name="origami-engine",
    version="1.0.0",
    packages=find_packages(),
    entry_points={"console_scripts": ["origami=origami.cli:main"]},
    install_requires=["anthropic>=0.27.0"],
)
