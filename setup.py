"""
Script de configuração para o Self-Evolving Bot
"""
import sys
from setuptools import setup, find_packages
import os
from pathlib import Path

# Lê os requisitos
with open('requirements.txt') as f:
    requirements = f.read().splitlines()

setup(
    name="Self-Evolving-Bot",
    version="1.0.0",
    author="Bot Developer",
    description="Um bot inteligente que aprende e evolui",
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    packages=find_packages(),
    install_requires=requirements,
    python_requires=">=3.8",
    entry_points={
        "console_scripts": [
            "self-evolving-bot=gui_interface:main",
        ],
    },
    classifiers=[
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    include_package_data=True,
) 