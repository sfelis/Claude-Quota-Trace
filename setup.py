#!/usr/bin/env python3
"""Setup script for floating-ball package.

Supports older pip versions that can't read pyproject.toml metadata.
"""
from setuptools import setup, find_packages

setup(
    name="floating-ball",
    version="1.0.0",
    description="A macOS floating desktop widget that displays Claude API subscription usage in real-time",
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    author="Floating Ball Contributors",
    license="MIT",
    python_requires=">=3.9",
    packages=find_packages(include=["floating_ball", "floating_ball.*"]),
    install_requires=[
        "PyQt6>=6.6.0",
        "curl_cffi>=0.6.0",
        "playwright>=1.40.0",
        "requests>=2.31.0",
    ],
    entry_points={
        "console_scripts": [
            "floating-ball=floating_ball.main:main",
        ],
    },
    classifiers=[
        "Development Status :: 4 - Beta",
        "Environment :: MacOS X",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Operating System :: MacOS",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Topic :: Utilities",
    ],
)
