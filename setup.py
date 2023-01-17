import os
import setuptools


PACKAGE_NAME = "StocksAssistant"
DELETE_FILENAME = [".DS_Store"]


with open('requirements.txt') as fp:
    install_requires = fp.read()

with open("README.md", "r") as fh:
    long_description = fh.read()


def findPackageData():
    # add path
    paths = [PACKAGE_NAME]
    for (path, directories, filenames) in os.walk(PACKAGE_NAME):
        for filename in filenames:
            if filename not in DELETE_FILENAME:
                paths.append(os.path.join("..", path, filename))
    return paths


setuptools.setup(
    name=PACKAGE_NAME,
    version="0.0.1",
    author="Robert",
    author_email="876pcl@gmail.com",
    description="Stocks assistant",
    license="LICENSE",
    long_description=long_description,
    long_description_content_type="text/markdown",
    packages=setuptools.find_packages(),
    include_package_data=True,
    package_data={"": findPackageData()},
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: License",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.7",
    install_requires=install_requires,
    entry_points={
        'console_scripts': [
            f'{PACKAGE_NAME}={PACKAGE_NAME}.run:run'
        ]
    },
)
