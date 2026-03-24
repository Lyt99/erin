from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as f:
    long_description = f.read()

setup(
    name="erin",
    version="0.1.0",
    author="Lyt99",
    description="An OpenAI-based Python function auto-generation tool",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/Lyt99/erin",
    packages=find_packages(exclude=[".venv", "tests"]),
    python_requires=">=3.8",
    install_requires=[
        "openai>=2.15.0",
    ],
    license="WTFPL",
    classifiers=[
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Programming Language :: Python :: 3.13",
        "License :: OSI Approved :: The Unlicense (Unlicense)",
        "Operating System :: OS Independent",
    ],
)
