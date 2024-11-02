from flask import Flask, request, jsonify
from models import db, init_app  # importa init_app
from models.taxis_modelo import Taxi  # Importa solo el modelo
from dotenv import load_dotenv
import os

# Carga las variables del archivo .env
load_dotenv()

app = Flask(__name__)

# Configuración de la base de datos usando la variable de entorno
app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('DATABASE_URI')

# Inicializa la base de datos con la aplicación
init_app(app)

# Definición de endpoints
@app.route('/taxis', methods=['GET'])
def get_taxis():
    try:
        # Obtener parámetros de la solicitud
        plate = request.args.get('plate')  # Parámetro de placa
        page = request.args.get('page', default=1, type=int)  # Página (por defecto es 1)
        limit = request.args.get('limit', default=10, type=int)  # Límite de resultados (por defecto es 10)

        # Construir la consulta base
        query = Taxi.query 

        # Filtrar por 'plate' si se proporciona
        if plate:
            # Usar LIKE para coincidencias parciales
            query = query.filter(Taxi.plate.ilike(f"%{plate}%"))

        # Aplicar paginación
        taxis_paginated = query.paginate(page=page, per_page=limit, error_out=False)

        # Verificar si hay elementos
        if not taxis_paginated.items:
            return jsonify({"mensaje": "No se encontraron taxis"}), 200

        # Construir respuesta
        taxis_data = [{"id": taxi.id, "plate": taxi.plate} for taxi in taxis_paginated.items]
        return jsonify(taxis_data), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500  # Retorna el error como respuesta en caso de excepción

# Ruta de prueba
@app.route('/', methods=['GET'])
def index():
    response = {"mensaje": "Bienvenido a la Api de taxis"}
    return jsonify(response), 200

if __name__ == '__main__':
    with app.app_context():
        db.create_all()  # Esto crea las tablas en la base de datos
    app.run(debug=True)