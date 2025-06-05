#!/bin/bash
# Connect to SQL Server db.


# Load .env file safely (without needing export in each line)
if [ -f .env ]; then
    echo "Loading environment variables from .env..."
    set -o allexport
    source ../.env
    set +o allexport
else
    echo ".env file not found. Aborting."
    exit 1
fi

# Connect to the database using sqlcmd
echo "Connecting to database $DB_NAME ..."
sqlcmd -S $DB_HOST,$DB_PORT -U $DB_USER -P $DB_PASSWORD -d $DB_NAME