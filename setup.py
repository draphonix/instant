from setuptools import setup, find_packages

setup(
    name='instant',
    version='0.1.0',
    packages=find_packages(),
    include_package_data=True,
    install_requires=[
        'click',
        'python-dotenv',
    ],
    entry_points={
        'console_scripts': [
            'instant = instant:cli',
        ],
    },
)