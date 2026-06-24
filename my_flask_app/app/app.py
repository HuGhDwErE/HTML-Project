from flask import Flask, Request, jsonify, render_template, request
from app.config.config import get_config_by_name
from app.initialize_functions import initialize_route, initialize_db, initialize_swagger
import pandas as pd
from sentence_transformers import SentenceTransformer
from sklearn.metrics.pairwise import cosine_similarity

def create_app(config=None) -> Flask:

    app = Flask(__name__)
    data ={
        "item_name": [
            "daedric Boots of fire suppression",
            "Ebony Armor of Peerless Destruction:",
            "Ring of Eminent Fortify Magicka:",
            "Iron Sword of Burning",
            "Glass Shield of Grounding",
        ],
        "description": [
            "Increases fire resistance by 50%. Heavy Armor boots.",
            "Destruction Spells cost 20% less magicka. Heavy Armor chestplate.",
            "Increases magicka by 40 points. Jewelry.",
            "Adds 10 points of fire damage. One-handed weapon.",
            "Reduces shock damage by 40%. Light Armor shield.",
        ]
    }

    df = pd.DataFrame(data)

    model = SentenceTransformer('all-MiniLM-L6-v2')
    item_texts = df['item_name'] + "" + df['description']
    item_embeddings = model.encode(item_texts.tolist())

    @app.route("/")
    def home():
        return render_template("item_page.html")
   
    @app.route("/search")
    def search():
        query = Request.args.get("q", "")

        query_embedding = model.encode([query])
        scores = cosine_similarity(query_embedding, item_embeddings)[0]

        df['score'] = scores
        results = df.sort_values('score', ascending=False).head(5)
        return jsonify(results[["item_name", "description", "score"]].to_dict(orient="records"))
    
    if __name__ == "__main__":
        app.run(debug=True)

    
    if config:
        app.config.from_object(get_config_by_name(config))

    initialize_db(app)

    initialize_route(app)

    initialize_swagger(app)

    return app
