import wuy
import setuptools

setuptools.setup(
    name='wuy',
    version=wuy.__version__,

    author="manatlan",
    author_email="manatlan@gmail.com",
    description="A simple module for making HTML GUI applications with python3/asyncio",
    long_description=open("README.md","r").read(),
    long_description_content_type="text/markdown",
    url="https://github.com/manatlan/wuy",
    py_modules=["wuy"], #setuptools.find_packages(),
    classifiers=(
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: GNU General Public License v2 (GPLv2)",
        "Operating System :: OS Independent",
    ),
    python_requires='>=3.5',
    install_requires=[
          'aiohttp',
          #~ 'winreg;platform_system=="Windows"'    (doesn't work on w10 ?!)
    ],
    keywords=['gui', 'html', 'javascript', 'electron', "asyncio", "aiohttp", "websocket"],
)
