from os import path as op

from setuptools import setup

basedir = op.abspath(op.dirname(__file__))


setup(
    name="AlchemyDumps",
    packages=["alchemydumps"],
    version=open(op.join(basedir, "VERSION")).read().strip(),
    description="SQLAlchemy backup/dump",
    long_description=open(op.join(basedir, "README.md")).read(),
    classifiers=[
        "Development Status :: 3 - Alpha",
        "License :: OSI Approved :: BSD 3-Clause License",
        "Programming Language :: Python :: 3.7",
        "Intended Audience :: Developers",
        "Topic :: Database",
        "Topic :: System :: Archiving :: Backup",
        "Topic :: Utilities",
    ],
    keywords="backup, sqlalchemy, flask, restore, dumps, serialization, ftp, ",
    url="https://gitlab.com/lesleslie/alchemydumps",
    author="Eduardo Cuducos",
    author_email="cuducos@gmail.com",
    maintainer="Les Leslie",
    maintainer_email="les@wedgwoodwebworks.com",
    license="BSD 3-Clause",
    include_package_data=True,
    test_suite="pytest",
    entry_points={"console_scripts": [
        "alchemydumps=alchemydumps.cli:alchemydumps"]},
)
