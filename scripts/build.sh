[ ! -d "build" ] && mkdir "build"
pyinstaller \
    -c -F \
    -i "../assets/icon.ico" \
    -n "pfg" \
    --specpath "build" \
    --distpath "build" \
    --workpath "build" \
    "src/main.py"