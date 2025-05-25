from flask import Flask, request
from flask_restx import Api, Resource, fields
from datetime import datetime
from models import db, User, Task
import os

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('DATABASE_URL')  # PostgreSQL
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db.init_app(app)

api = Api(app, version='1.0', title='API de Gestión de Tareas',
          description='Documentación interactiva con Swagger usando Flask-RESTX')

auth_ns = api.namespace('auth', description='Operaciones de autenticación')
tasks_ns = api.namespace('tasks', description='Operaciones con tareas')

# ------------------ MODELOS PARA LA DOCUMENTACIÓN ------------------ #

user_model = api.model('Usuario', {
    'user_nombre': fields.String(required=True),
    'user_apellidos': fields.String(required=True),
    'user_email': fields.String(required=True),
    'user_contrasena': fields.String(required=True)
})

login_model = api.model('Login', {
    'user_email': fields.String(required=True),
    'user_contrasena': fields.String(required=True)
})

task_model = api.model('Tarea', {
    'user_id': fields.Integer(required=True),
    'task_titulo': fields.String(required=True),
    'task_desc': fields.String,
    'task_fechahora': fields.String  # ISO format
})

update_task_model = api.model('ActualizarTarea', {
    'task_titulo': fields.String,
    'task_desc': fields.String,
    'task_fechahora': fields.String,
    'task_completo': fields.Boolean
})

# ------------------ INICIALIZAR DB ------------------ #
with app.app_context():
    db.create_all()

# ------------------ RUTAS ------------------ #

@auth_ns.route('/register')
class Register(Resource):
    @auth_ns.expect(user_model)
    def post(self):
        data = request.get_json()
        if User.query.filter_by(user_email=data['user_email']).first():
            return {'error': 'El email ya está registrado'}, 400

        nuevo_usuario = User(
            user_nombre=data['user_nombre'],
            user_apellidos=data['user_apellidos'],
            user_email=data['user_email'],
            user_contrasena=data['user_contrasena']
        )
        db.session.add(nuevo_usuario)
        db.session.commit()
        return {'message': 'Usuario registrado correctamente'}, 201


@auth_ns.route('/login')
class Login(Resource):
    @auth_ns.expect(login_model)
    def post(self):
        data = request.get_json()
        usuario = User.query.filter_by(user_email=data['user_email']).first()

        if not usuario:
            return {'error': 'Usuario no encontrado'}, 404

        if usuario.user_contrasena != data['user_contrasena']:
            return {'error': 'Contraseña incorrecta'}, 401

        return {
            'message': 'Inicio de sesión exitoso',
            'user_id': usuario.user_id,
            'user_nombre': usuario.user_nombre,
            'user_apellidos': usuario.user_apellidos,
            'user_email': usuario.user_email
        }, 200


@tasks_ns.route('/<int:user_id>')
class GetTasks(Resource):
    def get(self, user_id):
        tasks = Task.query.filter_by(user_id=user_id, task_activa=True).all()
        return [{
            'task_id': t.task_id,
            'task_titulo': t.task_titulo,
            'task_desc': t.task_desc,
            'task_fechahora': t.task_fechahora.isoformat() if t.task_fechahora else None,
            'task_completo': t.task_completo,
            'task_activa': t.task_activa,
            'task_creado': t.task_creado.isoformat(),
            'task_actualizado': t.task_actualizado.isoformat()
        } for t in tasks]


@tasks_ns.route('/')
class CreateTask(Resource):
    @tasks_ns.expect(task_model)
    def post(self):
        data = request.get_json()
        nueva_tarea = Task(
            user_id=data['user_id'],
            task_titulo=data['task_titulo'],
            task_desc=data.get('task_desc'),
            task_fechahora=datetime.fromisoformat(data['task_fechahora']) if data.get('task_fechahora') else None
        )
        db.session.add(nueva_tarea)
        db.session.commit()
        return {'message': 'Tarea creada correctamente'}, 201


@tasks_ns.route('/<int:task_id>')
class UpdateDeleteTask(Resource):
    @tasks_ns.expect(update_task_model)
    def put(self, task_id):
        tarea = Task.query.get_or_404(task_id)
        data = request.get_json()

        tarea.task_titulo = data.get('task_titulo', tarea.task_titulo)
        tarea.task_desc = data.get('task_desc', tarea.task_desc)
        if data.get('task_fechahora'):
            tarea.task_fechahora = datetime.fromisoformat(data['task_fechahora'])
        tarea.task_completo = data.get('task_completo', tarea.task_completo)
        db.session.commit()
        return {'message': 'Tarea actualizada correctamente'}

    def delete(self, task_id):
        tarea = Task.query.get_or_404(task_id)
        tarea.task_activa = False
        db.session.commit()
        return {'message': 'Tarea desactivada correctamente'}

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5001)
