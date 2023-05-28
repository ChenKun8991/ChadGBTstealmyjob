from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask import jsonify

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql://root:password123@localhost/mydatabase'
db = SQLAlchemy(app)

class Tour(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), nullable=False)
    rating = db.Column(db.Float, nullable=False)  # Changed to Float instead of Double
    description = db.Column(db.String(2000), nullable=False)
    created_at = db.Column(db.TIMESTAMP, server_default=db.func.current_timestamp(), nullable=False)
    
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    user = db.relationship('User', backref=db.backref('tours', lazy=True))

class Itinerary(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    itinerary = db.Column(db.String(2000), nullable=False)

    tour_id = db.Column(db.Integer, db.ForeignKey('tour.id'), nullable=False)
    user = db.relationship('Tour', backref=db.backref('itineraries', lazy=True))

class HighLight(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    hightlight = db.Column(db.String(2000), nullable=False)

    tour_id = db.Column(db.Integer, db.ForeignKey('tour.id'), nullable=False)
    tour = db.relationship('Tour', backref=db.backref('hightlights', lazy=True))

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), nullable=False)
    email = db.Column(db.String(50), nullable=False)
    created_at = db.Column(db.TIMESTAMP, server_default=db.func.current_timestamp(), nullable=False)

class Video(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), nullable=False)
    like = db.Column(db.Integer, nullable=False)  
    view_count  = db.Column(db.Integer, nullable=False) 
    created_at = db.Column(db.TIMESTAMP, server_default=db.func.current_timestamp(), nullable=False)
    link = db.Column(db.String(200), nullable=False)
    
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    user = db.relationship('User', backref=db.backref('videos', lazy=True))

class Comment(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    description = db.Column(db.String(2000), nullable=False)

    video_id = db.Column(db.Integer, db.ForeignKey('video.id'), nullable=False)
    video = db.relationship('Video', backref=db.backref('comments', lazy=True))
    
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    user = db.relationship('User', backref=db.backref('comments', lazy=True))
    
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
            'like': video.like,
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

# Insert dummy data
if __name__ == '__main__':
    # Create and insert dummy data for Tour table
    tour1 = Tour(name='Tour 1', rating=4.5, description='Description 1', created_at=datetime.now(), user_id=1)
    tour2 = Tour(name='Tour 2', rating=3.8, description='Description 2', created_at=datetime.now(), user_id=2)

    db.session.add(tour1)
    db.session.add(tour2)
    db.session.commit()

    # Create and insert dummy data for Itinerary table
    itinerary1 = Itinerary(itinerary='Itinerary 1', tour_id=1)
    itinerary2 = Itinerary(itinerary='Itinerary 2', tour_id=2)

    db.session.add(itinerary1)
    db.session.add(itinerary2)
    db.session.commit()

    # Create and insert dummy data for HighLight table
    highlight1 = HighLight(highlight='Highlight 1', tour_id=1)
    highlight2 = HighLight(highlight='Highlight 2', tour_id=2)

    db.session.add(highlight1)
    db.session.add(highlight2)
    db.session.commit()

    # Create and insert dummy data for User table
    user1 = User(name='User 1', email='user1@example.com', created_at=datetime.now())
    user2 = User(name='User 2', email='user2@example.com', created_at=datetime.now())

    db.session.add(user1)
    db.session.add(user2)
    db.session.commit()

    # Create and insert dummy data for Video table
    video1 = Video(name='Video 1', like=10, view_count=100, created_at=datetime.now(), link='video1.mp4', user_id=1)
    video2 = Video(name='Video 2', like=5, view_count=50, created_at=datetime.now(), link='video2.mp4', user_id=2)

    db.session.add(video1)
    db.session.add(video2)
    db.session.commit()

    # Create and insert dummy data for Comment table
    comment1 = Comment(description='Comment 1', video_id=1, user_id=1)
    comment2 = Comment(description='Comment 2', video_id=2, user_id=2)

    db.session.add(comment1)
    db.session.add(comment2)
    db.session.commit()

    app.run()