import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="mhtml_utils", # Replace with your own username
    version="0.0.1",
    author="Viet Le",
    author_email="vietlq85@gmail.com",
    description="Convert MHT/MHTML files to HTML/Excel",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/vietlq/mhtml_utils",
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.4',
)
