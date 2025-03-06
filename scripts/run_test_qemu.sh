#!/bin/sh
pip3 install poetry
sudo apt-get install -y dbus-daemon python3-gi libgirepository1.0-dev gcc libcairo2-dev pkg-config python3-dev gir1.2-gtk-3.0
REQUIRE_CYTHON=1 poetry install --only=main,dev
dbus-run-session -- poetry run pytest --cov-report=xml --timeout=5
