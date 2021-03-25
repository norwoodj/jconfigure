#!/usr/bin/env python
from distutils.core import setup

setup(
    name="jconfigure",
    packages=["jconfigure"],
    version="_VERSION",
    description="A python configuration management library",
    author="John Norwood",
    author_email="norwood.john.m@gmail.com",
    url="https://github.com/norwoodj/jconfigure",
    download_url="https://github.com/norwoodj/jconfigure/archive/19.0123-dev.tar.gz",
    keywords=["configuration"],
    classifiers=[],
    install_requires=[
        "PyYAML==5.4",
    ]
)
