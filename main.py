import sqlite3
import mysql.connector
import psycopg2
import pyodbc
import json
import csv
from tabulate import tabulate

def fetch_tables(db_type, **kwargs):
    try:
        if db_type == 'sqlite':
            with sqlite3.connect(kwargs['database']) as conn:
                cursor = conn.cursor()
                cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
                tables = [table[0] for table in cursor.fetchall()]
                return tables

        elif db_type == 'mysql':
            with mysql.connector.connect(
                host=kwargs['host'],
                user=kwargs['user'],
                password=kwargs['password'],
                database=kwargs['database']
            ) as conn:
                cursor = conn.cursor()
                cursor.execute("SHOW TABLES")
                tables = [table[0] for table in cursor.fetchall()]
                return tables

        elif db_type == 'postgresql':
            with psycopg2.connect(
                host=kwargs['host'],
                user=kwargs['user'],
                password=kwargs['password'],
                dbname=kwargs['database']
            ) as conn:
                cursor = conn.cursor()
                cursor.execute("SELECT table_name FROM information_schema.tables WHERE table_schema='public'")
                tables = [table[0] for table in cursor.fetchall()]
                return tables

        elif db_type == 'mssql':
            with pyodbc.connect(
                f"DRIVER={{ODBC Driver 17 for SQL Server}};SERVER={kwargs['server']};DATABASE={kwargs['database']};UID={kwargs['user']};PWD={kwargs['password']}"
            ) as conn:
                cursor = conn.cursor()
                cursor.execute("SELECT table_name FROM information_schema.tables WHERE table_type='BASE TABLE'")
                tables = [table[0] for table in cursor.fetchall()]
                return tables

        else:
            raise ValueError("Unsupported database type.")

    except Exception as e:
        print(f"Error fetching tables: {e}")
        return []

