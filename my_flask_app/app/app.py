from pickle import GET

from werkzeug.security import generate_password_hash, check_password_hash
from flask import session
from app.db.db import db
from app.db.models import User
from flask import Flask, jsonify, render_template, request
from app.config.config import get_config_by_name
from app.initialize_functions import initialize_route, initialize_db, initialize_swagger
import pandas as pd
from sentence_transformers import SentenceTransformer
from sklearn.metrics.pairwise import cosine_similarity

def create_app(config=None) -> Flask:

    app = Flask(__name__)
    @app.route("/register", methods=["POST"])
    def register():
        data = request.get_json()
        
        username = data.get("username", "").strip()
        password = data.get("password", "").strip()
        
        if not username or not password:
            return jsonify({"error": "Username and password are required"}), 400
        
        existing_user = User.query.filter_by(username=username).first()
        if existing_user:
            return jsonify({"error": "Username already exists"}), 400
        
        password_hash = generate_password_hash(password)
        
        new_user = User(username=username, password_hash=password_hash)
        db.session.add(new_user)
        db.session.commit()
        
        return jsonify({"message": "User registered successfully"}), 201
    
    @app.route("/login", methods=[GET, "POST"])
    def login():
        if request.method == "GET":
            return render_template("login_page,html")
        
        data = request.get_json()
        
        username = data.get("username", "").strip()
        password = data.get("password", "")
        
        user = user.query.filter_by(username=username).first()
        
        if user and check_password_hash(user.password_hash, password):
            session["user_id"] = user.id
            session["username"] = user.username
            
            return jsonify({
                "message": "Login Successful",
                "username": user.username,
            })
        
        return jsonify({"error": "Incorrect username or password"}), 401
    df = pd.read_csv("app/data/skyrim_items.csv")
    df.columns = df.columns.str.strip()

    df["item_weight"] = df["item_weight"].fillna("Unknown").astype(str)
    df["item_value"] = df["item_value"].fillna("Unknown").astype(str)

    model = SentenceTransformer('all-MiniLM-L6-v2')

    item_texts = (
        df["item_name"].astype(str) + " " +
        df["category"].astype(str) + " " +
        df["item_type"].astype(str) + " " +
        df["rarity"].astype(str) + " " +
        df["effect"].astype(str) + " " +
        df["quest"].astype(str) + " " +
        df["location"].astype(str) + " " +
        df["dlc"].astype(str) + " " +
        df["tags"].astype(str)
)
    
    item_embeddings = model.encode(item_texts.tolist())

    @app.route("/")
    def home():
        return render_template("Html_project.html")

    @app.route("/items")
    def items():
        return render_template("item_page.html")

    @app.route("/storage")
    def storage():
        return render_template("storage_page.html")

    @app.route("/questlines")
    def questlines():
        return render_template("questline_page.html")
   
    @app.route("/search")
    def search():
        query = request.args.get("q", "")

        query_embedding = model.encode([query])
        scores = cosine_similarity(query_embedding, item_embeddings)[0]

        df['score'] = scores
        results = df.sort_values('score', ascending=False).head(5)
        return jsonify(
            results[
                [
                    "item_name",
                    "category",
                    "item_type",
                    "rarity",
                    "effect",
                    "quest",
                    "location",
                    "dlc",
                    "item_weight",
                    "item_value",
                    "image",
                    "tags",
                    "score"
                ]
            ].to_dict(orient="records")
        )
    
    if config:
        app.config.from_object(get_config_by_name(config))

    initialize_db(app)

    initialize_route(app)

    initialize_swagger(app)

    return app