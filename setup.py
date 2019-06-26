from setuptools import setup

setup(
    name='faceblur',
    version='1.0',
    install_requires=['numpy', 'matplotlib', 'pillow'],
    entry_points={
        'console_scripts': ['blurp=faceblur.run:main'],
    }
)