def fetch_data(db_type, **kwargs):
    try:
        if db_type == 'sqlite':
            with sqlite3.connect(kwargs['database']) as conn:
                cursor = conn.cursor()
                table_name = kwargs.get('table')
                query = kwargs.get('query')
                if query:
                    cursor.execute(query)
                elif table_name:
                    cursor.execute(f"PRAGMA table_info({table_name})")
                    columns = [column[1] for column in cursor.fetchall()]
                    if not columns:
                        raise ValueError(f"Table '{table_name}' not found in the database.")
                    cursor.execute(f"SELECT * FROM {table_name}")
                else:
                    raise ValueError("Either table name or custom query is required.")
                rows = cursor.fetchall()
                if rows:
                    print(tabulate(rows, headers=columns if 'columns' in locals() else [], tablefmt="pretty"))
                    if kwargs.get('export'):
                        export_data(rows, columns if 'columns' in locals() else [], kwargs['export'])
                else:
                    print("No data found.")

        elif db_type == 'mysql':
            with mysql.connector.connect(
                host=kwargs['host'],
                user=kwargs['user'],
                password=kwargs['password'],
                database=kwargs['database']
            ) as conn:
                cursor = conn.cursor()
                table_name = kwargs.get('table')
                query = kwargs.get('query')
                if query:
                    cursor.execute(query)
                elif table_name:
                    cursor.execute(f"SELECT COLUMN_NAME FROM INFORMATION_SCHEMA.COLUMNS WHERE TABLE_NAME = '{table_name}' AND TABLE_SCHEMA = '{kwargs['database']}'")
                    columns = [column[0] for column in cursor.fetchall()]
                    if not columns:
                        raise ValueError(f"Table '{table_name}' not found in the database.")
                    cursor.execute(f"SELECT * FROM {table_name}")
                else:
                    raise ValueError("Either table name or custom query is required.")
                rows = cursor.fetchall()
                if rows:
                    print(tabulate(rows, headers=columns if 'columns' in locals() else [], tablefmt="pretty"))
                    if kwargs.get('export'):
                        export_data(rows, columns if 'columns' in locals() else [], kwargs['export'])
                else:
                    print("No data found.")

        elif db_type == 'postgresql':
            with psycopg2.connect(
                host=kwargs['host'],
                user=kwargs['user'],
                password=kwargs['password'],
                dbname=kwargs['database']
            ) as conn:
                cursor = conn.cursor()
                table_name = kwargs.get('table')
                query = kwargs.get('query')
                if query:
                    cursor.execute(query)
                elif table_name:
                    cursor.execute(f"SELECT column_name FROM information_schema.columns WHERE table_name = '{table_name}'")
                    columns = [column[0] for column in cursor.fetchall()]
                    if not columns:
                        raise ValueError(f"Table '{table_name}' not found in the database.")
                    cursor.execute(f"SELECT * FROM {table_name}")
                else:
                    raise ValueError("Either table name or custom query is required.")
                rows = cursor.fetchall()
                if rows:
                    print(tabulate(rows, headers=columns if 'columns' in locals() else [], tablefmt="pretty"))
                    if kwargs.get('export'):
                        export_data(rows, columns if 'columns' in locals() else [], kwargs['export'])
                else:
                    print("No data found.")

        elif db_type == 'mssql':
            with pyodbc.connect(
                f"DRIVER={{ODBC Driver 17 for SQL Server}};SERVER={kwargs['server']};DATABASE={kwargs['database']};UID={kwargs['user']};PWD={kwargs['password']}"
            ) as conn:
                cursor = conn.cursor()
                table_name = kwargs.get('table')
                query = kwargs.get('query')
                if query:
                    cursor.execute(query)
                elif table_name:
                    cursor.execute(f"SELECT COLUMN_NAME FROM INFORMATION_SCHEMA.COLUMNS WHERE TABLE_NAME = '{table_name}'")
                    columns = [column[0] for column in cursor.fetchall()]
                    if not columns:
                        raise ValueError(f"Table '{table_name}' not found in the database.")
                    cursor.execute(f"SELECT * FROM {table_name}")
                else:
                    raise ValueError("Either table name or custom query is required.")
                rows = cursor.fetchall()
                if rows:
                    print(tabulate(rows, headers=columns if 'columns' in locals() else [], tablefmt="pretty"))
                    if kwargs.get('export'):
                        export_data(rows, columns if 'columns' in locals() else [], kwargs['export'])
                else:
                    print("No data found.")

        elif db_type == 'json':
            json_file = kwargs.get('file')
            if not json_file:
                raise ValueError("JSON file path is required.")
            with open(json_file, 'r') as f:
                data = json.load(f)
                print(json.dumps(data, indent=4))
                if kwargs.get('export'):
                    export_data(data, None, kwargs['export'])

        else:
            raise ValueError("Unsupported database type. Supported types: sqlite, mysql, postgresql, mssql, json.")

    except Exception as e:
        print(f"Error: {e}")

def export_data(data, columns, export_format):
    try:
        if export_format == 'csv':
            with open('output.csv', 'w', newline='') as f:
                writer = csv.writer(f)
                if columns:
                    writer.writerow(columns)
                writer.writerows(data)
            print("Data exported to output.csv")
        elif export_format == 'json':
            with open('output.json', 'w') as f:
                json.dump(data, f, indent=4)
            print("Data exported to output.json")
        else:
            raise ValueError("Unsupported export format. Supported formats: csv, json.")
    except Exception as e:
        print(f"Error exporting data: {e}")

