#/user/bin/env bash

python3 -m venv venv
. venv/bin/activate
pip install dist/app-1.0.0-py3-none-any.whl
export FLASK_APP=app
pip install waitress
waitress-serve --call 'app:create_app'
