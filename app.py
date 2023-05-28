from flask import Flask
from flask_mysqldb import MySQL

app = Flask(__name__)
app.config['MYSQL_HOST'] = 'localhost'  # MySQL server host
app.config['MYSQL_USER'] = 'root'  # MySQL username
app.config['MYSQL_PASSWORD'] = 's9927714i'  # MySQL password
app.config['MYSQL_DB'] = 'mydatabase'  # MySQL database name

mysql = MySQL(app)

@app.route('/')
def index():
    # Perform a MySQL query
    cur = mysql.connection.cursor()
    cur.execute('SELECT * FROM users')
    results = cur.fetchall()
    cur.close()
    
    # Process the query results
    output = ''
    for row in results:
        output += f'ID: {row[0]}, Name: {row[1]}, Email: {row[2]}\n'
        
    return output

if __name__ == '__main__':
    app.run()