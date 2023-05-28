from flask import Flask, jsonify, request
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime


app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql://root:password123@localhost/mydatabase'
db = SQLAlchemy(app)

class Tour(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), nullable=False)
    rating = db.Column(db.Float, nullable=False) 
    description = db.Column(db.String(2000), nullable=False)
    created_at = db.Column(db.TIMESTAMP, server_default=db.func.current_timestamp(), nullable=False)
    
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    user = db.relationship('User', backref=db.backref('tours', lazy=True))

class Itinerary(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    itinerary = db.Column(db.String(2000), nullable=False)

    tour_id = db.Column(db.Integer, db.ForeignKey('tour.id'), nullable=False)
    tour = db.relationship('Tour', backref=db.backref('itineraries', cascade='all, delete', lazy=True))

class HighLight(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    highlight = db.Column(db.String(2000), nullable=False)

    tour_id = db.Column(db.Integer,  db.ForeignKey('tour.id'), nullable=False)
    tour = db.relationship('Tour',backref=db.backref('highlights', cascade='all, delete', lazy=True))

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), nullable=False)
    email = db.Column(db.String(50), nullable=False)
    created_at = db.Column(db.TIMESTAMP, server_default=db.func.current_timestamp(), nullable=False)

class Video(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), nullable=False)
    thumb_up = db.Column(db.Integer, nullable=False)  
    view_count  = db.Column(db.Integer, nullable=False) 
    created_at = db.Column(db.TIMESTAMP, server_default=db.func.current_timestamp(), nullable=False)
    link = db.Column(db.String(200), nullable=False)
    
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    user = db.relationship('User', backref=db.backref('videos', cascade='all, delete', lazy=True))

