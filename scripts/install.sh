python -m pip install --upgrade pip
pip install requests
pip install pytest
pip install pytest-cov
[ "$1" != "skip-build-tools" ] && pip install pyinstaller