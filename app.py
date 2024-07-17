from flask import Flask, request, jsonify
from dotenv import  dotenv_values
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy import Column, Integer, String
from sqlalchemy.ext.declarative import declarative_base
import hashlib

app = Flask(__name__)
config = dotenv_values(".env")

username = config['USERNAME']
password = config['PASSWORD']
host = 'localhost'
port = 3306
DB_NAME = config['DB_NAME']

engine = create_engine(f"mysql://{username}:{password}@{host}:{port}/{DB_NAME}")
Session = sessionmaker(bind=engine)
session = Session()

Base = declarative_base()

class User(Base):
    __tablename__ = "Users"
    id = Column(Integer, primary_key=True)
    username = Column(String(50), unique=True, nullable=False)
    password = Column(String(50), nullable=False)
    role = Column(String(50))

# Create the table in the database
Base.metadata.create_all(engine)

def getPassword(id):
    user = session.query(User).get(id)
    return user.password

@app.route('/user/add', methods=['POST'])
def add_user():
    try:
        data = request.json
        if not data or not all(key in data for key in ('username', 'password', 'role')):
            return jsonify({'error': 'Missing data'}), 400
        
        hashed_password = hashlib.md5(data['password'].encode('utf-8')).hexdigest()
        data['password'] = hashed_password
        new_user = User(username=data['username'], password=hashed_password, role=data['role'])
        session.add(new_user)
        session.commit()

        return jsonify(data), 201
    
    except Exception as e:
        session.rollback()  # Rollback the session in case of an error
        return jsonify({'error': str(e)}), 500

@app.route('/user')
def get_users():
    try:
        users = session.query(User).all()
        users_dict = []
        for user in users:
            user_data = {
                'id': user.id,
                'username': user.username,
                'role': user.role
            }
            users_dict.append(user_data)
        return jsonify(users=users_dict)
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/user/<int:id>', methods = ['GET', "PUT" ,'DELETE'])
def perform_operation(id):
    if request.method == "GET":
        try:
            user = session.query(User).get(id)
            if user:
                user_data = {
                    'id': user.id,
                    'username': user.username,
                    'role': user.role
                }
                return jsonify(user_data)
            else:
                return jsonify({'error': 'User not found'}), 404
        
        except Exception as e:
            return jsonify({'error': str(e)}), 500

    elif request.method == "PUT" :
        try:
            user = session.query(User).get(id)
            if not user:
                return jsonify({'error': 'User not found'}), 404
            
            data = request.json
            print(data)
            if 'username' in data :
                user.username = data['username']

            if 'new_password' in data:    
                 if 'old_password' in data:
                     hashed_old = hashlib.md5(data['old_password'].encode('utf-8')).hexdigest()
                     if(hashed_old == getPassword(id)):
                         user.password = hashlib.md5(data['new_password'].encode('utf-8')).hexdigest()
                         print("success")
                     else:
                         return jsonify({'error' : 'Wrong password'})    
                     
            if 'role' in data :    
                user.role = data['role']
            
            session.commit()
            return jsonify({'msg': 'User update successful'}), 200
    
        except Exception as e:
            session.rollback()
            return jsonify({'error': str(e)}), 500
        
    else:
        try:
            user = session.query(User).get(id)
            if not user:
                return jsonify({'error': 'User not found'}), 404
            
            session.delete(user)
            session.commit()

            return jsonify({'msg': 'User deleted successfully'}), 200
    
        except Exception as e:
            session.rollback()
            return jsonify({'error': str(e)}), 500


