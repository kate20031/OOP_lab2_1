#!/bin/bash

export PYTHONPATH="/home/acer/PycharmProjects/Zaliczeniowy_autobusy"
pip install -r requirements.txt
pylint **/*.py
flake8 **/*.py
black **/*.py
autopep8 --in-place --aggressive --aggressive **/*.py

python -m main