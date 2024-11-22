import pytest
from datetime import datetime, timezone
from app import app, db
from models.taxis_modelo import Taxi
from models.trajectory_modelo import Trajectory

@pytest.fixture
def client():
    app.config['TESTING'] = True
    with app.app_context():
        #db.create_all()  # Crear tablas en la base de datos de prueba
        yield app.test_client()  # Proporciona el cliente de prueba
        db.session.remove()
        #db.drop_all()  # Elimina tablas después de las pruebas
def test_get_trajectories(client):
    with app.app_context():
        # Agregar datos de prueba
        taxi = Taxi(plate="TEST123")
        db.session.add(taxi)
        db.session.commit()

        trayectoria = Trajectory(
            taxi_id=taxi.id,
            latitude=10.0,
            longitude=20.0,
            date=datetime.now(timezone.utc)  # Usar 'date' en lugar de 'timestamp'
        )
        db.session.add(trayectoria)
        db.session.commit()

        # Realizar la solicitud para obtener trayectorias
        response = client.get(f'/taxis/{taxi.id}/trayectoria?fecha={datetime.now().date()}')
        data = response.get_json()

        # Verificar respuesta
        assert response.status_code == 200
        assert data is not None
        assert "latitud" in data[0]
        assert "longitud" in data[0]
        assert "timestamp" in data[0] 

def test_get_trajectories_no_data(client):
    # Solicitud para un taxi o fecha sin trayectorias
    response = client.get('/taxis/999/trayectoria?fecha=2024-11-11')
    data = response.get_json()

    # Verificar que el JSON no sea None antes de usarlo
    assert response.status_code == 404
    assert data is not None, "Expected a JSON response but got None"
    assert data.get("error") == "No se encontraron trayectorias"