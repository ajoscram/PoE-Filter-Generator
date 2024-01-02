COMMAND="pytest --cov=src --no-cov-on-fail --cov-fail-under=99.5"
[ "$1" == "rep" ] && COMMAND="$COMMAND --cov-report=html"
$COMMAND