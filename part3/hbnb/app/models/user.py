from app import db
from flask_bcrypt import Bcrypt
from app.models.base_model import BaseModel
import re
from datetime import datetime


bcrypt = Bcrypt()

class User(BaseModel):
    __tablename__ = 'users'

    first_name = db.Column(db.String(50), nullable=False)
    last_name = db.Column(db.String(50), nullable=False)
    email = db.Column(db.String(120), nullable=False, unique=True)
    password_hash = db.Column(db.String(128), nullable=False)
    is_admin = db.Column(db.Boolean, default=False)

    # One-to-many relationship with Place
    places = db.relationship('Place', backref='owner', lazy=True)

    # One-to-many relationship with Review
    reviews = db.relationship('Review', backref='author', lazy=True)

    def __init__(self, first_name, last_name, email, password, is_admin=False):
        self.first_name = first_name
        self.last_name = last_name
        self.email = email
        self.set_password(password)  # Automatically sets the password hash
        self.is_admin = is_admin
        self.validate_user()
        
        # Call save() to ensure created_at and updated_at are set
        self.save()

    def set_password(self, password):
        """Set the password hash, this is where we encrypt the password."""
        self.password_hash = bcrypt.generate_password_hash(password).decode('utf-8')

    def check_password(self, password):
        """Check if the provided password matches the stored password hash."""
        return bcrypt.check_password_hash(self.password_hash, password)

    def validate_user(self):
        """Validate the user data."""
        if not self.first_name:
            raise ValueError("First name is required")
        if not self.last_name:
            raise ValueError("Last name is required")
        if not self.email:
            raise ValueError("Email is required")
        if not self.password_hash:
            raise ValueError("Password is required")
        # Check for valid email format using regex
        email_regex = r'^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z]{2,}$'
        if not re.match(email_regex, self.email):
            raise ValueError("Invalid email format")
    def save(self):
        """Update the updated_at timestamp whenever the object is modified"""
        self.updated_at = datetime.now()
        db.session.add(self)
        db.session.commit()  # Commit the transaction so that the `id` is set
    def to_dict(self):
        """Convert the User object to a dictionary."""
        return {
            'id': self.id,
            'first_name': self.first_name,
            'last_name': self.last_name,
            'email': self.email,
            'is_admin': self.is_admin
        }
    