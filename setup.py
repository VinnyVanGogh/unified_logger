from setuptools import setup, find_packages

setup(
    name="cw-rpa-unified-logger",
    version="0.1.0",
    packages=find_packages(where="src"),
    package_dir={"": "src"},
    install_requires=[
        "colorlog>=6.7.0",
        "requests>=2.28.0"
    ],
    extras_require={
        "asio": ["cw-rpa"]
    },
    python_requires=">=3.9"
)
