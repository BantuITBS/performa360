import psycopg2
import os

# Connection parameters (Supabase connection string and credentials)
conn_params = {
    'dbname': 'postgres',  # Replace with your database name
    'user': 'postgres.giaxdmydrjwhjfrbwogt',  # From Supabase pooler connection string
    'password': 'MAZAtaka@45_1978',  # Replace with actual password
    'host': 'aws-0-eu-central-1.pooler.supabase.com',  # Session pooler host
    'port': '5432',  # Default PostgreSQL port
    'sslmode': 'require'  # Ensures SSL connection is used
}

print("Connecting to the database...")

# Connect to the Supabase database
try:
    conn = psycopg2.connect(**conn_params)
    print("Connection successful.")
except Exception as e:
    print(f"Error connecting to the database: {e}")
    exit()

# Open a cursor to perform database operations
cur = conn.cursor()

print("Opening the SQL file to execute...")

# Use the full path to the SQL file (absolute path)
sql_file_path = r'C:\Users\TakawiraMazando\desktop\perf_mgmt\user_creation_model.sql'

try:
    with open(sql_file_path, 'r') as f:
        cur.execute(f.read())
    print("SQL file executed successfully.")
except Exception as e:
    print(f"Error executing SQL file: {e}")
    cur.close()
    conn.close()
    exit()

# Commit the changes to the database
try:
    conn.commit()
    print("Changes committed to the database.")
except Exception as e:
    print(f"Error committing changes: {e}")
    conn.rollback()

# Query the table with the correct table name and column names
try:
    cur.execute('SELECT COUNT(*) FROM user_creation_model;')  # Correct table name (no quotes needed)
    row_count = cur.fetchone()[0]
    print(f"Restore success - {row_count} rows found in 'user_creation_model'.")
except Exception as e:
    print(f"Error verifying restore success: {e}")

# Close the cursor and the connection
cur.close()
conn.close()
print("Cursor and connection closed.")
