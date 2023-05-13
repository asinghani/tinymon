from setuptools import setup

setup(
    name = "tinymon",
    version = "1.0.0",
    packages = ["tinymon"],
    entry_points = {
        "console_scripts": [
            "tinymon = tinymon.tinymon:main"
        ]
    },
    install_requires=[
        "pyyaml",
        "pwntools",
        "termcolor",
        "tqdm"
    ]
)
