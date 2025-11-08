#!/bin/bash

# Setup script for MySQL database
# This script creates the database for the Appointment Service

echo "Setting up MySQL database for Appointment Service..."

# MySQL credentials
MYSQL_ROOT_PASSWORD=${MYSQL_ROOT_PASSWORD:-"root"}
MYSQL_DATABASE="appointment_db"

# Create database (using root user)
mysql -u root -p"$MYSQL_ROOT_PASSWORD" <<EOF
CREATE DATABASE IF NOT EXISTS $MYSQL_DATABASE;
EOF

if [ $? -eq 0 ]; then
    echo "✓ Database setup completed successfully!"
    echo "  Database: $MYSQL_DATABASE"
    echo "  Using root user for database connection"
else
    echo "✗ Database setup failed!"
    exit 1
fi


