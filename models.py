from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

db = SQLAlchemy()

class User(db.Model):
    __tablename__ = 'users'

    user_id = db.Column(db.Integer, primary_key=True)
    user_nombre = db.Column(db.String(80), nullable=False)
    user_apellidos = db.Column(db.String(120), nullable=False)
    user_email = db.Column(db.String(120), unique=True, nullable=False)
    user_contrasena = db.Column(db.String(128), nullable=False)

    tasks = db.relationship('Task', backref='user', lazy=True)

class Task(db.Model):
    __tablename__ = 'tasks'

    task_id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.user_id'), nullable=False)
    task_titulo = db.Column(db.String(120), nullable=False)
    task_desc = db.Column(db.Text)
    task_fechahora = db.Column(db.DateTime)
    task_completo = db.Column(db.Boolean, default=False)
    task_activa = db.Column(db.Boolean, default=True)
    task_creado = db.Column(db.DateTime, default=datetime.utcnow)
    task_actualizado = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
