import uuid
from app import db
from .base_model import BaseModel  # Inherit from BaseModel

class Amenity(BaseModel):  # Inherit from BaseModel
    __tablename__ = 'amenities'

    # UUID primary key
    id = db.Column(db.String(36), primary_key=True, default=str(uuid.uuid4), unique=True)
    name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.String(512))

    def __repr__(self):
        return f'<Amenity {self.name}>'
