from flask import Flask, request, jsonify
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy import Column, Integer, String
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy_serializer import SerializerMixin

app = Flask(__name__)
username = 'root'
password = 'Khyati123'
host = 'localhost'
port = 3306
DB_NAME = 'products'

engine = create_engine(f"mysql://{username}:{password}@{host}:{port}/{DB_NAME}")
Session = sessionmaker(bind=engine)
session = Session()

Base = declarative_base()

class User(Base, SerializerMixin):
    __tablename__ = "Users"
    id = Column(Integer, primary_key=True)
    username = Column(String, unique=True, nullable=False)
    password = Column(String, nullable=False)
    role = Column(String)

# Create the table in the database
Base.metadata.create_all(engine)

@app.route('/add', methods=['POST'])
def add_user():
    try:
        data = request.json
        if not data or not all(key in data for key in ('username', 'password', 'role')):
            return jsonify({'error': 'Missing data'}), 400
        
        new_user = User(username=data['username'], password=data['password'], role=data['role'])
        session.add(new_user)
        session.commit()

        return jsonify(data), 201
    
    except Exception as e:
        session.rollback()  # Rollback the session in case of an error
        return jsonify({'error': str(e)}), 500

@app.route('/')
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

@app.route('/data/<int:id>')
def get_user_with_id(id):
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

@app.route('/update/<int:id>', methods=['PUT'])
def update_user(id):
    try:
        user = session.query(User).get(id)
        if not user:
            return jsonify({'error': 'User not found'}), 404
        
        data = request.json
        user.username = data['username']
        user.role = data['role']
        session.commit()

        return jsonify({'msg': 'User update successful'}), 200
    
    except Exception as e:
        session.rollback()
        return jsonify({'error': str(e)}), 500

@app.route('/delete/<int:id>', methods=['DELETE'])
def delete_user(id):
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

if __name__ == '__main__':
    app.run(debug=True)


    


