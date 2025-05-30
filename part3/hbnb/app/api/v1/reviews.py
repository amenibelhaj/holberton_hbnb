from flask_restx import Namespace, Resource, fields
from app.services import facade
from flask_jwt_extended import get_jwt, jwt_required, get_jwt_identity
from app.services.facade import HBnBFacade

facade = HBnBFacade()

api = Namespace('reviews', description='Review operations')
# Define the review model for input validation and documentation
review_model = api.model('Review', {
    'text': fields.String(required=True, description='Text of the review'),
    'rating': fields.Integer(required=True, description='Rating of the place (1-5)')
})


@api.route('/')
class ReviewList(Resource):
    @api.expect(review_model)
    @api.response(201, 'Review successfully created')
    @api.response(400, 'Invalid input data')
    @api.response(404, 'Place not found')
    @api.response(404, 'User not found')
    @jwt_required()
    def post(self):
        """Register a new review"""
        review_data = api.payload
        current_user_id = get_jwt_identity()  # Get user ID from JWT
        place = facade.get_place(review_data['place_id'])
        user = facade.get_user_by_id(current_user_id)
        if not user:
            return {'error': 'User not found'}, 404
        if not place:
            return {'error': 'Place not found'}, 404
        if place['place']['user_id'] == current_user_id:
            return {'error': 'You cannot review your own place'}, 400
        place_reviews = facade.get_reviews_by_place(review_data['place_id'])
        for existing_review in place_reviews:
            if existing_review.user_id == current_user_id:
                return {'error': 'You have already reviewed this place'}, 400
        try:
            new_review = facade.create_review({
                'text': review_data['text'],
                'rating': review_data['rating'],
                'user_id': current_user_id,
                'place_id': review_data['place_id']
            })
            return {
                'id': new_review.id,
                'text': new_review.text,
                'rating': new_review.rating,
                'user_id': new_review.user_id,
                'place_id': new_review.place_id
            }, 201
        except ValueError as e:
            return {'error': f'Invalid input data: {str(e)}'}, 400
    
    @api.response(200, 'List of reviews retrieved successfully')
    @api.response(404, 'No reviews found')
    def get(self):
        """Retrieve a list of all reviews"""
        reviews = facade.get_all_reviews()
        if not reviews:
            return {'error': 'No reviews found'}, 404
        return [{'id': review.id, 'text': review.text, 'rating': review.rating, 'user_id': review.user_id, 'place_id': review.place_id} for review in reviews], 200


@api.route('/<review_id>')
class ReviewResource(Resource):
    @api.response(200, 'Review details retrieved successfully')
    @api.response(404, 'Review not found')
    def get(self, review_id):
        """Get review details by ID"""
        review = facade.get_review(review_id)
        if not review:
            return {'error': 'Review not found'}, 404
        return {'id': review.id, 'text': review.text, 'rating': review.rating, 'user_id': review.user_id, 'place_id': review.place_id}, 200
   
    @api.expect(review_model)
    @api.response(200, 'Review updated successfully')
    @api.response(404, 'Review not found')
    @api.response(403, 'Unauthorized action')
    @api.response(500, 'Failed to update this review')
    @jwt_required()
    def put(self, review_id):
        """Update a review's information by ID"""
        review = facade.get_review(review_id)
        if not review:
            return {'error': 'Review not found'}, 404
        current_user = get_jwt_identity()
        if review.user_id != current_user:
            return {'error': 'Unauthorized action'}, 403
        review_data = api.payload
        review.text = review_data.get('text', review.text)
        review.rating = review_data.get('rating', review.rating)
        updated_review = facade.update_review(review.id, {
            'text': review.text,
            'rating': review.rating,
        })
        if not updated_review:
            return {'error': 'Failed to update this review'}, 500
        return {'id': review.id, 'text': review.text, 'rating': review.rating, 'user_id': review.user_id, 'place_id': review.place_id}, 200
   
    @api.response(200, 'Review deleted successfully')
    @api.response(404, 'Review not found')
    @api.response(403, 'Unauthorized action')
    @api.response(500, 'Failed to delete this review')
    @jwt_required()
    def delete(self, review_id):
        """Delete a review"""
        review = facade.get_review(review_id)
        current_user_id = get_jwt_identity()
        claims = get_jwt()
        if not review:
            return {'error': 'Review not found'}, 404
        if review.user_id != current_user_id and not claims.get('is_admin'):
            return {'error': 'Unauthorized action'}, 403
        deleted_review = facade.delete_review(review_id)
        if deleted_review:
            return {'error': 'Failed to delete this review'}, 500
        return {'message': 'Review deleted successfully'}, 200
    
@api.route('/places/<place_id>/reviews')
class PlaceReviewList(Resource):
    @api.response(200, 'List of reviews retrieved successfully')
    @api.response(404, 'No reviews found for this place')
    def get(self, place_id):
        """Retrieve all reviews for a specific place"""
        place = facade.get_place(place_id)
        if not place:
            return {'error': 'Place not found'}, 404
        reviews = facade.get_reviews_by_place(place_id)
        if not reviews:
            return {'error': 'No reviews found for this place'}, 404
        return [{'id': review.id, 'text': review.text, 'rating': review.rating, 'user_id': review.user_id, 'place_id': review.place_id} for review in reviews], 200

    @api.expect(review_model)
    @api.response(201, 'Review successfully created')
    @api.response(400, 'Invalid input data')
    @api.response(404, 'Place not found')
    @api.response(404, 'User not found')
    @jwt_required()
    def post(self, place_id):
        """Post a new review for a place"""
        review_data = api.payload
        current_user_id = get_jwt_identity()  # Get user ID from JWT
        place = facade.get_place(place_id)  # Get place by place_id
        user = facade.get_user_by_id(current_user_id)
        
        if not user:
            return {'error': 'User not found'}, 404
        if not place:
            return {'error': 'Place not found'}, 404
        if place['place']['user_id'] == current_user_id:
            return {'error': 'You cannot review your own place'}, 400
        
        place_reviews = facade.get_reviews_by_place(place_id)
        for existing_review in place_reviews:
            if existing_review.user_id == current_user_id:
                return {'error': 'You have already reviewed this place'}, 400
        
        try:
            new_review = facade.create_review({
                'text': review_data['text'],
                'rating': review_data['rating'],
                'user_id': current_user_id,
                'place_id': place_id  # Link the review to the place using place_id
            })
            return {
                'id': new_review.id,
                'text': new_review.text,
                'rating': new_review.rating,
                'user_id': new_review.user_id,
                'place_id': new_review.place_id
            }, 201
        except ValueError as e:
            return {'error': f'Invalid input data: {str(e)}'}, 400