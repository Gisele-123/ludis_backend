from flask import Flask
from .config import Config
from .extensions import db, migrate, jwt, cors, mail
from .auth.routes import auth_bp
from .matches.routes import matches_bp

def create_app():
    app = Flask(__name__)
    app.config.from_object(Config())

    # Init extensions
    db.init_app(app)
    migrate.init_app(app, db)
    jwt.init_app(app)
    cors.init_app(app, resources={r"/*": {"origins": app.config["CORS_ORIGINS"]}}, supports_credentials=True)
    mail.init_app(app)

    # Register blueprints
    app.register_blueprint(auth_bp, url_prefix="/auth")
    app.register_blueprint(matches_bp, url_prefix="/matches")

    @app.get("/health")
    def health():
        return {"status": "ok"}, 200

    return app


