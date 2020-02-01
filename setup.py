from setuptools import setup

setup(
    name="chainee",
    description="Blockchain implementation",
    version="0.1",
    author="Stepan Vetrovec",
    python_requires=">=3.6",
    packages=["chainee"],
    entry_points={
        "console_scripts": [
            "chainee-node = chainee.node:main",
            "chainee-tools = chainee.tools:main",
        ],
    },
    install_requires=["secp256k1"]
)
