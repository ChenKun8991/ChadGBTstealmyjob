from flask import Flask, render_template, url_for, request, redirect
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql://root:password123@localhost/mysql'


mysql = SQLAlchemy(app)

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