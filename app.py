from flask import Flask, request
from flask_restx import Api, Resource, fields
from models import db, init_app
from models.taxis_modelo import Taxi
from models.TaxiUbicacion_modelo import TaxiUbicacion
from dotenv import load_dotenv
import os
from datetime import datetime, timezone

# Carga las variables del archivo .env
load_dotenv()

app = Flask(__name__)
api = Api(app, version='1.0', title='API de Taxis',
          description='API para gestionar taxis y consultar ubicaciones')

# Define un namespace para organizar las rutas en Swagger
ns = api.namespace('taxis', description='Operaciones relacionadas con taxis')
ubicacion_ns = api.namespace('ubicaciones', description='Operaciones relacionadas con ubicaciones de taxis')

# Configuración de la base de datos usando la variable de entorno
app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('DATABASE_URI')

# Inicializa la base de datos con la aplicación
init_app(app)

# Modelo de taxi para Swagger
taxi_model = api.model('Taxi', {
    'id': fields.Integer(description='ID del taxi'),
    'plate': fields.String(description='Placa del taxi')
})

ubicacion_model = api.model('Ubicacion', {
   'latitud': fields.Float(description='Latitud del taxi'),
   'longitud': fields.Float(description='Longitud del taxi'), 
   'timestamp': fields.DateTime(description='Fecha y hora de la ubicación')
})

# Definición de endpoints
@ns.route('/')
class TaxisResource(Resource):
    @ns.doc(params={'plate': 'Número de placa', 'page': 'Número de página', 'limit': 'Límite de resultados'})
    @ns.response(200, 'Success', [taxi_model])
    @ns.response(404, 'No se encontraron taxis')
    def get(self):
        """Obtiene una lista de taxis con opciones de filtro y paginación"""
        try:
            plate = request.args.get('plate')
            page = request.args.get('page', default=1, type=int)
            limit = request.args.get('limit', default=10, type=int)

            query = Taxi.query

            if plate:
                query = query.filter(Taxi.plate.ilike(f"%{plate}%"))

            taxis_paginated = query.paginate(page=page, per_page=limit, error_out=False)

            if not taxis_paginated.items:
                return {"mensaje": "No se encontraron taxis"}, 200

            taxis_data = [{"id": taxi.id, "plate": taxi.plate} for taxi in taxis_paginated.items]
            return taxis_data, 200

        except Exception as e:
            return {"error": str(e)}, 500
        
@ubicacion_ns.route('/<int:taxi_id>/ubicacion')
@ubicacion_ns.param('fecha', 'Fecha en formato YYYY-MM-DD')
class TaxiUbicacionResource(Resource):
    @ubicacion_ns.doc(params={'fecha': 'Fecha en formato YYYY-MM-DD'})
    @ubicacion_ns.response(200, 'Success', [ubicacion_model])
    @ubicacion_ns.response(404, 'No se encontraron ubicaciones para el taxi')
    def get(self, taxi_id):
        """Obtiene la ubicación de un taxi por ID y fecha"""
        try:
            fecha_str = request.args.get('fecha')
            if not fecha_str:
                return {"mensaje": "Fecha no proporcionada o en formato incorrecto. Se requiere formato YYYY-MM-DD."}, 400
            
            fecha = datetime.strptime(fecha_str, '%Y-%m-%d').date()
                
            ubicaciones = TaxiUbicacion.query.filter(
                TaxiUbicacion.taxi_id == taxi_id,
                db.func.date(TaxiUbicacion.timestamp) == fecha
            ).all()
            
            if not ubicaciones:
                return {"mensaje": "No se encontraron ubicaciones para el taxi en la fecha especificada"}, 404
            
            ubicaciones_data = [
                {"latitud": ubicacion.latitud, "longitud": ubicacion.longitud, "timestamp": ubicacion.timestamp.strftime('%Y-%m-%d %H:%M:%S')}
                for ubicacion in ubicaciones
            ]
            return ubicaciones_data, 200

        except Exception as e:
            return {"error": str(e)}, 500

# Ruta de prueba
@ns.route('/bienvenida')
class BienvenidaResource(Resource):
    def get(self):
        """Ruta de bienvenida"""
        response = {"mensaje": "Bienvenido a la API de taxis"}
        return response, 200

# Registra el namespace
api.add_namespace(ns, path='/taxis')
api.add_namespace(ubicacion_ns, path='/ubicaciones')

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True)