import pytest
from app import app, db
from models.taxis_modelo import Taxi

@pytest.fixture
def client():
    # Configura la aplicación en modo de prueba
    app.config['TESTING'] = True
    app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://usuario:contraseña@localhost:puerto/nombre_base_de_datos'  # Cambia esto por la URI de tu base de datos real
    
    with app.test_client() as client:
        with app.app_context():
            # Omite db.create_all() y la inserción de datos de prueba para usar datos reales.
            yield client  # Client se usará en cada prueba

def test_get_taxis_without_params(client):
    """Prueba el endpoint sin parámetros."""
    response = client.get('/taxis')
    assert response.status_code == 200
    data = response.get_json()
    assert len(data) > 0  # Asegúrate de que devuelva taxis

def test_get_taxis_with_plate_param(client):
    """Prueba el endpoint con el parámetro plate existente."""
    response = client.get('/taxis?plate=PAOF-6727')  # Usa una placa que ya existe
    assert response.status_code == 200  # Verifica que el código de estado sea 200
    data = response.get_json()  # Obtén los datos en formato JSON

    # Verifica la longitud del campo 'results'
    assert len(data['results']) == 1  # Asegúrate de que devuelva exactamente un resultado
    assert data['results'][0]['plate'] == 'PAOF-6727'  # Verifica que la placa coincida

def test_get_taxis_with_partial_plate_param(client):
    """Prueba el endpoint con una coincidencia parcial en plate."""
    response = client.get('/taxis?plate=CNCJ')
    assert response.status_code == 200
    data = response.get_json()
    print(data)  # Esto te ayudará a identificar la estructura de la respuesta

def test_get_taxis_with_page_and_limit_params(client):
    """Prueba el endpoint con los parámetros page y limit."""
    response = client.get('/taxis?page=1&limit=2')
    assert response.status_code == 200
    data = response.get_json()
    
    results = data.get('results', [])  # Obtén los resultados
    assert len(results) <= 2  # Asegúrate de que se respete el límite

def test_get_taxis_with_invalid_plate(client):
    """Prueba el endpoint con un parámetro plate que no existe."""
    response = client.get('/taxis?plate=ZZZ999')  # Usa una placa que no existe
    assert response.status_code == 404
    data = response.get_json()
    assert data == {"mensaje": "No se encontraron taxis."}  # Espera el mensaje
