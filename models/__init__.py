from flask_sqlalchemy import SQLAlchemy

# Inicializa la base de datos
db = SQLAlchemy()

# Importa tus modelos para asegurarte de que se registren con SQLAlchemy
from .taxis_modelo import Taxi
from .trajectory_modelo import Trajectory