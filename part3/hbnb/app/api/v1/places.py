from flask_restx import Namespace, Resource, fields
from app.services import facade
from app.services.facade import HBnBFacade
from app import db
from app.models.amenity import Amenity 
from app.models.place import Place
from app.models.amenity import Amenity


from flask_jwt_extended import get_jwt, jwt_required, get_jwt_identity

facade = HBnBFacade()
api = Namespace('places', description='Place operations')
# Define the models for related entities
amenity_model = api.model('PlaceAmenity', {
    'id': fields.String(description='Amenity ID'),
    'name': fields.String(description='Name of the amenity')
})

user_model = api.model('PlaceUser', {
    'id': fields.String(description='User ID'),
    'first_name': fields.String(description='First name of the owner'),
    'last_name': fields.String(description='Last name of the owner'),
    'email': fields.String(description='Email of the owner'),
})

place_model = api.model('Place', {
    'title': fields.String(required=True, description='Title of the place'),
    'description': fields.String(description='Description of the place'),
    'price': fields.Float(required=True, description='Price per night'),
    'latitude': fields.Float(required=True, description='Latitude of the place'),
    'longitude': fields.Float(required=True, description='Longitude of the place')
})

@api.route('/')
class PlaceList(Resource):
    @api.expect(place_model)
    @api.response(201, 'Place successfully created')
    @api.response(400, 'Invalid input data')
    @jwt_required()
    def post(self):
        """Register a new place"""
        place_data = api.payload
        current_user_id = get_jwt_identity()
        place_data['user_id'] = current_user_id

        # Get the amenities_ids from the request payload (if any)
        amenities_ids = place_data.get('amenities_ids', [])

        try:
            # Create the new place using the facade
            new_place = facade.create_place(place_data)

            # If amenities_ids are provided, add them to the new place
            if amenities_ids:
                for amenity_id in amenities_ids:
                    # Query the amenity by ID
                    amenity = Amenity.query.get(amenity_id)  # Fetch the amenity by ID

                    if amenity:
                        # Add the amenity to the place
                        new_place.add_amenity(amenity)
                    else:
                        # If any amenity ID is invalid, return an error
                        return {'error': f'Amenity with ID {amenity_id} not found'}, 404
            
            # After adding amenities, return the newly created place's details
            associated_amenities = [amenity.name for amenity in new_place.associated_amenities]

            return {
                'id': new_place.id,
                'title': new_place.title,
                'description': new_place.description,
                'price': new_place.price,
                'latitude': new_place.latitude,
                'longitude': new_place.longitude,
                'associated_amenities': associated_amenities
            }, 201

        except ValueError:
            return {'error': 'Invalid input data'}, 400

    @api.response(200, 'List of places retrieved successfully')
    @api.response(404, 'No places found')
    def get(self):
        """Retrieve a list of all places"""
        places_data = facade.get_all_places()
        if not places_data:
            return {'error': 'No places found'}, 404

        return [{
            'id': place_data['place']['id'],
            'title': place_data['place']['title'],
            'description': place_data['place']['description'],
            'price': place_data['place']['price'],
            'latitude': place_data['place']['latitude'],
            'longitude': place_data['place']['longitude'],
            'associated_amenities': place_data['associated_amenities']
        } for place_data in places_data], 200



@api.route('/<place_id>')
class PlaceResource(Resource):
    @api.response(200, 'Place details retrieved successfully')
    @api.response(404, 'Place not found')
    def get(self, place_id):
        """Get place details by ID"""
        place_data = facade.get_place(place_id)
        if not place_data:
            return {'error': 'No places found'}, 404
        
        return place_data, 200
    
    @api.expect(place_model)
    @api.response(200, 'Place updated successfully')
    @api.response(404, 'Place not found')
    @api.response(403, 'Unauthorized action')
    @api.response(500, 'Failed to update this place')
    @jwt_required()
    def put(self, place_id):
        """Update a place's information"""
        place_data = facade.get_place(place_id)
        current_user_id = get_jwt_identity()
        if not place_data:
            return {'error': 'Place not found'}, 404
        if place_data['place']['user_id'] != current_user_id:
            return {'error': 'Unauthorized action'}, 403
        user_place = api.payload
        updated_place = facade.update_place(place_id, user_place)
        if not updated_place:
            return {'error': 'Failed to update this place'}, 500
        associated_amenities = [amenity.id for amenity in updated_place.associated_amenities]
        return {
            'id': updated_place.id,
            'title': updated_place.title,
            'description': updated_place.description,
            'price': updated_place.price,
            'latitude': updated_place.latitude,
            'longitude': updated_place.longitude,
            'associated_amenities': associated_amenities
        }, 200

    @api.response(200, 'Review deleted successfully')
    @api.response(404, 'Review not found')
    @api.response(403, 'Unauthorized action')
    @api.response(500, 'Failed to delete this review')
    @jwt_required()
    def delete(self, place_id):
        """Delete a review"""
        place = facade.get_place(place_id)
        if not place:
            return {'error': 'Place not found'}, 404
        current_user = get_jwt_identity()
        claims = get_jwt()
        if place.user_id != current_user and not claims.get('is_admin'):
            return {'error': 'Unauthorized action'}, 403
        deleted_place = facade.delete_place(place_id)
        if not deleted_place:
            return {'error': 'Failed to delete this place'}, 500
        return {'message': 'Place deleted successfully'}, 200

        # Get the list of amenity IDs from the request payload
        amenities_ids = api.payload.get('amenities_ids')
        
        if not amenities_ids:
            return {'error': 'Amenities IDs are required'}, 400
        
