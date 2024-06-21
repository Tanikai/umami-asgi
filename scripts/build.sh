#!/bin/sh

python -m build
twine check dist/*
