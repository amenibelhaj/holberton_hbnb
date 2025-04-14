# app/models/amenity.py

import uuid
from app import db
from .base_model import BaseModel  # Inherit from BaseModel

class Amenity(BaseModel):  # Inherit from BaseModel
    __tablename__ = 'amenities'
    
    name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.String(512))

    def __repr__(self):
        return f'<Amenity {self.name}>'
