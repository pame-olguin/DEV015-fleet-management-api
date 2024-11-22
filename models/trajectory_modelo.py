from models import db
from sqlalchemy import Column, Integer, Float, Date, ForeignKey  # Cambié DateTime por Date
from datetime import datetime

class Trajectory(db.Model):
    __tablename__ = 'trajectories'

    # Definición de las columnas
    id = db.Column(db.Integer, primary_key=True)
    taxi_id = db.Column(db.Integer, db.ForeignKey('taxis.id'), nullable=False)  # Clave foránea a 'taxis'
    date = db.Column(db.Date, nullable=False)  # Fecha de la trayectoria
    latitude = db.Column(db.Float, nullable=False)  # Latitud
    longitude = db.Column(db.Float, nullable=False)  # Longitud

    # Relación con el modelo Taxi (muchos a uno)
    taxi = db.relationship('Taxi', back_populates='trajectories')

    # Método para convertir el objeto en un diccionario JSON
    def to_dict(self):
        return {
            "latitude": self.latitude,
            "longitude": self.longitude,
            "date": self.date.isoformat()  # Formato ISO para compatibilidad en JSON
        }