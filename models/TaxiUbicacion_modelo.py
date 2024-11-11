from flask_sqlalchemy import SQLAlchemy 
from datetime import datetime, timezone

db = SQLAlchemy()

# definición del modelo TaxiUbicación 
class TaxiUbicacion(db.Model):
  __tablename__ = 'trajectories'
  id = db.Column(db.Integer, primary_key=True)
  taxi_id = db.Column(db.Integer, db.ForeignKey('taxis.id'), nullable=False)
  latitud = db.Column(db.Float, nullable=False) 
  longitud = db.Column(db.Float, nullable=False)
  timestamp = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc), nullable=False)

  taxi = db.relationship('Taxi', backref=db.backref('ubicaciones', lazy=True))