@api.route('/<place_id>/amenities')
class PlaceAmenitiesResource(Resource):
    @api.expect(amenity_model)  # Expecting a list of amenity IDs
    @api.response(200, 'Amenities added successfully')
    @api.response(404, 'Place not found')
    @api.response(400, 'Invalid input')
    @jwt_required()
    def post(self, place_id):
        """Add amenities to a place"""
        # Fetch place from the database (place_data will be a dictionary)
        place_data = facade.get_place(place_id)
        
        if not place_data:
            return {'error': 'Place not found'}, 404
        
        # Get the list of amenity IDs from the request payload
        amenities_ids = api.payload.get('amenities_ids')
        
        if not amenities_ids:
            return {'error': 'Amenities IDs are required'}, 400
        
        # Query the amenities table and get the amenities
        amenities = Amenity.query.filter(Amenity.id.in_(amenities_ids)).all()
        
        if len(amenities) != len(amenities_ids):
            return {'error': 'Some amenities not found'}, 404
        
        # Check if 'associated_amenities' exists in place_data
        if 'associated_amenities' in place_data:
            # If it exists, extend the list of associated amenities
            existing_amenities_ids = [amenity.id for amenity in place_data['associated_amenities']]
            for amenity in amenities:
                if amenity.id not in existing_amenities_ids:
                    place_data['associated_amenities'].append(amenity)
        else:
            # If it doesn't exist, create the list of associated amenities
            place_data['associated_amenities'] = amenities
        
        # Update the place data in the database (make sure this function properly updates the database)
        facade.update_place(place_data)

        return {'message': 'Amenities added successfully'}, 200

    @api.response(200, 'Amenities retrieved successfully')
    @api.response(404, 'Place not found')
    @jwt_required()
    def get(self, place_id):
        """Retrieve amenities associated with a place by its ID"""
        # Fetch place from the database
        place_data = facade.get_place(place_id)
        
        if not place_data:
            return {'error': 'Place not found'}, 404
        associated_amenities = place_data['associated_amenities']
        # Retrieve the associated amenities for the place
        amenities = Amenity.query.filter(Amenity.id.in_(associated_amenities)).all()
        
        # If there are associated amenities, return them
        if associated_amenities:
     # Return a list of amenities (you can modify this as needed)
            amenities_list = [{'id': amenity.id, 'name': amenity.name} for amenity in amenities]
            return {'associated_amenities': amenities_list}, 200
        else:
            return {'message': 'No amenities associated with this place'}, 404



@api.route('/admin/<place_id>')
class AdminPlaceModify(Resource):
    @api.expect(place_model)
    @api.response(200, 'Place updated successfully')
    @api.response(404, 'Place not found')
    @api.response(403, 'Unauthorized action')
    @api.response(500, 'Failed to update this place')
    @jwt_required()
    def put(self, place_id):
        current_user = get_jwt_identity()
       
        claims = get_jwt()
        if not claims.get('is_admin'):
            return {'error': 'Admin privileges required'}, 403
       
       
        place = facade.get_place(place_id)
        if not place:
            return {'error': 'Place not found'}, 404
       
        user_place = api.payload
        updated_place = facade.update_place(place_id, user_place)
        if not updated_place:
            return {'error': 'Failed to update this place'}, 500
        return {'id': updated_place.id, 'title': updated_place.title, 'description': updated_place.description, 'price': updated_place.price, 'latitude': updated_place.latitude, 'longitude' : updated_place.longitude}, 200