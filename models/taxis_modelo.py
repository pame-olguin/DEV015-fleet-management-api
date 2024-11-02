from . import db  # Importa la instancia de db desde el módulo de models

# Definir el modelo Taxi
class Taxi(db.Model):
    __tablename__ = 'taxis'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)  # Clave primaria autoincremental
    plate = db.Column(db.String(20), nullable=False)

    def __repr__(self):
        return f'<Taxi {self.plate}>'