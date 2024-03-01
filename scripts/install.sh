python -m pip install --upgrade pip
[ "$1" != "skip-build-tools" ] && pip install -U pyinstaller
pip install -U requests
pip install -U rich
pip install -U pytest
pip install -U pytest-cov