"""Setup for image-ray package (editable install for development)."""

from setuptools import find_packages, setup

setup(
    name="image-ray",
    version="0.1.0",
    packages=find_packages(where="src"),
    package_dir={"": "src"},
    python_requires=">=3.9",
    install_requires=[
        "ray>=2.9.0",
        "Pillow>=10.0.0",
    ],
)
