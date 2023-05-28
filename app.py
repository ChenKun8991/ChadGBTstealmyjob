from flask import Flask, jsonify, request

from flask import (
    Flask,
    request,
    make_response,
    redirect,
    abort,
    jsonify,
)
from flask_cors import CORS
import os
from sgid_client import SgidClient, generate_pkce_pair
from dotenv import load_dotenv
from uuid import uuid4
from urllib.parse import urlencode, parse_qs

from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

load_dotenv()
# In-memory store for user session data
# In a real application, this would be a database.
session_data = {}
SESSION_COOKIE_NAME = "exampleAppSession"

app = Flask(__name__)
# Allow app to interact with demo frontend
frontend_host = os.getenv("SGID_FRONTEND_HOST") or "http://localhost:5173"
CORS(app, origins=[frontend_host], supports_credentials=True)

app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql://root:password123@localhost/mydatabase'
db = SQLAlchemy(app)

## Models
sgid_client = SgidClient(
    client_id=os.getenv("SGID_CLIENT_ID"),
    client_secret=os.getenv("SGID_CLIENT_SECRET"),
    private_key=os.getenv("SGID_PRIVATE_KEY"),
    redirect_uri="http://localhost:5001/api/redirect",
)

## START OF SGID

@app.route("/api/auth-url")
def get_auth_url():
    ice_cream_selection = request.args.get("icecream")
    session_id = str(uuid4())
    # Use search params to store state so other key-value pairs
    # can be added easily
    state = urlencode(
        {
            "icecream": ice_cream_selection,
        }
    )
    # We pass the user's ice cream preference as the state,
    # so after they log in, we can display it together with the
    # other user info.
    code_verifier, code_challenge = generate_pkce_pair()
    url, nonce = sgid_client.authorization_url(
        state=state, code_challenge=code_challenge
    )
    session_data[session_id] = {
        "state": state,
        "nonce": nonce,
        "code_verifier": code_verifier,
    }
    res = make_response({"url": url})
    res.set_cookie(SESSION_COOKIE_NAME, session_id, httponly=True)
    return res


@app.route("/api/redirect")
def handle_redirect():
    auth_code = request.args.get("code")
    state = request.args.get("state")
    session_id = request.cookies.get(SESSION_COOKIE_NAME)

    session = session_data.get(session_id, None)
    # Validate that the state matches what we passed to sgID for this session
    if session is None or session["state"] != state:
        return redirect(f"{frontend_host}/error")

    sub, access_token = sgid_client.callback(
        code=auth_code, code_verifier=session["code_verifier"], nonce=session["nonce"]
    )
    session["access_token"] = access_token
    session["sub"] = sub
    session_data[session_id] = session

    return redirect(f"{frontend_host}/logged-in")


@app.route("/api/userinfo")
def userinfo():
    session_id = request.cookies.get(SESSION_COOKIE_NAME)
    session = session_data.get(session_id, None)
    access_token = (
        None
        if session is None or "access_token" not in session
        else session["access_token"]
    )
    if session is None or access_token is None:
        abort(401)
    sub, data = sgid_client.userinfo(sub=session["sub"], access_token=access_token)

    # Add ice cream flavour to userinfo
    ice_cream_selection = parse_qs(session["state"])["icecream"][0]
    data["iceCream"] = ice_cream_selection

    return {"sub": sub, "data": data}


@app.route("/api/logout")
def logout():
    session_id = request.cookies.get(SESSION_COOKIE_NAME)
    del session_data[session_id]
    res = make_response({})
    res.delete_cookie(SESSION_COOKIE_NAME)
    return res

## END OF SGID

class Tour(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), nullable=False)
    rating = db.Column(db.Float, nullable=False) 
    description = db.Column(db.String(2000), nullable=False)
    created_at = db.Column(db.TIMESTAMP, server_default=db.func.current_timestamp(), nullable=False)
    
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    user = db.relationship('User', backref=db.backref('tours', cascade='all, delete', lazy=True))

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
    email = db.Column(db.String(50), nullable=False, unique=True)
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

