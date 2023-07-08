if [ "$1" == "rep" ]
then
    COVERAGE_FOLDER=htmlcov
    COVERAGE_FILE=$COVERAGE_FOLDER/index.html
    if [ ! -d $COVERAGE_FOLDER ]
    then
        mkdir $COVERAGE_FOLDER
        touch $COVERAGE_FILE
        echo "<h1>Refresh this web page to see the coverage report!</h1>" > $COVERAGE_FILE
    fi
    start $COVERAGE_FILE # Windows only
fi

nodemon --exec "bash scripts/test.sh $@ || exit 1" --ext .py # Requires node and nodemon installed