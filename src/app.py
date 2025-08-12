from flask import Flask, render_template, request, redirect, url_for
import mysql.connector
import os
from mysql.connector import Error

app = Flask(__name__)

# Database configuration
DB_CONFIG = {
    'host': os.getenv('DB_HOST', 'mysql'),
    'port': os.getenv('DB_PORT', '3306'),
    'user': os.getenv('DB_USER', 'root'),
    'password': os.getenv('DB_PASSWORD', 'password'),
    'database': os.getenv('DB_NAME', 'itemsdb')
}

def get_db_connection():
    try:
        connection = mysql.connector.connect(**DB_CONFIG)
        return connection
    except Error as e:
        print(f"Error connecting to MySQL: {e}")
        return None

def init_db():
    connection = get_db_connection()
    if connection:
        try:
            cursor = connection.cursor()
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS items (
                    id INT AUTO_INCREMENT PRIMARY KEY,
                    name VARCHAR(255) NOT NULL,
                    description TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
            connection.commit()
            cursor.close()
        except Error as e:
            print(f"Error creating table: {e}")
        finally:
            connection.close()

@app.route('/')
def index():
    connection = get_db_connection()
    items = []
    if connection:
        try:
            cursor = connection.cursor(dictionary=True)
            cursor.execute("SELECT * FROM items ORDER BY created_at DESC")
            items = cursor.fetchall()
            cursor.close()
        except Error as e:
            print(f"Error fetching items: {e}")
        finally:
            connection.close()

    return render_template('index.html', items=items)

@app.route('/add', methods=['POST'])
def add_item():
    name = request.form.get('name')
    description = request.form.get('description')

    if name:
        connection = get_db_connection()
        if connection:
            try:
                cursor = connection.cursor()
                cursor.execute(
                    "INSERT INTO items (name, description) VALUES (%s, %s)",
                    (name, description)
                )
                connection.commit()
                cursor.close()
            except Error as e:
                print(f"Error adding item: {e}")
            finally:
                connection.close()

    return redirect(url_for('index'))

@app.route('/health')
def health():
    return {'status': 'healthy'}, 200

if __name__ == '__main__':
    init_db()
    app.run(host='0.0.0.0', port=5000, debug=True)