## Routing 

## Tours CRUD
@app.route('/tours', methods=['GET'])
@app.route('/tours/<int:tour_id>', methods=['GET'])
def get_tours(tour_id=None):
    if tour_id is not None:
        tour = Tour.query.get_or_404(tour_id)
        tour_data = {
            'id': tour.id,
            'name': tour.name,
            'rating': tour.rating,
            'description': tour.description,
            'created_at': tour.created_at
            # Add more fields if needed
        }
        return jsonify(tour_data)
    else:
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


## Itineraries CRUD
@app.route('/itineraries', methods=['GET'])
@app.route('/itineraries/<int:itinerary_id>', methods=['GET'])
def get_itineraries(itinerary_id=None):
    if itinerary_id is not None:
        itinerary = Itinerary.query.get_or_404(itinerary_id)
        itinerary_data = {
            'id': itinerary.id,
            'itinerary': itinerary.itinerary
            # Add more fields if needed
        }
        return jsonify(itinerary_data)
    else:
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

## Highlights CRUD
@app.route('/highlights', methods=['GET'])
@app.route('/highlights/<int:highlight_id>', methods=['GET'])
def get_highlights(highlight_id=None):
    if highlight_id is not None:
        highlight = HighLight.query.get_or_404(highlight_id)
        highlight_data = {
            'id': highlight.id,
            'highlight': highlight.highlight
            # Add more fields if needed
        }
        return jsonify(highlight_data)
    else:   
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

@app.route('/highlights', methods=['POST'])
def create_highlight():
    data = request.get_json()
    highlight_text = data.get('highlight')
    tour_id = data.get('tour_id')


    new_highlight = HighLight(highlight=highlight_text, tour_id=tour_id)

    db.session.add(new_highlight)
    db.session.commit()

    return jsonify({'message': 'Highlight created successfully', 'id': new_highlight.id}), 201

@app.route('/highlights/<int:highlight_id>', methods=['PUT'])
def update_highlight(highlight_id):
    highlight = HighLight.query.get_or_404(highlight_id)

    data = request.get_json()
    highlight_text = data.get('highlight')
    tour_id = data.get('tour_id')

    highlight.highlight = highlight_text
    highlight.tour_id = tour_id

    db.session.commit()

    return jsonify({'message': 'Highlight updated successfully'})

@app.route('/highlights/<int:highlight_id>', methods=['DELETE'])
def delete_highlight(highlight_id):
    highlight = HighLight.query.get_or_404(highlight_id)

    db.session.delete(highlight)
    db.session.commit()

    return jsonify({'message': 'Highlight deleted successfully'})

## Users CRUD
@app.route('/users', methods=['GET'])
@app.route('/users/<int:user_id>', methods=['GET'])
def get_users(user_id=None):
    if user_id == None:
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
    else:
        user = User.query.get_or_404(user_id)
        user_data = {
            'id': user.id,
            'name': user.name,
            'email': user.email,
            'created_at': user.created_at
            # Add more fields if needed
        }
        return jsonify(user_data)

@app.route('/users', methods=['POST'])
def create_user():
    data = request.get_json()
    name = data.get('name')
    email = data.get('email')

    if not name or not email:
        return jsonify({'message': 'Name and email are required'}), 400

    new_user = User(name=name, email=email)
    db.session.add(new_user)
    db.session.commit()

    return jsonify({'message': 'User created successfully', 'id': new_user.id}), 201

@app.route('/users/<int:user_id>', methods=['PUT'])
def update_user(user_id):
    user = User.query.get_or_404(user_id)
    data = request.get_json()
    name = data.get('name')
    email = data.get('email')

    if not name or not email:
        return jsonify({'message': 'Name and email are required'}), 400

    user.name = name
    user.email = email
    db.session.commit()

    return jsonify({'message': 'User updated successfully'})

