from flask import Flask, jsonify, send_from_directory, request
import os
from flask_cors import CORS
from pymongo import MongoClient
import requests # required for making HTTP requests

static_path = os.getenv('STATIC_PATH','static')
template_path = os.getenv('TEMPLATE_PATH','templates')

# Mongo connection
mongo_uri = os.getenv("MONGO_URI")
mongo = MongoClient(mongo_uri)
db = mongo.get_default_database()

app = Flask(__name__, static_folder=static_path, template_folder=template_path)
CORS(app)

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

@app.route('/api/comments/<article_id>', methods=['GET'])
@app.route('/comments/<article_id>', methods=['GET'])  # Also handle non-API path for compatibility
def get_comments(article_id):
    from urllib.parse import unquote
    
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
@app.route('/comments', methods=['POST'])  # Also handle non-API path for compatibility
def add_comment():
    data = request.json
    article_id = data.get('articleID')
    username = data.get('username', 'anonymous')
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

@app.route('/')
@app.route('/<path:path>')
def serve_frontend(path=''):
    if path != '' and os.path.exists(os.path.join(static_path,path)):
        return send_from_directory(static_path, path)
    return send_from_directory(template_path, 'index.html')

@app.route("/test-mongo")
def test_mongo():
    return jsonify({"collections": db.list_collection_names()})

if __name__ == '__main__':
    debug_mode = os.getenv('FLASK_ENV') != 'production'
    app.run(host='0.0.0.0', port=int(os.environ.get('PORT', 8000)),debug=debug_mode)