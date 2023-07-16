python -m pip install --upgrade pip
[ "$1" != "skip-build-tools" ] && pip install pyinstaller
pip install requests
pip install rich
pip install pytest
pip install pytest-cov