def main():
    db_type = input("Enter database type (sqlite, mysql, postgresql, mssql, json): ").strip().lower()
    if db_type not in ['sqlite', 'mysql', 'postgresql', 'mssql', 'json']:
        print("Unsupported database type.")
        return

    if db_type == 'sqlite':
        database_file = input("Enter SQLite database file path: ").strip()
        tables = fetch_tables(db_type, database=database_file)
        if not tables:
            print("No tables found in the database.")
            return
        print("Available tables:")
        for i, table in enumerate(tables, 1):
            print(f"{i}. {table}")
        table_choice = input("Enter the number of the table to fetch data from (or leave blank to use custom query): ").strip()
        if table_choice:
            table_name = tables[int(table_choice) - 1]
            fetch_data(db_type, database=database_file, table=table_name, export=input("Export data to (csv/json) or leave blank: ").strip())
        else:
            query = input("Enter custom query: ").strip()
            fetch_data(db_type, database=database_file, query=query, export=input("Export data to (csv/json) or leave blank: ").strip())

    elif db_type == 'mysql':
        host = input("Enter MySQL host: ").strip()
        user = input("Enter MySQL user: ").strip()
        password = input("Enter MySQL password: ").strip()
        database = input("Enter MySQL database name: ").strip()
        tables = fetch_tables(db_type, host=host, user=user, password=password, database=database)
        if not tables:
            print("No tables found in the database.")
            return
        print("Available tables:")
        for i, table in enumerate(tables, 1):
            print(f"{i}. {table}")
        table_choice = input("Enter the number of the table to fetch data from (or leave blank to use custom query): ").strip()
        if table_choice:
            table_name = tables[int(table_choice) - 1]
            fetch_data(db_type, host=host, user=user, password=password, database=database, table=table_name, export=input("Export data to (csv/json) or leave blank: ").strip())
        else:
            query = input("Enter custom query: ").strip()
            fetch_data(db_type, host=host, user=user, password=password, database=database, query=query, export=input("Export data to (csv/json) or leave blank: ").strip())

    elif db_type == 'postgresql':
        host = input("Enter PostgreSQL host: ").strip()
        user = input("Enter PostgreSQL user: ").strip()
        password = input("Enter PostgreSQL password: ").strip()
        database = input("Enter PostgreSQL database name: ").strip()
        tables = fetch_tables(db_type, host=host, user=user, password=password, database=database)
        if not tables:
            print("No tables found in the database.")
            return
        print("Available tables:")
        for i, table in enumerate(tables, 1):
            print(f"{i}. {table}")
        table_choice = input("Enter the number of the table to fetch data from (or leave blank to use custom query): ").strip()
        if table_choice:
            table_name = tables[int(table_choice) - 1]
            fetch_data(db_type, host=host, user=user, password=password, database=database, table=table_name, export=input("Export data to (csv/json) or leave blank: ").strip())
        else:
            query = input("Enter custom query: ").strip()
            fetch_data(db_type, host=host, user=user, password=password, database=database, query=query, export=input("Export data to (csv/json) or leave blank: ").strip())

    elif db_type == 'mssql':
        server = input("Enter MSSQL server: ").strip()
        user = input("Enter MSSQL user: ").strip()
        password = input("Enter MSSQL password: ").strip()
        database = input("Enter MSSQL database name: ").strip()
        tables = fetch_tables(db_type, server=server, user=user, password=password, database=database)
        if not tables:
            print("No tables found in the database.")
            return
        print("Available tables:")
        for i, table in enumerate(tables, 1):
            print(f"{i}. {table}")
        table_choice = input("Enter the number of the table to fetch data from (or leave blank to use custom query): ").strip()
        if table_choice:
            table_name = tables[int(table_choice) - 1]
            fetch_data(db_type, server=server, user=user, password=password, database=database, table=table_name, export=input("Export data to (csv/json) or leave blank: ").strip())
        else:
            query = input("Enter custom query: ").strip()
            fetch_data(db_type, server=server, user=user, password=password, database=database, query=query, export=input("Export data to (csv/json) or leave blank: ").strip())

    elif db_type == 'json':
        json_file = input("Enter JSON file path: ").strip()
        fetch_data(db_type, file=json_file, export=input("Export data to (csv/json) or leave blank: ").strip())

if __name__ == "__main__":
    main()