from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="docu",
    version="0.1.0",
    author="Himanshu",
    author_email="hyattherate2005@gmail.com",
    description="Generate documentation from Python files using #/ comments",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/Himasnhu-AT/docu",
    project_urls={
        "Bug Tracker": "https://github.com/Himasnhu-AT/docu/issues",
    },
    classifiers=[
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "License :: OSI Approved :: BSD License",
        "Operating System :: OS Independent",
        "Environment :: Console",
        "Intended Audience :: Developers",
        "Topic :: Software Development :: Documentation",
    ],
    packages=find_packages(),
    include_package_data=True,
    python_requires=">=3.7",
    install_requires=[
        "click>=8.0.0",
        "rich>=10.0.0",
        "markdown>=3.3.0",
    ],
    entry_points={
        "console_scripts": [
            "docu=docu.cli:main",
        ],
    },
)