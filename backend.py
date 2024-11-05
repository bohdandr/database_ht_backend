import random
import string
from flask import Flask, request, jsonify
from flask_cors import CORS
import mysql.connector
from mysql.connector import Error

app = Flask(__name__)
CORS(app)  # Дозволити CORS для всіх доменів

# Функція для підключення до бази даних
def connect_to_db():
    return mysql.connector.connect(
        user='admin',
        password='Sygnivka12',
        host='databaseht.cjym424s2ike.eu-north-1.rds.amazonaws.com',
        database='databaseht'
    )


# Створення таблиці тасків
@app.route('/create_table', methods=['POST'])
def create_table():
    conn = None
    cursor = None
    try:
        conn = connect_to_db()
        cursor = conn.cursor()
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS task (
                id INT AUTO_INCREMENT PRIMARY KEY,
                ip_address VARCHAR(45) NOT NULL,
                description TEXT NOT NULL
            )
        """)
        return jsonify({"message": "Таблицю 'task' успішно створено!"}), 201
    except Error as err:
        return jsonify({"error": str(err)}), 500
    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()

# Додавання нового таску
@app.route('/tasks', methods=['POST'])
def add_task():
    data = request.json
    ip_address = data.get('ip_address')
    description = data.get('description')
    
    conn = connect_to_db()
    cursor = conn.cursor()
    cursor.execute("INSERT INTO task (ip_address, description) VALUES (%s, %s)", (ip_address, description))
    conn.commit()
    cursor.close()
    conn.close()
    return jsonify({"message": "Таск успішно додано!"}), 201

# Отримання всіх тасків
@app.route('/tasks', methods=['GET'])
def get_all_tasks():
    conn = connect_to_db()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM task")
    tasks = cursor.fetchall()
    cursor.close()
    conn.close()
    
    # Форматування даних для відповіді
    tasks_list = [{"id": task[0], "ip_address": task[1], "description": task[2]} for task in tasks]
    
    return jsonify(tasks_list), 200

# Видалення всіх тасків
@app.route('/tasks', methods=['DELETE'])
def delete_all_tasks():
    conn = None
    cursor = None
    try:
        conn = connect_to_db()
        cursor = conn.cursor()
        cursor.execute("DELETE FROM task")
        conn.commit()  # Підтвердження змін
        return jsonify({"message": "Усі таски успішно видалено!"}), 200
    except Error as err:
        return jsonify({"error": str(err)}), 500
    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()

# Додавання випадкового таску для тестування
@app.route('/add_random_task', methods=['POST'])
def add_random_task():
    # Генерація випадкових значень для IP-адреси та опису таску
    ip_address = '.'.join(str(random.randint(0, 255)) for _ in range(4))
    description = ''.join(random.choices(string.ascii_letters + string.digits, k=20))
    
    try:
        conn = connect_to_db()
        cursor = conn.cursor()
        cursor.execute("INSERT INTO task (ip_address, description) VALUES (%s, %s)", (ip_address, description))
        conn.commit()
        return jsonify({"message": "Випадковий таск успішно додано!", "ip_address": ip_address, "description": description}), 201
    except Error as err:
        return jsonify({"error": str(err)}), 500
    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()


@app.route('/hello', methods=['GET'])
def hello():
    return jsonify({"message": "Hello, World!"}), 200

if __name__ == '__main__':
    with app.app_context():
        add_random_task()  
    app.run(host='0.0.0.0', port=5000)
