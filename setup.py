from setuptools import setup, find_packages

setup(
    name="altkinter",
    version="0.1.0",
    description="A modern Tkinter widget library with custom themes and controls.",
    author="Saurabh Odukle",
    author_email="odukle@gmail.com",
    url="https://github.com/odukle/altkinter",
    packages=find_packages(),
    install_requires=[
        "Pillow",
        "pycairo"
    ],
    python_requires=">=3.7",
    include_package_data=True,
    license="MIT",
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
)