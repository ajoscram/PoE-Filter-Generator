if [ "$1" == "report" ]
then
    coverage_folder=htmlcov
    coverage_file=$coverage_folder/index.html
    if [ ! -d $coverage_folder ]
    then
        mkdir $coverage_folder
        touch $coverage_file
        echo "<h1>Refresh this web page to see the coverage report!</h1>" > $coverage_file
    fi
    start $coverage_file # Windows only
fi

python tools/pymon.py "bash scripts/test.sh $@" "src\**\*.py" "tests\**\*.py"