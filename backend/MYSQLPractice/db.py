# db.py
# This file is responsible for setting up the connection to the MySQL database using SQLAlchemy.
# SQLAlchemy is a popular Python library that helps you interact with databases in a simple and powerful way.
# The 'engine' object created here will be used in other parts of the application to run SQL queries.

from sqlalchemy import create_engine  # Import the function to create a database engine

# Database connection details:
# These variables store the information needed to connect to your MySQL database.
# - username: The username you use to log in to MySQL
# - password: The password for your MySQL user
# - host: The address of the MySQL server (usually 'localhost' if running on your own computer)
# - database: The name of the database you want to use
username = 'anirudh'
password = 'password123'
host = 'localhost'
database = 'players_data'

# Create the SQLAlchemy engine:
# The engine is the starting point for any SQLAlchemy application.
# It manages the connection pool and lets you execute SQL statements.
# The connection string format is:
#   'mysql+mysqlconnector://<username>:<password>@<host>/<database>'
# - 'mysql+mysqlconnector' tells SQLAlchemy to use the MySQL Connector/Python driver.
# - The rest fills in your connection details.
engine = create_engine(f'mysql+mysqlconnector://{username}:{password}@{host}/{database}')

# Now, you can import 'engine' from this file in other parts of your project to run SQL queries.