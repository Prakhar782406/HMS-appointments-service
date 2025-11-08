@echo off
REM Setup script for MySQL database on Windows
REM This script creates the database for the Appointment Service

echo Setting up MySQL database for Appointment Service...

REM MySQL credentials
set MYSQL_ROOT_PASSWORD=root
set MYSQL_DATABASE=appointment_db

REM Create database (using root user)
mysql -u root -p%MYSQL_ROOT_PASSWORD% -e "CREATE DATABASE IF NOT EXISTS %MYSQL_DATABASE%;"

if %ERRORLEVEL% EQU 0 (
    echo Database setup completed successfully!
    echo   Database: %MYSQL_DATABASE%
    echo   Using root user for database connection
) else (
    echo Database setup failed!
    exit /b 1
)


