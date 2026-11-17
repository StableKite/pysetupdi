from setuptools import setup
import os.path
import sys

setup(
    name='pysetupdi',
    version='2018.10.23+stablekite.2',
    packages=['pysetupdi'],
    package_data={'pysetupdi': ['py.typed', '*.pyi']},
    python_requires='>=3.10',
    url='https://github.com/gwangyi/pysetupdi',
    license='MIT',
    author='Sungkwang Lee',
    author_email='gwangyi.kr@gmail.com',
    description='Python SetupAPI wrapper',
    platforms=['win32'],
    entry_points={
        'console_scripts': ['pysetupdi=pysetupdi.__main__:main']
    }
)
