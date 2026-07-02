from flask import Flask, jsonify, render_template, request
from app.config.config import get_config_by_name
from app.initialize_functions import initialize_route, initialize_db, initialize_swagger
import pandas as pd
from sentence_transformers import SentenceTransformer
from sklearn.metrics.pairwise import cosine_similarity

def create_app(config=None) -> Flask:

    app = Flask(__name__)

    df = pd.read_csv("app/data/skyrim_items.csv")

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

    @app.route("/login")
    def login():
        return render_template("login_page.html")
   
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