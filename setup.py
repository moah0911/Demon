#!/usr/bin/env python3
"""
Setup script for the Demon programming language.
"""

from setuptools import setup, find_packages

setup(
    name="demon-lang",
    version="1.0.0",
    description="Demon Programming Language",
    author="Demon Team",
    packages=find_packages(),
    entry_points={
        "console_scripts": [
            "demon=src.tools.cli:main",
        ],
    },
    python_requires=">=3.7",
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
    ],
)