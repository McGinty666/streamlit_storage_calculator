import streamlit as st
import pyodbc
import pandas as pd

def get_data_from_azure():
    # Define your Azure SQL database connection details
    server = 'your_server.database.windows.net'
    database = 'your_database'
    username = 'your_username'
    password = 'your_password'
    driver = '{ODBC Driver 17 for SQL Server}'

    # Establish a connection to the database
    conn = pyodbc.connect(f'DRIVER={driver};SERVER={server};PORT=1433;DATABASE={database};UID={username};PWD={password}')
    query = 'SELECT * FROM your_table'  # Replace with your actual query

    # Execute the query and fetch the data
    data = pd.read_sql(query, conn)
    conn.close()

    return data

def main():
    st.title("Azure Database Data Import")

    if st.button("Import Data"):
        data = get_data_from_azure()
        st.write("Data imported successfully!")
        st.write(data)

if __name__ == "__main__":
    main()