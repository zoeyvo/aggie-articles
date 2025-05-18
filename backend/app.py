from flask import Flask, jsonify, send_from_directory, request, session, redirect, url_for
from functools import wraps
import os
from flask_cors import CORS
from pymongo import MongoClient
from bson.objectid import ObjectId
import requests 
from urllib.parse import unquote
from authlib.integrations.flask_client import OAuth

static_path = os.getenv('STATIC_PATH','static')
template_path = os.getenv('TEMPLATE_PATH','templates')

# Mongo connection
mongo_uri = os.getenv("MONGO_URI")
mongo = MongoClient(mongo_uri)
db = mongo.get_default_database()

app = Flask(__name__, static_folder=static_path, template_folder=template_path)

# Configure CORS to allow cookies to be sent in cross-origin requests
CORS(app, supports_credentials=True)

# Configure OAuth with Dex
oauth = OAuth(app)
oauth.register(
    name='dex',
    client_id='flask-app',
    client_secret='flask-secret',
    # For internal service-to-service communication
    server_metadata_url='http://dex:5556/.well-known/openid-configuration',
    # These URLs must be what the browser can access
    authorize_url='http://localhost:5556/auth',
    access_token_url='http://dex:5556/token',  # Backend uses this directly
    userinfo_endpoint='http://dex:5556/userinfo',  # Backend uses this directly
    client_kwargs={'scope': 'openid email profile'},
)

app.secret_key = os.environ.get("FLASK_SECRET_KEY", "dev_secret")
# Set session expiration to 1 day
app.config['PERMANENT_SESSION_LIFETIME'] = 60 * 60 * 24  # 24 hours in seconds
# Ensure session cookies are properly set for Docker environment
app.config['SESSION_COOKIE_SECURE'] = False  # Set to True in production with HTTPS
app.config['SESSION_COOKIE_HTTPONLY'] = True
app.config['SESSION_COOKIE_SAMESITE'] = 'Lax'  # Important for cross-domain cookies

@app.route('/login')
def login():
    # Use explicit URL with localhost for browser access
    redirect_uri = "http://localhost:8000/auth/callback"
    print(f"Login redirecting to Dex with callback URL: {redirect_uri}")
    return oauth.dex.authorize_redirect(redirect_uri)

@app.route('/auth/callback')
def auth_callback():
    try:
        print("Auth callback started")
        token = oauth.dex.authorize_access_token()
        # Use userinfo endpoint instead of parse_id_token
        userinfo = oauth.dex.userinfo(token=token)
        print(f"User info: {userinfo}")

        session.clear()
        session['user'] = userinfo
        session.permanent = True

        print(f"User authenticated: {userinfo.get('email', 'unknown email')}")
        return redirect(f'http://localhost:{os.getenv("FRONTEND_PORT")}/?auth_success=' + os.urandom(4).hex())
    except Exception as e:
        print(f"Authentication error: {str(e)}")
        import traceback
        traceback.print_exc()
        return redirect(f'http://localhost:{os.getenv("FRONTEND_PORT")}/?auth_error=1')

def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user' not in session:
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated_function

@app.route('/api/key')
def get_key():
    return jsonify({'apiKey': os.getenv('NYT_API_KEY')})

@app.route('/api/articles')
def get_articles():

    api_key = os.getenv('NYT_API_KEY')
    NYT_API_URL = "https://api.nytimes.com/svc/search/v2/articlesearch.json"
    
    if not api_key:
        return jsonify({'error': 'NYT_API_KEY is not set in .env'}), 500

    # Query
    query = request.args.get('query', 'Sacramento', 'Davis')
    
    # Filter to narrow location to California
    filter = "timesTag.location%3ACalifornia"
    
    api_url = f"{NYT_API_URL}?q={query}&fq={filter}&api-key={api_key}"

    try:
        response = requests.get(api_url)
        data = response.json()
        return jsonify(data)
    except requests.exceptions.RequestException as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/comments/<path:article_id>', methods=['GET'])