@app.route('/users/<int:user_id>', methods=['DELETE'])
def delete_user(user_id):
    user = User.query.get_or_404(user_id)
    db.session.delete(user)
    db.session.commit()

    return jsonify({'message': 'User deleted successfully'})
# Videos CRUD
@app.route('/videos', methods=['GET'])
@app.route('/videos/<int:video_id>', methods=['GET'])
def get_videos(video_id=None):
    if video_id is None:
        videos = Video.query.all()
        video_list = []
        for video in videos:
            video_data = {
                'id': video.id,
                'name': video.name,
                'thumb_up': video.thumb_up,
                'view_count': video.view_count,
                'created_at': video.created_at,
                'link': video.link,
                # Add more fields if needed
            }
            video_list.append(video_data)
        return jsonify(video_list)
    else:
        video = Video.query.get_or_404(video_id)
        video_data = {
            'id': video.id,
            'name': video.name,
            'thumb_up': video.thumb_up,
            'view_count': video.view_count,
            'created_at': video.created_at,
            'link': video.link,
        }
        return jsonify(video_data)


@app.route('/videos', methods=['POST'])
def create_video():
    data = request.get_json()
    video = Video(name=data['name'], thumb_up=data['thumb_up'], view_count=data['view_count'], link=data['link'], user_id=data['user_id'])
    db.session.add(video)
    db.session.commit()
    return jsonify({'message': 'Video created successfully', 'id': video.id})

@app.route('/videos/<int:video_id>', methods=['PUT'])
def update_video(video_id):
    video = Video.query.get_or_404(video_id)
    data = request.get_json()
    video.name = data['name']
    video.thumb_up = data['thumb_up']
    video.view_count = data['view_count']
    video.link = data['link']
    db.session.commit()
    return jsonify({'message': 'Video updated successfully'})

@app.route('/videos/<int:video_id>', methods=['DELETE'])
def delete_video(video_id):
    video = Video.query.get_or_404(video_id)
    db.session.delete(video)
    db.session.commit()
    return jsonify({'message': 'Video deleted successfully'})

@app.route('/comments', methods=['GET'])
@app.route('/comments/<int:comment_id>', methods=['GET'])
def get_comments(comment_id = None):
    if comment_id == None:
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
    else:
        comment = Comment.query.get_or_404(comment_id)
        comment_data = {
        'id': comment.id,
        'description': comment.description
        # Add more fields if needed
    }
    return jsonify(comment_data)

@app.route('/comments', methods=['POST'])
def create_comment():
    description = request.json.get('description')
    video_id = request.json.get('video_id')
    user_id = request.json.get('user_id')

    if not description:
        return jsonify({'message': 'Description is required'}), 400

    video = Video.query.get(video_id)
    if not video:
        return jsonify({'message': 'Invalid video_id'}), 404

    user = User.query.get(user_id)
    if not user:
        return jsonify({'message': 'Invalid user_id'}), 404

    comment = Comment(description=description, video_id=video_id, user_id=user_id)
    db.session.add(comment)
    db.session.commit()

    return jsonify({'message': 'Comment created successfully', 'id': comment.id}), 201
@app.route('/comments/<int:comment_id>', methods=['PUT'])
def update_comment(comment_id):
    comment = Comment.query.get_or_404(comment_id)

    description = request.json.get('description')

    if not description:
        return jsonify({'message': 'Description is required'}), 400
    
    comment.description = description
    db.session.commit()

    return jsonify({'message': 'Comment updated successfully'}), 200

@app.route('/comments/<int:comment_id>', methods=['DELETE'])
def delete_comment(comment_id):
    comment = Comment.query.get_or_404(comment_id)
    db.session.delete(comment)
    db.session.commit()
    return jsonify({'message': 'Comment deleted successfully'})

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
    video1 = Video(name='Video 1', thumb_up=10, view_count=100, link='video1.mp4', user_id=1)
    video2 = Video(name='Video 2', thumb_up=5, view_count=50, link='video2.mp4', user_id=2)
    
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