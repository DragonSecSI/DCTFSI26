from flask import Flask, request, render_template_string
import sqlite3
import os
import time

import mysql.connector

app = Flask(__name__)


FLAG = os.environ.get('FLAG')

sqlite_conn = sqlite3.connect('./db/foods.db', check_same_thread=False)
sqlite_conn.execute('CREATE TABLE IF NOT EXISTS food (id INTEGER PRIMARY KEY, name TEXT)')
sqlite_conn.execute('CREATE TABLE IF NOT EXISTS secret_union (id INT AUTO_INCREMENT PRIMARY KEY, secret VARCHAR(255))')
sqlite_conn.execute('INSERT INTO secret_union (secret) VALUES ("I like cookies")')
sqlite_conn.commit()


for i in range(15):
    try:
        mysql_conn = mysql.connector.connect(
            user=os.environ.get('MYSQL_USER', 'root'),
            password=os.environ.get('MYSQL_PASSWORD', 'password'),
            host=os.environ.get('MYSQL_HOST', 'db'),
            database=os.environ.get('MYSQL_DATABASE', 'foods')
        )
        break
    except mysql.connector.errors.InterfaceError:
        print("Waiting for MySQL to be ready...")
        time.sleep(5)
else:
    raise Exception("Could not connect to MySQL after multiple attempts")

mysql_cursor = mysql_conn.cursor()
mysql_cursor.execute('CREATE TABLE IF NOT EXISTS food (id INT AUTO_INCREMENT PRIMARY KEY, name VARCHAR(255))')
mysql_cursor.execute('CREATE TABLE IF NOT EXISTS flag (id INT AUTO_INCREMENT PRIMARY KEY, secret VARCHAR(255))')


foods = ['Apple', 'Banana', 'Carrot', 'Donut', 'Eggplant', 'Fig', 'Grape', 'Honeydew']


mysql_cursor.execute('SELECT COUNT(*) FROM food')
if mysql_cursor.fetchone()[0] == 0:
    for food in foods:
        mysql_cursor.execute('INSERT INTO food (name) VALUES (%s)', (food,))
    mysql_conn.commit()

mysql_cursor.execute('INSERT INTO flag (secret) VALUES (%s)', (FLAG,))
mysql_conn.commit()


HTML = '''
<form method="get">
    <input name="q" placeholder="Search food">
    <button type="submit">Search</button>
</form>
<ul>
{% for item in results %}
    <li>{{item}}</li>
{% endfor %}
</ul>
'''

@app.route('/', methods=['GET'])
def search():
    q = request.args.get('q', '')
    query_sqlite = "SELECT name FROM food WHERE name LIKE '" + q + "'"
    explain_cur = sqlite_conn.execute("EXPLAIN QUERY PLAN " + query_sqlite)
    explain_rows = explain_cur.fetchall()
    for row in explain_rows:
        if "union" in str(row).lower():
            return "<h1>SQL INJECTION DETECTED</h1>"

    mysql_cursor.execute("SELECT name FROM food WHERE name LIKE '" + q + "'")
    test = mysql_cursor.fetchall()
    results = [r[0] for r in test]
    return render_template_string(HTML, results=results)

if __name__ == '__main__':
    app.run(host="0.0.0.0", port=8000)
