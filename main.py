import sqlite3
import mysql.connector
import psycopg2
import pyodbc
import json
import csv
import zlib
import logging
from tabulate import tabulate
from cryptography.fernet import Fernet, InvalidToken
from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from cryptography.hazmat.primitives.asymmetric import rsa, padding, ec
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.hazmat.backends import default_backend
import base64
import os
import hashlib
import bcrypt
from concurrent.futures import ThreadPoolExecutor

# Configure logging
logging.basicConfig(filename='database_viewer.log', level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def derive_key(password, salt):
    """
    Derives a key from a password and salt using PBKDF2HMAC.
    """
    kdf = PBKDF2HMAC(
        algorithm=hashes.SHA256(),
        length=32,
        salt=salt,
        iterations=100000,
        backend=default_backend()
    )
    return base64.urlsafe_b64encode(kdf.derive(password.encode()))

def decrypt_aes(encrypted_data, key):
    """
    Decrypts data using AES symmetric encryption.
    """
    try:
        # Split the encrypted data into IV and ciphertext
        iv = encrypted_data[:16]
        ciphertext = encrypted_data[16:]

        # Create a Cipher object
        cipher = Cipher(algorithms.AES(key), modes.CFB(iv), backend=default_backend())
        decryptor = cipher.decryptor()

        # Decrypt the data
        decrypted_data = decryptor.update(ciphertext) + decryptor.finalize()
        return decrypted_data
    except Exception as e:
        logging.error(f"AES decryption failed: {e}")
        return None

def decrypt_des(encrypted_data, key):
    """
    Decrypts data using DES symmetric encryption.
    """
    try:
        # Split the encrypted data into IV and ciphertext
        iv = encrypted_data[:8]
        ciphertext = encrypted_data[8:]

        # Create a Cipher object
        cipher = Cipher(algorithms.TripleDES(key), modes.CFB(iv), backend=default_backend())
        decryptor = cipher.decryptor()

        # Decrypt the data
        decrypted_data = decryptor.update(ciphertext) + decryptor.finalize()
        return decrypted_data
    except Exception as e:
        logging.error(f"DES decryption failed: {e}")
        return None

def decrypt_3des(encrypted_data, key):
    """
    Decrypts data using 3DES symmetric encryption.
    """
    try:
        # Split the encrypted data into IV and ciphertext
        iv = encrypted_data[:8]
        ciphertext = encrypted_data[8:]

        # Create a Cipher object
        cipher = Cipher(algorithms.TripleDES(key), modes.CFB(iv), backend=default_backend())
        decryptor = cipher.decryptor()

        # Decrypt the data
        decrypted_data = decryptor.update(ciphertext) + decryptor.finalize()
        return decrypted_data
    except Exception as e:
        logging.error(f"3DES decryption failed: {e}")
        return None

def decrypt_rsa(encrypted_data, private_key):
    """
    Decrypts data using RSA asymmetric encryption.
    """
    try:
        decrypted_data = private_key.decrypt(
            encrypted_data,
            padding.OAEP(
                mgf=padding.MGF1(algorithm=hashes.SHA256()),
                algorithm=hashes.SHA256(),
                label=None
            )
        )
        return decrypted_data
    except Exception as e:
        logging.error(f"RSA decryption failed: {e}")
        return None

def decrypt_ecc(encrypted_data, private_key):
    """
    Decrypts data using ECC asymmetric encryption.
    """
    try:
        decrypted_data = private_key.decrypt(
            encrypted_data,
            ec.ECDH()
        )
        return decrypted_data
    except Exception as e:
        logging.error(f"ECC decryption failed: {e}")
        return None

def decompress_data(compressed_data):
    """
    Decompresses data using zlib.
    """
    try:
        return zlib.decompress(compressed_data)
    except Exception as e:
        logging.error(f"Decompression failed: {e}")
        return None

def decrypt_combined(encrypted_data, key, private_key=None):
    """
    Decrypts data that has been encrypted with multiple algorithms in combination.
    """
    try:
        # Step 1: Try RSA decryption (if private key is provided)
        if private_key and isinstance(private_key, rsa.RSAPrivateKey):
            decrypted_data = decrypt_rsa(encrypted_data, private_key)
            if decrypted_data is not None:
                encrypted_data = decrypted_data

        # Step 2: Try AES decryption
        decrypted_data = decrypt_aes(encrypted_data, key)
        if decrypted_data is not None:
            encrypted_data = decrypted_data

        # Step 3: Try DES decryption
        decrypted_data = decrypt_des(encrypted_data, key)
        if decrypted_data is not None:
            encrypted_data = decrypted_data

        # Step 4: Try 3DES decryption
        decrypted_data = decrypt_3des(encrypted_data, key)
        if decrypted_data is not None:
            encrypted_data = decrypted_data

        # Step 5: Try ECC decryption (if private key is provided)
        if private_key and isinstance(private_key, ec.EllipticCurvePrivateKey):
            decrypted_data = decrypt_ecc(encrypted_data, private_key)
            if decrypted_data is not None:
                encrypted_data = decrypted_data

        # Step 6: Try decompression
        decompressed_data = decompress_data(encrypted_data)
        if decompressed_data is not None:
            encrypted_data = decompressed_data

        return encrypted_data.decode('utf-8') if isinstance(encrypted_data, bytes) else encrypted_data
    except Exception as e:
        logging.error(f"Combined decryption failed: {e}")
        return None

def fetch_tables(db_type, **kwargs):
    """
    Fetches the list of tables in the database.
    """
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

        elif db_type == 'json':
            # JSON files don't have tables, so return a dummy value
            return ["data"]

        else:
            raise ValueError("Unsupported database type.")

    except Exception as e:
        logging.error(f"Error fetching tables: {e}")
        return []

def fetch_data(db_type, **kwargs):
    """
    Fetches and decrypts data from the database or JSON file.
    """
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
                    decrypted_rows = []
                    for row in rows:
                        decrypted_row = []
                        for cell in row:
                            if isinstance(cell, bytes):
                                decrypted_cell = decrypt_combined(cell, kwargs['key'], kwargs.get('private_key'))
                                decrypted_row.append(decrypted_cell if decrypted_cell is not None else cell)
                            else:
                                decrypted_row.append(cell)
                        decrypted_rows.append(decrypted_row)
                    print(tabulate(decrypted_rows, headers=columns if 'columns' in locals() else [], tablefmt="pretty"))
                    if kwargs.get('export'):
                        export_data(decrypted_rows, columns if 'columns' in locals() else [], kwargs['export'])
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
                    decrypted_rows = []
                    for row in rows:
                        decrypted_row = []
                        for cell in row:
                            if isinstance(cell, bytes):
                                decrypted_cell = decrypt_combined(cell, kwargs['key'], kwargs.get('private_key'))
                                decrypted_row.append(decrypted_cell if decrypted_cell is not None else cell)
                            else:
                                decrypted_row.append(cell)
                        decrypted_rows.append(decrypted_row)
                    print(tabulate(decrypted_rows, headers=columns if 'columns' in locals() else [], tablefmt="pretty"))
                    if kwargs.get('export'):
                        export_data(decrypted_rows, columns if 'columns' in locals() else [], kwargs['export'])
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
                    decrypted_rows = []
                    for row in rows:
                        decrypted_row = []
                        for cell in row:
                            if isinstance(cell, bytes):
                                decrypted_cell = decrypt_combined(cell, kwargs['key'], kwargs.get('private_key'))
                                decrypted_row.append(decrypted_cell if decrypted_cell is not None else cell)
                            else:
                                decrypted_row.append(cell)
                        decrypted_rows.append(decrypted_row)
                    print(tabulate(decrypted_rows, headers=columns if 'columns' in locals() else [], tablefmt="pretty"))
                    if kwargs.get('export'):
                        export_data(decrypted_rows, columns if 'columns' in locals() else [], kwargs['export'])
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
                    decrypted_rows = []
                    for row in rows:
                        decrypted_row = []
                        for cell in row:
                            if isinstance(cell, bytes):
                                decrypted_cell = decrypt_combined(cell, kwargs['key'], kwargs.get('private_key'))
                                decrypted_row.append(decrypted_cell if decrypted_cell is not None else cell)
                            else:
                                decrypted_row.append(cell)
                        decrypted_rows.append(decrypted_row)
                    print(tabulate(decrypted_rows, headers=columns if 'columns' in locals() else [], tablefmt="pretty"))
                    if kwargs.get('export'):
                        export_data(decrypted_rows, columns if 'columns' in locals() else [], kwargs['export'])
                else:
                    print("No data found.")

        elif db_type == 'json':
            json_file = kwargs.get('file')
            if not json_file:
                raise ValueError("JSON file path is required.")
            with open(json_file, 'r') as f:
                data = json.load(f)
                if isinstance(data, list):
                    print(tabulate(data, headers="keys", tablefmt="pretty"))
                else:
                    print(json.dumps(data, indent=4))
                if kwargs.get('export'):
                    export_data(data, None, kwargs['export'])

        else:
            raise ValueError("Unsupported database type. Supported types: sqlite, mysql, postgresql, mssql, json.")

    except Exception as e:
        logging.error(f"Error: {e}")

def export_data(data, columns, export_format):
    """
    Exports data to CSV or JSON format.
    """
    try:
        if export_format == 'csv':
            with open('output.csv', 'w', newline='') as f:
                writer = csv.writer(f)
                if columns:
                    writer.writerow(columns)
                if isinstance(data, list):
                    writer.writerows(data)
                else:
                    writer.writerow([data])
            print("Data exported to output.csv")
        elif export_format == 'json':
            with open('output.json', 'w') as f:
                json.dump(data, f, indent=4)
            print("Data exported to output.json")
        else:
            raise ValueError("Unsupported export format. Supported formats: csv, json.")
    except Exception as e:
        logging.error(f"Error exporting data: {e}")

def load_private_key(private_key_path):
    """
    Loads an RSA or ECC private key from a file.
    """
    try:
        with open(private_key_path, "rb") as key_file:
            private_key = serialization.load_pem_private_key(
                key_file.read(),
                password=None,
                backend=default_backend()
            )
            return private_key
    except Exception as e:
        logging.error(f"Error loading private key: {e}")
        return None

def main():
    db_type = input("Enter database type (sqlite, mysql, postgresql, mssql, json): ").strip().lower()
    if db_type not in ['sqlite', 'mysql', 'postgresql', 'mssql', 'json']:
        print("Unsupported database type.")
        return

    password = input("Enter encryption password: ").strip()
    salt = input("Enter encryption salt: ").strip().encode()
    key = derive_key(password, salt)

    private_key = None
    if input("Do you have an RSA or ECC private key? (yes/no): ").strip().lower() == 'yes':
        private_key_path = input("Enter the path to the private key file: ").strip()
        private_key = load_private_key(private_key_path)

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
            fetch_data(db_type, database=database_file, table=table_name, key=key, private_key=private_key, export=input("Export data to (csv/json) or leave blank: ").strip())
        else:
            query = input("Enter custom query: ").strip()
            fetch_data(db_type, database=database_file, query=query, key=key, private_key=private_key, export=input("Export data to (csv/json) or leave blank: ").strip())

    elif db_type == 'mysql':
        host = input("Enter MySQL host: ").strip()
        user = input("Enter MySQL user: ").strip()
        password_db = input("Enter MySQL password: ").strip()
        database = input("Enter MySQL database name: ").strip()
        tables = fetch_tables(db_type, host=host, user=user, password=password_db, database=database)
        if not tables:
            print("No tables found in the database.")
            return
        print("Available tables:")
        for i, table in enumerate(tables, 1):
            print(f"{i}. {table}")
        table_choice = input("Enter the number of the table to fetch data from (or leave blank to use custom query): ").strip()
        if table_choice:
            table_name = tables[int(table_choice) - 1]
            fetch_data(db_type, host=host, user=user, password=password_db, database=database, table=table_name, key=key, private_key=private_key, export=input("Export data to (csv/json) or leave blank: ").strip())
        else:
            query = input("Enter custom query: ").strip()
            fetch_data(db_type, host=host, user=user, password=password_db, database=database, query=query, key=key, private_key=private_key, export=input("Export data to (csv/json) or leave blank: ").strip())

    elif db_type == 'postgresql':
        host = input("Enter PostgreSQL host: ").strip()
        user = input("Enter PostgreSQL user: ").strip()
        password_db = input("Enter PostgreSQL password: ").strip()
        database = input("Enter PostgreSQL database name: ").strip()
        tables = fetch_tables(db_type, host=host, user=user, password=password_db, database=database)
        if not tables:
            print("No tables found in the database.")
            return
        print("Available tables:")
        for i, table in enumerate(tables, 1):
            print(f"{i}. {table}")
        table_choice = input("Enter the number of the table to fetch data from (or leave blank to use custom query): ").strip()
        if table_choice:
            table_name = tables[int(table_choice) - 1]
            fetch_data(db_type, host=host, user=user, password=password_db, database=database, table=table_name, key=key, private_key=private_key, export=input("Export data to (csv/json) or leave blank: ").strip())
        else:
            query = input("Enter custom query: ").strip()
            fetch_data(db_type, host=host, user=user, password=password_db, database=database, query=query, key=key, private_key=private_key, export=input("Export data to (csv/json) or leave blank: ").strip())

    elif db_type == 'mssql':
        server = input("Enter MSSQL server: ").strip()
        user = input("Enter MSSQL user: ").strip()
        password_db = input("Enter MSSQL password: ").strip()
        database = input("Enter MSSQL database name: ").strip()
        tables = fetch_tables(db_type, server=server, user=user, password=password_db, database=database)
        if not tables:
            print("No tables found in the database.")
            return
        print("Available tables:")
        for i, table in enumerate(tables, 1):
            print(f"{i}. {table}")
        table_choice = input("Enter the number of the table to fetch data from (or leave blank to use custom query): ").strip()
        if table_choice:
            table_name = tables[int(table_choice) - 1]
            fetch_data(db_type, server=server, user=user, password=password_db, database=database, table=table_name, key=key, private_key=private_key, export=input("Export data to (csv/json) or leave blank: ").strip())
        else:
            query = input("Enter custom query: ").strip()
            fetch_data(db_type, server=server, user=user, password=password_db, database=database, query=query, key=key, private_key=private_key, export=input("Export data to (csv/json) or leave blank: ").strip())

    elif db_type == 'json':
        json_file = input("Enter JSON file path: ").strip()
        fetch_data(db_type, file=json_file, key=key, private_key=private_key, export=input("Export data to (csv/json) or leave blank: ").strip())

if __name__ == "__main__":
    main()