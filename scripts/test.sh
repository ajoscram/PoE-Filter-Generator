command="pytest --cov=src --no-cov-on-fail --cov-fail-under=99.5"
[ "$1" == "report" ] && command="$command --cov-report=html"
$command