class Comment(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    description = db.Column(db.String(2000), nullable=False)

    video_id = db.Column(db.Integer, db.ForeignKey('video.id'), nullable=False)
    video = db.relationship('Video', backref=db.backref('comments', cascade='all, delete', lazy=True))
    
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    user = db.relationship('User', backref=db.backref('comments', cascade='all, delete', lazy=True))

#Tours 
@app.route('/tours', methods=['GET'])
def get_tours():
    tours = Tour.query.all()
    tour_list = []
    for tour in tours:
        tour_data = {
            'id': tour.id,
            'name': tour.name,
            'rating': tour.rating,
            'description': tour.description,
            'created_at': tour.created_at
            # Add more fields if needed
        }
        tour_list.append(tour_data)
    return jsonify(tour_list)

@app.route('/tours', methods=['POST'])
def create_tour():
    data = request.get_json()  
    name = data.get('name')
    rating = data.get('rating')
    description = data.get('description')
    user_id= data.get('user_id')
    new_tour = Tour(name=name, rating=rating, description=description, user_id = user_id)
    db.session.add(new_tour)
    db.session.commit()

    return jsonify({'message': 'Tour created successfully', 'id': new_tour.id}), 201

@app.route('/tours/<int:tour_id>', methods=['PUT'])
def edit_tour(tour_id):
    tour = Tour.query.get_or_404(tour_id)
    data = request.get_json()
    tour.name = data.get('name', tour.name)
    tour.rating = data.get('rating', tour.rating)
    tour.description = data.get('description', tour.description)
    db.session.commit()
    return jsonify({'message': 'Tour updated successfully'})

@app.route('/tours/<int:tour_id>', methods=['DELETE'])
def delete_tour(tour_id):
    tour = Tour.query.get_or_404(tour_id)
    db.session.delete(tour)
    db.session.commit()
    return jsonify({'message': 'Tour deleted successfully'})

@app.route('/itineraries', methods=['GET'])
def get_itineraries():
    itineraries = Itinerary.query.all()
    itinerary_list = []
    for itinerary in itineraries:
        itinerary_data = {
            'id': itinerary.id,
            'itinerary': itinerary.itinerary
            # Add more fields if needed
        }
        itinerary_list.append(itinerary_data)
    return jsonify(itinerary_list)

@app.route('/itineraries', methods=['POST'])
def create_itinerary():
    data = request.get_json()
    itinerary_text = data.get('itinerary')
    tour_id = data.get('tour_id')

    tour = Tour.query.get(tour_id)
    if tour is None:
        return jsonify({'error': 'Invalid tour_id'}), 404

    new_itinerary = Itinerary(itinerary=itinerary_text, tour_id=tour_id)
    db.session.add(new_itinerary)
    db.session.commit()

    return jsonify({'message': 'Itinerary created successfully', 'id': new_itinerary.id}), 201


@app.route('/itineraries/<int:itinerary_id>', methods=['PUT'])
def update_itinerary(itinerary_id):
    data = request.get_json()
    itinerary_text = data.get('itinerary')
    tour_id = data.get('tour_id')

    itinerary = Itinerary.query.get_or_404(itinerary_id)

    tour = Tour.query.get(tour_id)
    if tour is None:
        return jsonify({'error': 'Invalid tour_id'}), 404

    itinerary.itinerary = itinerary_text
    itinerary.tour_id = tour_id
    db.session.commit()

    return jsonify({'message': 'Itinerary updated successfully'})

@app.route('/itineraries/<int:itineraries_id>', methods=['DELETE'])
def delete_itinerary(itineraries_id):
    itinerary = Itinerary.query.get_or_404(itineraries_id)
    db.session.delete(itinerary)
    db.session.commit()
    return jsonify({'message': 'Itinerary deleted successfully'})

@app.route('/highlights', methods=['GET'])
def get_highlights():
    highlights = HighLight.query.all()
    highlight_list = []
    for highlight in highlights:
        highlight_data = {
            'id': highlight.id,
            'highlight': highlight.highlight
            # Add more fields if needed
        }
        highlight_list.append(highlight_data)
    return jsonify(highlight_list)


@app.route('/users', methods=['GET'])
def get_users():
    users = User.query.all()
    user_list = []
    for user in users:
        user_data = {
            'id': user.id,
            'name': user.name,
            'email': user.email,
            'created_at': user.created_at
            # Add more fields if needed
        }
        user_list.append(user_data)
    return jsonify(user_list)

@app.route('/videos', methods=['GET'])
def get_videos():
    videos = Video.query.all()
    video_list = []
    for video in videos:
        video_data = {
            'id': video.id,
            'name': video.name,
            'thumb_up': video.thumb_up,
            'view_count': video.view_count,
            'created_at': video.created_at,
            'link': video.link
            # Add more fields if needed
        }
        video_list.append(video_data)
    return jsonify(video_list)

@app.route('/comments', methods=['GET'])
def get_comments():
    comments = Comment.query.all()
    comment_list = []
    for comment in comments:
        comment_data = {
            'id': comment.id,
            'description': comment.description
            # Add more fields if needed
        }
        comment_list.append(comment_data)
    return jsonify(comment_list)


def populate_data():
    # Create and insert dummy data for User table
    user1 = User(name='User 1', email='user1@example.com', created_at=datetime.now())
    user2 = User(name='User 2', email='user2@example.com', created_at=datetime.now())

    db.session.add(user1)
    db.session.add(user2)

    # Create and insert dummy data for Tour table
    tour1 = Tour(name='Tour 1', rating=4.5, description='Description 1', created_at=datetime.now(), user_id=1)
    tour2 = Tour(name='Tour 2', rating=3.8, description='Description 2', created_at=datetime.now(), user_id=2)

    db.session.add(tour1)
    db.session.add(tour2)

    # Create and insert dummy data for Itinerary table
    itinerary1 = Itinerary(itinerary='Itinerary 1', tour_id=1)
    itinerary2 = Itinerary(itinerary='Itinerary 2', tour_id=2)

    db.session.add(itinerary1)
    db.session.add(itinerary2)

    # Create and insert dummy data for HighLight table
    highlight1 = HighLight(highlight='Highlight 1', tour_id=1)
    highlight2 = HighLight(highlight='Highlight 2', tour_id=2)

    db.session.add(highlight1)
    db.session.add(highlight2)

    # Create and insert dummy data for Video table
    video1 = Video(name='Video 1', thumb_up=10, view_count=100, created_at=datetime.now(), link='video1.mp4', user_id=1)
    video2 = Video(name='Video 2', thumb_up=5, view_count=50, created_at=datetime.now(), link='video2.mp4', user_id=2)

    db.session.add(video1)
    db.session.add(video2)

    # Create and insert dummy data for Comment table
    comment1 = Comment(description='Comment 1', video_id=1, user_id=1)
    comment2 = Comment(description='Comment 2', video_id=2, user_id=2)

    db.session.add(comment1)
    db.session.add(comment2)
    db.session.commit()
    
def drop_all_tables():
    db.drop_all()
    
# Insert dummy data
if __name__ == '__main__':
    with app.app_context():
        print("pass")
        drop_all_tables()
        db.create_all()
        populate_data()
    app.run()