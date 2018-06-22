#!/usr/bin/env python
from distutils.core import setup

setup(
    name="jconfigure",
    packages=["jconfigure"],
    version="18.0622",
    description="A python configuration management library",
    author="John Norwood",
    author_email="norwood.john.m@gmail.com",
    url="https://github.com/norwoodj/jconfigure",
    download_url="https://github.com/norwoodj/jconfigure/archive/18.0622.tar.gz",
    keywords=["configuration"],
    classifiers=[],
    install_requires=[
        "PyYAML==3.12",
    ]
)
