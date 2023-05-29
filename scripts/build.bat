if not exist ".\build" mkdir ".\build"
pyinstaller -c -i "../assets/icon.ico" -F -n "pfg" --specpath "build" --distpath "build" --workpath "build" --hidden-import "handlers.econ" --hidden-import "handlers.tag" --hidden-import "handlers.strict" --hidden-import "handlers.import" --hidden-import "handlers.choose" --hidden-import "handlers.format" --hidden-import "handlers.index" "src/main.py"