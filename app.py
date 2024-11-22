from flask import Flask, request, jsonify
from flask_restx import Api, Resource, fields
from flask_migrate import Migrate  # Importa Migrate
from models import db
from models.taxis_modelo import Taxi
from models.trajectory_modelo import Trajectory
from dotenv import load_dotenv
import os
from datetime import datetime
from sqlalchemy import func

# Carga las variables del archivo .env
load_dotenv()

app = Flask(__name__)
app.url_map.strict_slashes = False
api = Api(app, version='1.0', title='API de Taxis',
          description='API para gestionar taxis y consultar trayectorias')

# Configuración de la base de datos
app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('DATABASE_URI')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db.init_app(app)

# Configuración de Flask-Migrate
migrate = Migrate(app, db)  # Inicializa Flask-Migrate

# Modelos de Swagger
taxi_model = api.model('Taxi', {
    'id': fields.Integer(description='ID del taxi'),
    'plate': fields.String(description='Placa del taxi')
})

trajectory_model = api.model('Trajectory', {
    'latitud': fields.Float(description='Latitud del taxi'),
    'longitud': fields.Float(description='Longitud del taxi'),
    'timestamp': fields.DateTime(description='Fecha y hora de la ubicación')
})

# Namespace
taxis_ns = api.namespace('taxis', description='Operaciones relacionadas con taxis')

# Endpoint para listar taxis
@taxis_ns.route('/')
class TaxisResource(Resource):
    @taxis_ns.doc(params={'plate': 'Número de placa', 'page': 'Número de página', 'limit': 'Límite de resultados'})
    @taxis_ns.response(200, 'Success', [taxi_model])
    @taxis_ns.response(404, 'No se encontraron taxis')
    def get(self):
        """Obtiene una lista de taxis con opciones de filtro y paginación"""
        # Obtener parámetros de la solicitud
        plate = request.args.get('plate', '').strip()
        page = int(request.args.get('page', 1))
        limit = int(request.args.get('limit', 10))

        # Construir la consulta base
        query = db.session.query(Taxi)

        # Aplicar filtro por número de placa (si se proporciona)
        if plate:
            query = query.filter(Taxi.plate.ilike(f'%{plate}%'))

        # Paginación
        taxis = query.paginate(page=page, per_page=limit, error_out=False)

        # Verificar si hay resultados
        if not taxis.items:
            return {"mensaje": "No se encontraron taxis."}, 404

        # Formatear la respuesta
        result = [{'id': taxi.id, 'plate': taxi.plate} for taxi in taxis.items]

        return {
            'page': page,
            'total_pages': taxis.pages,
            'total_items': taxis.total,
            'results': result
        }, 200

# Endpoint para trayectorias
@taxis_ns.route('/<int:taxi_id>/trayectoria')
class TaxiTrajectoryResource(Resource):
    @taxis_ns.doc(params={'fecha': 'Fecha en formato YYYY-MM-DD'})
    @taxis_ns.response(200, 'Success', [trajectory_model])
    @taxis_ns.response(400, 'Fecha es requerida o formato inválido')
    @taxis_ns.response(404, 'No se encontraron trayectorias')
    def get(self, taxi_id):
        """Obtiene las trayectorias de un taxi por ID y fecha"""
        fecha_str = request.args.get('fecha')
        if not fecha_str:
            return {"error": "Fecha es requerida"}, 400

        try:
            fecha = datetime.strptime(fecha_str, '%Y-%m-%d').date()
        except ValueError:
            return {"error": "Formato de fecha inválido"}, 400

        trajectories = Trajectory.query.filter_by(taxi_id=taxi_id).filter(
            func.date(Trajectory.date) == fecha
        ).all()

        if not trajectories:
            return {"error": "No se encontraron trayectorias"}, 404

        return [{"latitud": t.latitude, "longitud": t.longitude, "timestamp": t.date.isoformat()} for t in trajectories], 200

# Registro del namespace
api.add_namespace(taxis_ns, path='/taxis')

# Inicialización de la base de datos y ejecución de la aplicación
if __name__ == '__main__':
    with app.app_context():
        db.create_all()  # Asegúrate de crear las tablas si no existen
        app.run(debug=True)