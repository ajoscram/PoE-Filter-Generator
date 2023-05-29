nodemon --exec "pytest --cov=src --no-cov-on-fail || exit 1" --ext py
:: --cov-fail-under=95 <- remember to add this once coverage is high
:: --cov-report=html to get an html report