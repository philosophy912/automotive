# -*- coding:utf-8 -*-
# --------------------------------------------------------
# Copyright (C), 2016-2020, China TSP, All rights reserved
# --------------------------------------------------------
# @Name:        setup.py
# @Purpose:     安装配置文件
# @Author:      lizhe
# @Created:     2020/02/09 11:24
# --------------------------------------------------------
import re
import setuptools
from os.path import abspath, dirname, join

current_folder = dirname(abspath(__file__))
with open(join(current_folder, "src", "automotive", "version.py"), "rt", encoding="utf-8") as f:
    VERSION = re.search("\nVERSION = '(.*)'", f.read()).group(1)
with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setuptools.setup(
    name="automotive",
    version=VERSION,
    description="A simple framework for automotive system",
    long_description=long_description,
    long_description_content_type="text/markdown",
    author="lizhe",
    author_email="lizhe@bdstar.com",
    packages=setuptools.find_packages("src"),
    package_dir={"": "src"},
    # 依赖的相关文件
    package_data={
        "": ["*.dll", "*.ini"]
    },
    python_requires=">=3.6.*",
    # 安装依赖的包
    install_requires=[
        "pinyin>=0.4.0",
        "loguru>=0.4.3",
        "sounddevice>=0.3.14",
        "numpy>=1.18.1",
        "opencv-python>=4.1.0.25",
        "pandas>=1.0.0",
        "pyserial>=3.4",
        "pygame>=1.9.5",
        "Appium-Python-Client>=0.40",
        "chardet>=3.0.4",
        "pyttsx3>=2.7",
        "ImageHash>=4.0",
        "paramiko>=2.7.1",
        "PyYAML>=5.1.2",
        "pypiwin32>=223",
        "wheel>=0.34.2",
        "airtest>=1.1.3",
        "pytest>=5.3.5",
        "allure-pytest>=2.8.12",
        "uiautomator2>=2.10.0",
        "weditor>-0.5.0"
    ],
    classifiers=[
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.7",
        "Operating System :: OS Independent",
    ]
)
