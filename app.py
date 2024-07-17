from flask import Flask, request, jsonify
import json
from flask_mysqldb import MySQL
import hashlib
app = Flask(__name__)

app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD'] = 'Nksk12@3'
app.config['MYSQL_DB'] = 'products'

mysql = MySQL(app)



def create_table():
     cur = mysql.connection.cursor()
     cur.execute("CREATE TABLE IF NOT EXISTS Users (id INT AUTO_INCREMENT PRIMARY KEY ,username VARCHAR(50) UNIQUE NOT NULL, password VARCHAR(50) NOT NULL, role VARCHAR(50))")
     mysql.connection.commit()
     cur.close()

with app.app_context():
    create_table()    

def get_user_data(id): 
    cur = mysql.connection.cursor()
    cur.execute('''SELECT id,username,role FROM Users WHERE id = %s''', (id,))
    data = cur.fetchall()
    cur.close()
    if not data:
        return "not found"
    return jsonify(data), 200
  
@app.route('/')
def getResult():
   try:
    cur = mysql.connection.cursor()
    cur.execute("SELECT id,username,role FROM Users")
    data = cur.fetchall()
    print(data)
    cur.close()
    return jsonify(data)
   except Exception as e:
        return jsonify({'error': str(e)}), 500
   


@app.route('/data/<int:id>')
def get_user(id):
  try:  
    return get_user_data(id)
  except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/add',methods = ['POST'])
def addUser():
    try:
        data = request.json
        if not data or not all(key in data for key in ( 'username', 'password', 'role')):
                return jsonify({'error': 'Missing data'}), 400
        cur = mysql.connection.cursor()
        username = data['username']
        hashed_password = hashlib.md5(data['password'].encode('utf-8')).hexdigest()
        role = data['role']
        data['password'] = hashed_password
        cur.execute('''INSERT INTO Users (username,password,role) VALUES (%s, %s, %s)''', (username,hashed_password,role))
        mysql.connection.commit()
        cur.close()
        return jsonify(data), 201
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/update/<int:id>', methods = ['PUT'] )
def updateUser(id):
    try:
        data = request.json
        if not data or not all(key in data for key in ('username', 'role')):
            return jsonify({'error': 'Missing data'}), 400
        
        value = get_user_data(id)
        
        if value == "not found" : 
            return jsonify({'error': 'Missing user'}), 404
        
        cur = mysql.connection.cursor()

        username = data['username']
        role = data['role']
        cur.execute('''UPDATE Users SET username = %s, role = %s WHERE id = %s''', (username,role,id))
        mysql.connection.commit()
        cur.close()
        return jsonify({'message': 'Data updated successfully'})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/delete/<int:id>',methods=["DELETE"])
def deleteUser(id):
    
    try:
        cur = mysql.connection.cursor()
        cur.execute('''DELETE FROM Users WHERE id = %s''', (id,))
        mysql.connection.commit()
        cur.close()
        return jsonify({'message': 'Data deleted successfully'})
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500
    


