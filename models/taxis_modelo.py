from models import db
from sqlalchemy import Column, Integer, String
from .trajectory_modelo import Trajectory  # Importa la clase Trajectory

class Taxi(db.Model):
    __tablename__ = 'taxis'

    # Definición de las columnas
    id = db.Column(db.Integer, primary_key=True)
    plate = db.Column(db.String, nullable=False)

    # Relación con las trayectorias (uno a muchos)
    trajectories = db.relationship('Trajectory', back_populates='taxi')

    def __repr__(self):
        return f'<Taxi {self.plate}>'