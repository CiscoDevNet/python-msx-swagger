#
# Copyright (c) 2021 Cisco Systems, Inc and its affiliates
# All rights reserved
#
import os.path
from setuptools import setup, find_packages


def current_path(file_name):
    return os.abspath(os.path.join(__file__, os.path.pardir, file_name))


# with open("README.md", "r", encoding="utf-8") as fh:
#     long_description = fh.read()

setup(
    name='msxswagger',
    version='0.7.0',
    author="Cisco MSX",
    author_email="ananasta@cisco.com",
    description='A package that enables swagger ui in your python web application',
    include_package_data=True,
    package_dir={"": "src"},
    packages=find_packages(),
    python_requires=">=3.6",
    install_requires=[
        "Flask~=2.0.3",
        "Flask-Cors~=3.0.10",
        "flask-restx~=0.5.1",
        "Werkzeug~=2.0.3",
    ],
)
