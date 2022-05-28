#/user/bin/env bash

python3 -m venv venv
. venv/bin/activate
venv/bin/python3 -m pip install --upgrade pip
pip install requests
pip install numpy
pip install Flask
pip install wheel
python setup.py bdist_wheel
