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
    """Facade class for managing interactions between models and repositories."""

    def __init__(self):
        """Initialize the facade with repository instances."""
        self.user_repo = UserRepository()
        self.place_repo = PlaceRepository()
        self.review_repo = ReviewRepository()
        self.amenity_repo = AmenityRepository()

    # User Methods
    def create_user(self, user_data):
        """Create a new user and save it to the database."""
        user = User(**user_data)
        self.user_repo.add(user)
        return user

    def get_user(self, user_id):
        """Retrieve a user by their ID."""
        return self.user_repo.get(user_id)

    def get_user_by_email(self, email):
        """Retrieve a user by their email."""
        return self.user_repo.get_user_by_email(email)

    def get_all_users(self):
        """Retrieve a list of all users."""
        return self.user_repo.get_all()

    def update_user(self, user_id, user_data):
        """Update a user's information by their ID."""
        user = self.user_repo.get(user_id)
        if not user:
            return None
        user.first_name = user_data.get('first_name', user.first_name)
        user.last_name = user_data.get('last_name', user.last_name)
        db.session.commit()
        return user

    def get_user_by_id(self, user_id):
        """Retrieve a user by their ID (alias for get_user)."""
        return self.user_repo.get_user_by_id(user_id)

    def save_user(self, user):
        """Save a user object to the database."""
        db.session.add(user)
        db.session.commit()

    # Amenity Methods
    def create_amenity(self, amenity_data):
        """Create a new amenity and associate it with places if provided."""
        amenity_id = str(uuid.uuid4())
        amenity = Amenity(
            id=amenity_id,
            name=amenity_data['name'],
            description=amenity_data.get('description')
        )

        place_ids = amenity_data.get('associated_places', [])
        if place_ids:
            places = self.place_repo.get_places_by_ids(place_ids)
            amenity.associated_places.extend(places)

        self.amenity_repo.add(amenity)
        return amenity

    def get_amenity(self, amenity_id):
        """Retrieve an amenity by its ID."""
        return self.amenity_repo.get(amenity_id)

    def get_all_amenities(self):
        """Retrieve a list of all amenities."""
        return self.amenity_repo.get_all()

    def update_amenity(self, amenity_id, amenity_data):
        """Update an amenity's information and associated places."""
        amenity = self.amenity_repo.get(amenity_id)
        if not amenity:
            return None

        amenity.name = amenity_data.get('name', amenity.name)
        amenity.description = amenity_data.get('description', amenity.description)

        place_ids = amenity_data.get('associated_places', [])
        if place_ids is not None:
            new_places = self.place_repo.get_places_by_ids(place_ids)
            # Add new places
            for place in new_places:
                if place not in amenity.associated_places:
                    amenity.associated_places.append(place)
            # Remove places not in the updated list
            to_remove = [place for place in amenity.associated_places if place.id not in place_ids]
            for place in to_remove:
                amenity.associated_places.remove(place)

        db.session.commit()
        return amenity

    def get_amenities_by_ids(self, amenity_ids):
        """Retrieve a list of amenities by their IDs."""
        return self.amenity_repo.get_amenities_by_ids(amenity_ids)

    # Place Methods
    def create_place(self, place_data):
        """Create a new place and associate it with amenities if provided."""
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
        """Retrieve a place by its ID, including associated amenity names."""
        place = Place.query.get(place_id)
        if not place:
            return None
        amenity_names = [amenity.name for amenity in place.associated_amenities]
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
            'associated_amenities': amenity_names
        }

    def get_all_places(self):
        """Retrieve a list of all places with their associated amenities."""
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
        """Update a place's information and associated amenities."""
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
            # Add new amenities
            for amenity in new_amenities:
                if amenity not in place.associated_amenities:
                    place.associated_amenities.append(amenity)
            # Remove amenities not in the updated list
            to_remove = [amenity for amenity in place.associated_amenities if amenity.id not in amenity_ids]
            for amenity in to_remove:
                place.associated_amenities.remove(amenity)

        db.session.commit()
        return place

    def delete_place(self, place_id):
        """Delete a place by its ID."""
        return self.place_repo.delete(place_id)

    def get_places_by_price_range(self, min_price, max_price):
        """Retrieve places within a price range."""
        return self.place_repo.get_by_price_range(min_price, max_price)

    def get_places_by_amenity(self, amenity_id):
        """Retrieve places associated with a specific amenity."""
        return self.place_repo.get_by_amenity(amenity_id)

    def get_places_by_owner(self, owner_id):
        """Retrieve places owned by a specific user."""
        return self.place_repo.get_by_owner(owner_id)

    def get_places_by_ids(self, place_ids):
        """Retrieve a list of places by their IDs."""
        return self.place_repo.get_places_by_ids(place_ids)

    # Review Methods
    def get_reviews_by_place(self, place_id):
        """Retrieve all reviews for a specific place."""
        place = self.place_repo.get(place_id)
        if not place:
            raise ValueError("Place not found")
        reviews = self.review_repo.get_by_place(place_id)
        return reviews or []

    def create_review(self, review_data):
        """Create a new review with validation."""
        try:
            # Validate required fields
            required_fields = ['rating', 'text', 'user_id', 'place_id']
            if not all(key in review_data for key in required_fields):
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

            # Create a new review
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
            raise e
        except Exception as e:
            raise Exception(f"Failed to create review: {str(e)}")
        finally:
            db.session.rollback()