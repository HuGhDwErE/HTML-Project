from pathlib import Path
import secrets
from flask import Flask, jsonify, render_template, request
from app.config.config import get_config_by_name
from app.initialize_functions import initialize_route, initialize_db, initialize_swagger
from app.auth import initialize_auth, login_required
from app.admin import initialize_admin
from app.appeals import initialize_appeals


def create_app(config=None) -> Flask:
    app = Flask(__name__)
    app.config.from_object(get_config_by_name(config if isinstance(config, str) else "development"))
    if isinstance(config, dict):
        app.config.update(config)
    if not app.config.get("SECRET_KEY"):
        if config == "production":
            raise RuntimeError("Set SECRET_KEY to a strong random value before running production.")
        Path(app.instance_path).mkdir(parents=True, exist_ok=True)
        secret_path = Path(app.instance_path) / "secret.key"
        try:
            with secret_path.open("x") as secret_file:
                secret_file.write(secrets.token_hex(32))
        except FileExistsError:
            pass
        app.config["SECRET_KEY"] = secret_path.read_text().strip()
    initialize_db(app)
    initialize_auth(app)
    initialize_admin(app)
    initialize_appeals(app)
    search_data = None

    def load_search():
        import pandas as pd
        from sentence_transformers import SentenceTransformer
        df = pd.read_csv(Path(app.root_path) / "data" / "skyrim_items.csv")
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
        return df, model, item_embeddings

    @app.route("/")
    def home():
        return render_template("Html_project.html")

    @app.route("/items")
    def items():
        return render_template("item_page.html")

    @app.route("/storage")
    @login_required
    def storage():
        return render_template("storage_page.html")

    @app.route("/questlines")
    def questlines():
        return render_template("questline_page.html")

    @app.route("/search")
    def search():
        from sklearn.metrics.pairwise import cosine_similarity
        nonlocal search_data
        if search_data is None:
            search_data = load_search()
        df, model, item_embeddings = search_data
        query = request.args.get("q", "")

        query_embedding = model.encode([query])
        scores = cosine_similarity(query_embedding, item_embeddings)[0]

        df = df.assign(score=scores)
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

    initialize_route(app)
    initialize_swagger(app)
    return app
