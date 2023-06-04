@echo off
if not exist ".\build" mkdir ".\build"
pyinstaller -c -i "../assets/icon.ico" -F -n "pfg" --specpath "build" --distpath "build" --workpath "build" "src/main.py"