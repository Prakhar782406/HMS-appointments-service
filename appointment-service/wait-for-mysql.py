"""
Script to wait for MySQL to be ready before starting the application
"""
import time
import sys
import pymysql
import os

MYSQL_HOST = os.getenv('MYSQL_HOST', 'localhost')
MYSQL_PORT = int(os.getenv('MYSQL_PORT', '33063'))
MYSQL_USER = os.getenv('MYSQL_USER', 'root')
MYSQL_PASSWORD = os.getenv('MYSQL_PASSWORD', 'root')
MYSQL_DATABASE = os.getenv('MYSQL_DATABASE', 'appointment_db')

max_attempts = 30
attempt = 0

while attempt < max_attempts:
    try:
        print(f"Attempting to connect to MySQL at {MYSQL_HOST}:{MYSQL_PORT},{MYSQL_PASSWORD},{MYSQL_USER}...")
        connection = pymysql.connect(
            host=MYSQL_HOST,
            port=MYSQL_PORT,
            user=MYSQL_USER,
            password=MYSQL_PASSWORD,
            database=MYSQL_DATABASE
        )
        connection.close()
        print("MySQL is ready!")
        sys.exit(0)
    except Exception as e:
        print(e)
        attempt += 1
        print(f"Waiting for MySQL... (attempt {attempt}/{max_attempts})")
        if attempt >= max_attempts:
            print(f"MySQL is not ready after {max_attempts} attempts")
            sys.exit(1)
        time.sleep(2)


