from app.models.review import Review
from app import db
from app.persistence.repository import SQLAlchemyRepository

class ReviewRepository(SQLAlchemyRepository):
    def __init__(self):
        super().__init__(Review)

    def get_by_place(self, place_id):
        # Query the reviews table to get all reviews for a given place
        return db.session.query(Review).filter(Review.place_id == place_id).all()

    def get_review_by_user_and_place(self, user_id, place_id):
        # Check if a review already exists for the user on the specified place
        return self.model.query.filter_by(user_id=user_id, place_id=place_id).first()
