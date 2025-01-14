## Database Viewer and Exporter
- This is a Python tool for viewing and exporting data from various databases and JSON files. It supports `SQLite`, `MySQL`, `PostgreSQL`, `MSSQL`, and `JSON` files. Users can also export query results in `CSV` or `JSON` formats. The tool is designed to handle encrypted data using multiple encryption algorithms and can decrypt data that has been encrypted with a combination of algorithms

## Features
- **Support for Multiple Database Types**:
    - SQLite
    - MySQL
    - PostgreSQL
    - MSSQL
    - JSON files
- **Automatic Table Detection**:
    - Lists all tables in the database for easy selection.
- **Custom Queries**:
    - Allows users to run custom SQL queries.
- **Data Export**:
    - Export query results or table data to `CSV` or `JSON` formats.
- **User-Friendly Interface**:
    - Interactive command-line interface for easy navigation.
- **Error Handling**:
    - Provides clear error messages for invalid inputs or connection issues.
- **Support for Encrypted Data**:
    - Decrypts data using multiple encryption algorithms:
        - **AES**: Symmetric encryption.
        - **DES**: Symmetric encryption.
        - **3DES**: Symmetric encryption.
        - **RSA**: Asymmetric encryption.
        - **ECC**: Elliptic Curve Cryptography.
        - **SHA-256**: Hashing algorithm./
        - **MD5**: Hashing algorithm.
        - **bcrypt**: Password hashing.
- **Combined Encryption Support**:
    - Handles data encrypted with a combination of algorithms (e.g., RSA + AES).
- **Data Compression**:
    Supports decompression of data using `zlib`.
- **Logging**:
    - Logs errors and important events to a file for debugging.
- **Configuration Support**:
    - Loads settings from a configuration file (`config.json`).
- **Parallel Database Connections**:
    - Connects to multiple databases simultaneously and executes queries in parallel.
---

## Requirements
- Python 3.6 or higher
- Required Python packages:
    - `cryptography`
    - `mysql-connector-python`
    - `psycopg2`
    - `pyodbc`
    - `tabulate`
    - `bcrypt`
- Install the required packages using:
    ```bash
    pip install cryptography mysql-connector-python psycopg2 pyodbc tabulate bcrypt
    ```
---

## How to Use
1. **Run the Script**:
    - Execute the script using Python:
        ```bash
        python database_viewer.py
        ```
2. **Select Database Type**:
    - Choose the database type (`sqlite`, `mysql`, `postgresql`, `mssql`, or `json`).
3. **Provide Connection Details**:
    - For *SQLite*: Provide the path to the database file.
    - For *MySQL*, *PostgreSQL*, and *MSSQL*: Provide host, user, password, and database name.
    - For *JSON*: Provide the path to the JSON file.
4. **Enter Encryption Details**:
    - Provide the encryption password and salt.
    - If applicable, provide the path to an RSA or ECC private key file.
5. **Choose a Table or Enter a Custom Query**:
    - The script will list all available tables. Select a table by entering its number.
    - Alternatively, enter a custom SQL query. 
6. **Export Data (Optional)**:
    - Choose to export the results to `CSV` or `JSON` format.
---

## Example Usage
- **SQLite Example**
    ```bash
    Enter database type (sqlite, mysql, postgresql, mssql, json): sqlite
    Enter SQLite database file path: example.db
    Available tables:
    1. users
    2. orders
    Enter the number of the table to fetch data from (or leave blank to use custom query): 1
    Export data to (csv/json) or leave blank: csv
    ```
- **MySQL Example**
    ```bash
    Enter database type (sqlite, mysql, postgresql, mssql, json): mysql
    Enter MySQL host: localhost
    Enter MySQL user: root
    Enter MySQL password: password
    Enter MySQL database name: my_db
    Available tables:
    1. customers
    2. products
    Enter the number of the table to fetch data from (or leave blank to use custom query): 2
    Export data to (csv/json) or leave blank: json
    ```
- **JSON Example**
    ```bash
    Enter database type (sqlite, mysql, postgresql, mssql, json): json
    Enter JSON file path: data.json
    Export data to (csv/json) or leave blank: csv
    ```
---

## Exporting Data
- **CSV**:
    - Exported to `output.csv`.
- **JSON**:
    - Exported to `output.json`.
---

## Supported Database Drivers
- **SQLite**: Built into Python.
- **MySQL**: Requires mysql-connector-python.
- **PostgreSQL**: Requires psycopg2.
- **MSSQL**: Requires pyodbc.
---

## License
- This project is open-source and available under the MIT [License](https://github.com/MrAmirRezaie/readDatabase/blob/main/LICENSE).
---

## Contributing
- Contributions are welcome! Please open an issue or submit a pull request for any improvements or bug fixes.
---

## Contact

For questions, feedback, or bug reports, contact the maintainer:
- **Email**: MrAmirRezaie70@gmail.com
- **Telegram**: [@MrAmirRezaie](https://t.me/MrAmirRezaie)
- **GitHub**: [MrAmirRezaie](https://github.com/MrAmirRezaie/)
---

**Enjoy using the Database Viewer and Exporter! 🚀**