@echo off
:: --cov-fail-under=95 <- remember to add this once coverage is high
set command=pytest --cov=src --no-cov-on-fail
if "%1"=="cov" (
    set command=%command% --cov-report=html
    if not exist ".\htmlcov" (
        mkdir ".\htmlcov"
        type NUL >%CD%\htmlcov\index.html
        echo ^<h1^>Refresh this web page to see the coverage report!^</h1^> >%CD%\htmlcov\index.html
    )
    start file:///%CD%\htmlcov\index.html
)
nodemon --exec "%command% || exit 1" --ext .py