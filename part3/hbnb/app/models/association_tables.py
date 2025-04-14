from app import db

# Association Table for Many-to-Many Relationship between Place and Amenity
place_amenity_association = db.Table(
    'place_amenity', db.Model.metadata,
    db.Column('place_id', db.String(36), db.ForeignKey('places.id'), primary_key=True),
    db.Column('amenity_id', db.String(36), db.ForeignKey('amenities.id'), primary_key=True)
)