def get_comments(article_id):
    # URL decode the article_id in case it's URL encoded
    article_id = unquote(article_id)
    
    # Extract the unique identifier part after nyt://
    if "nyt://" in article_id:
        article_id = article_id.split("nyt://")[1]
    elif "nyt:/" in article_id:
        article_id = article_id.split("nyt:/")[1]
    
    print(f"Extracted article ID: {article_id}")
    
    # Use article-comments collection instead of comments
    all_comments = list(db["article-comments"].find({"articleID": article_id}))
    for comment in all_comments:
        comment["_id"] = str(comment["_id"])  # convert ObjectId to string
    print(f"Fetched {len(all_comments)} comments for article ID: {article_id}")
    return jsonify(all_comments)  # Always returns a valid JSON array, even if empty

@app.route('/api/comments', methods=['POST'])
@login_required
def add_comment():
    # Check if user is authenticated
    if 'user' not in session:
        return jsonify({"error": "Authentication required"}), 401
    
    data = request.json
    article_id = data.get('articleID')
    # Get username from authenticated session
    user_data = session['user']
    username = user_data.get('username', user_data.get('email', 'anonymous'))
    text = data.get('text')    
    
    if not article_id or not text:
        return jsonify({"error": "Missing fields"}), 400
    # Extract the unique identifier part after nyt://
    if "nyt://" in article_id:
        article_id = article_id.split("nyt://")[1]
    elif "nyt:/" in article_id:
        article_id = article_id.split("nyt:/")[1]
    
    print(f"Storing comment with article ID: {article_id}")
        
    comment = {
        "articleID": article_id,
        "username": username,
        "text": text
    }

    db["article-comments"].insert_one(comment)
    print(f"Added comment for article ID: {article_id}")
    return jsonify({"message": "Comment added"}), 201
  
@app.route('/api/moderate/<comment_id>', methods=['PUT'])
def moderate_comment(comment_id):
    data = request.json
  
    # Update the text field of comment object in DB
    status = db["article-comments"].update_one(
      {"_id": ObjectId(comment_id)}, 
      {"$set": {"text": data.get("replace")}}
    )
    
    if status.matched_count:
      return jsonify({"message": "Comment deleted"}), 201
    else:
      return jsonify({"error": "Fail to delete comment"}), 400
    
# Force login on site entry
@app.route('/')
@app.route('/<path:path>')
def serve_frontend(path=''):
    # if 'user' not in session:
    #     # Always force login if not authenticated
    #     return redirect('/login')
    # Serve static files or index.html
    if path != '' and os.path.exists(os.path.join(static_path, path)):
        return send_from_directory(static_path, path)
    return send_from_directory(template_path, 'index.html')

@app.route('/api/user')
def get_user():
    """Return the current user info if authenticated, or authentication status if not."""
    print(f"Session keys: {list(session.keys()) if session else 'No session'}")
    
    if 'user' in session:
        # Return user info from the session
        user_data = session['user']
        print(f"User data from session: {user_data}")
        
        # Extract username and other fields
        username = user_data.get('username', user_data.get('email', 'User'))
        email = user_data.get('email', '')
        user_id = user_data.get('userID', user_data.get('sub', ''))
        
        print(f"Returning authenticated user: {username}, {email}")
        
        return jsonify({
            'authenticated': True,
            'username': username,
            'email': email,
            'user_id': user_id,
        })
    else:
        print("No user in session, returning unauthenticated")
        # User is not logged in - return status 200 with authenticated: false
        return jsonify({'authenticated': False})

@app.route('/logout')
def logout():
    """Clear the user session and redirect to home."""
    session.pop('user', None)
    return redirect('/')

if __name__ == '__main__':
    debug_mode = os.getenv('FLASK_ENV') != 'production'
    app.run(host='0.0.0.0', port=int(os.environ.get('PORT', 8000)),debug=debug_mode)