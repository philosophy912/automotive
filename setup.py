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
        "": ["*.dll", "*.ini", "*.xls*", "*.lib"]
    },
    python_requires=">=3.6.*",
    # 安装依赖的包
    install_requires=[
        "loguru>=0.4.3",
        "numpy>=1.19.3",
        "PyYAML>=5.4.1",
        "opencv-python>=4.5.1.48",
        "Appium-Python-Client>=0.40",
        "uiautomator2>=2.10.0",
        "wheel>=0.34.2",
        "pytest>=5.3.5",
        "airtest>=1.1.3",
        "ImageHash>=4.0",
        "chardet>=3.0.4",
        "pyserial>=3.4",
        "allure-pytest>=2.8.12"
    ],
    classifiers=[
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Operating System :: OS Independent",
    ]
)
