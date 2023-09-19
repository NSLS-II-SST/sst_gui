from setuptools import setup, find_packages

setup(
    author="ctitus@bnl.gov",
    python_requires=">=3.7",
    description="SST1 GUI",
    install_requires=["bluesky_widgets", "qtpy"],
    packages=find_packages(),
    name="sst_gui",
    use_scm_version=True,
    entry_points={
        "console_scripts": [
            "sst-gui = sst_gui.main:main"],
        },
    )
