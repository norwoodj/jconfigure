#!/usr/bin/env python
from distutils.core import setup

setup(
    name="jconfigure",
    packages=["jconfigure"],
    version="17.0917",
    description="A python configuration management library",
    author="John Norwood",
    author_email="norwood.john.m@gmail.com",
    url="https://github.com/norwoodj/jconfigure",
    download_url="https://github.com/norwoodj/jconfigure/archive/17.0917.tar.gz",
    keywords=["configuration"],
    classifiers=[],
    install_requires=[
        "PyYAML==3.12",
    ]
)
