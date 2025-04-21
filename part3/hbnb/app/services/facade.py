from app import db
from app.models.user import User
from app.models.amenity import Amenity
from app.models.place import Place
from app.models.review import Review
from app.services.repositories.user_repository import UserRepository
from app.services.repositories.place_repository import PlaceRepository
from app.services.repositories.review_repository import ReviewRepository
from app.services.repositories.amenity_repository import AmenityRepository
import uuid

class HBnBFacade:
    """Class for facade methods"""
    
    def __init__(self):
        self.user_repo = UserRepository()
        self.place_repo = PlaceRepository()
        self.review_repo = ReviewRepository()
        self.amenity_repo = AmenityRepository()

    # Methods for User
    def create_user(self, user_data):
        user = User(**user_data)
        self.user_repo.add(user)
        return user
    
    def get_user(self, user_id):
        return self.user_repo.get(user_id)
    
    def get_user_by_email(self, email):
        return self.user_repo.get_user_by_email(email)
    
    def get_all_users(self):
        return self.user_repo.get_all()
    
    def update_user(self, user_id, user_data):
        user = self.user_repo.get(user_id)
        if not user:
            return None
        user.first_name = user_data.get('first_name', user.first_name)
        user.last_name = user_data.get('last_name', user.last_name)
        db.session.commit()
        return user
    
    def get_user_by_id(self, user_id):
        return self.user_repo.get_user_by_id(user_id)
    
    def save_user(self, user):
        """Saves a user object to the database."""
        db.session.add(user)
        db.session.commit()

    # Methods for Amenity
    def create_amenity(self, amenity_data):
        amenity_id = str(uuid.uuid4())
        amenity = Amenity(
            id=amenity_id,
            name=amenity_data['name'],
            description=amenity_data.get('description', None)
        )

        place_ids = amenity_data.get('associated_places', [])
        if place_ids:
            places = self.place_repo.get_places_by_ids(place_ids)
            amenity.associated_places.extend(places)

        self.amenity_repo.add(amenity)
        return amenity
    
    def get_amenity(self, amenity_id):
        return self.amenity_repo.get(amenity_id)
    
    def get_all_amenities(self):
        return self.amenity_repo.get_all()
    
    def update_amenity(self, amenity_id, amenity_data):
        amenity = self.amenity_repo.get(amenity_id)
        if not amenity:
            return None
        amenity.name = amenity_data.get('name', amenity.name)
        amenity.description = amenity_data.get('description', amenity.description)

        place_ids = amenity_data.get('associated_places', [])
        if place_ids is not None:
            new_places = self.place_repo.get_places_by_ids(place_ids)

        for place in new_places:
            if place not in amenity.associated_places:
                amenity.associated_places.append(place)

        to_remove = [place for place in amenity.associated_places if place.id not in place_ids]
        for place in to_remove:
            amenity.associated_places.remove(place)

        db.session.commit()
        return amenity
    
    def get_amenities_by_ids(self, amenity_ids):
        return self.amenity_repo.get_amenities_by_ids(amenity_ids)

    # Methods for Place
    def create_place(self, place_data):
        place = Place(
            title=place_data['title'],
            description=place_data['description'],
            price=place_data['price'],
            latitude=place_data['latitude'],
            longitude=place_data['longitude'],
            user_id=place_data['user_id']
        ) 

        amenity_ids = place_data.get('associated_amenities', [])
        if amenity_ids:
            amenities = self.amenity_repo.get_amenities_by_ids(amenity_ids)
            place.associated_amenities.extend(amenities)

        self.place_repo.add(place)
        return place
    
    def get_place(self, place_id):
        place = self.place_repo.get(place_id)
        if place:
            return {
                'place': {
                    'id': place.id,
                    'title': place.title,
                    'description': place.description,
                    'price': place.price,
                    'latitude': place.latitude,
                    'longitude': place.longitude,
                    'user_id': place.user_id 
                },
                'associated_amenities': [amenity.id for amenity in place.associated_amenities]
            }
        return None
    
    def get_all_places(self):
        places = self.place_repo.get_all()
        return [
            {
                'place': {
                    'id': place.id,
                    'title': place.title,
                    'description': place.description,
                    'price': place.price,
                    'latitude': place.latitude,
                    'longitude': place.longitude
                },
                'associated_amenities': [amenity.id for amenity in place.associated_amenities]
            }
            for place in places
        ]
    
    def update_place(self, place_id, place_data):
        place = self.place_repo.get(place_id)
        if not place:
            return None
        place.title = place_data.get('title', place.title)
        place.description = place_data.get('description', place.description)
        place.price = place_data.get('price', place.price)
        place.latitude = place_data.get('latitude', place.latitude)
        place.longitude = place_data.get('longitude', place.longitude)
        
        amenity_ids = place_data.get('associated_amenities', [])
        if amenity_ids is not None:
            new_amenities = self.amenity_repo.get_amenities_by_ids(amenity_ids)

        for amenity in new_amenities:
            if amenity not in place.associated_amenities:
                place.associated_amenities.append(amenity)

        to_remove = [amenity for amenity in place.associated_amenities if amenity.id not in amenity_ids]
        for amenity in to_remove:
            place.associated_amenities.remove(amenity)

        db.session.commit()
        return place
    
    def delete_place(self, place_id):
        if self.place_repo.delete(place_id):
            return True
        return False
    
    def get_places_by_price_range(self, min_price, max_price):
        return self.place_repo.get_by_price_range(min_price, max_price)

    def get_places_by_amenity(self, amenity_id):
        return self.place_repo.get_by_amenity(amenity_id)

    def get_places_by_owner(self, owner_id):
        return self.place_repo.get_by_owner(owner_id)
    
    def get_places_by_ids(self, place_ids):
        return self.place_repo.get_places_by_ids(place_ids)

    # Methods for Review
    def get_reviews_by_place(self, place_id):
        place = self.place_repo.get(place_id)
        if not place:
            raise ValueError("Place not found")
        reviews = self.review_repo.get_by_place(place_id)
        return reviews or []

    def create_review(self, review_data):
        try:
            # Validate required fields
            if not all(key in review_data for key in ['rating', 'text', 'user_id', 'place_id']):
                raise ValueError("Missing required fields")
            if not (1 <= review_data['rating'] <= 5):
                raise ValueError("Rating must be between 1 and 5")
            if not review_data['text'].strip():
                raise ValueError("Text cannot be empty")
            
            # Validate foreign keys
            if not self.place_repo.get(review_data['place_id']):
                raise ValueError("Place not found")
            if not self.user_repo.get(review_data['user_id']):
                raise ValueError("User not found")
            
            # Create a new review with all required arguments
            review = Review(
                rating=review_data['rating'],
                text=review_data['text'],
                user_id=review_data['user_id'],
                place_id=review_data['place_id']
            )
            self.review_repo.add(review)
            db.session.commit()
            return review
        except ValueError as e:
            raise e  # Let the calling function handle this error
        except Exception as e:
            raise Exception(f"Failed to create review: {str(e)}")
        finally:
            db.session.rollback()
