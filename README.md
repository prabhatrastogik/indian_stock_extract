# Zerodha Stock Extraction Tool - Historical Daily Data

This code repo downloads and saved daily data to a postgres server for analytics and personal use.
It uses "zlogin" package that reads the ccess token from an AWS Dynamodb. Check that package to understand how to use AWS free tier to store access token that is read by this package

## Setup

Create an env variable DBURL that has the link to postgres server where this is to be stored

`export DBURL=postgresql://username:password@url_of_postgres_server:port/database`

Save the Zerodha API Key as an env variable

`export ZAPI=ZerodhaAPIKey`

Set up the process to save access_token in a DynamoDB table 'save_access' with date, datetime, access_token as columns/keys. (Check Zlogin repo for details);

OR create your own zlogin.py that returns "KiteConnect" instance post login and do not install zlogin (edit out in pyproject.toml)

`poetry install`
`poetry run python cli.py --all`