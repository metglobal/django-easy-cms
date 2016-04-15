import os
from setuptools import setup, find_packages

README = open(os.path.join(os.path.dirname(__file__), 'README.md')).read()

# allow setup.py to be run from any path
os.chdir(os.path.normpath(os.path.join(os.path.abspath(__file__), os.pardir)))

setup(
    name='django-easy-cms',
    version='0.1',
    packages=find_packages(),
    include_package_data=True,
    description='A basic cms application for Django.',
    long_description=README,
    url='https://github.com/metglobal/django-easy-cms',
    author='Metglobal',
    author_email='can.ozdemir@metglobal.com',
    install_requires=[
        'django>=1.5',
        'jsonfield==0.9.20',
        'django-hvad>=0.4.1',
        'django-markdown==0.7.0',
    ],
    dependency_links=[
        'https://github.com/KristianOellegaard/django-hvad.git#egg=django-hvad'
    ],
    classifiers=[
        'Development Status :: 5 - Production/Stable',
        'Intended Audience :: Developers',
        'Natural Language :: English',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Programming Language :: Python :: 2.7',
        'Topic :: Internet :: WWW/HTTP',
    ],
)
