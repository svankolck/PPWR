import os
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager

db = SQLAlchemy()
login_manager = LoginManager()


def create_app(config_name=None):
    app = Flask(__name__)

    # Configuration
    app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'dev-secret-key-change-in-production')
    db_path = os.environ.get('DATABASE_URL', 'sqlite:///' + os.path.join(os.path.abspath(os.path.dirname(__file__)), '..', 'ppwr.db'))
    app.config['SQLALCHEMY_DATABASE_URI'] = db_path
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    app.config['UPLOAD_FOLDER'] = os.path.join(os.path.abspath(os.path.dirname(__file__)), '..', 'uploads')
    app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max upload

    if config_name == 'testing':
        app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'
        app.config['TESTING'] = True
        app.config['WTF_CSRF_ENABLED'] = False

    # Initialize extensions
    db.init_app(app)
    login_manager.init_app(app)
    login_manager.login_view = 'auth.login'

    # Register blueprints
    from app.routes.auth import auth_bp
    from app.routes.dashboard import dashboard_bp
    from app.routes.packaging import packaging_bp
    from app.routes.suppliers import suppliers_bp
    from app.routes.documents import documents_bp
    from app.routes.requirements import requirements_bp
    from app.routes.gaps import gaps_bp
    from app.routes.tasks import tasks_bp
    from app.routes.dossier import dossier_bp
    from app.routes.components import components_bp

    app.register_blueprint(auth_bp)
    app.register_blueprint(dashboard_bp)
    app.register_blueprint(packaging_bp)
    app.register_blueprint(suppliers_bp)
    app.register_blueprint(documents_bp)
    app.register_blueprint(requirements_bp)
    app.register_blueprint(gaps_bp)
    app.register_blueprint(tasks_bp)
    app.register_blueprint(dossier_bp)
    app.register_blueprint(components_bp)

    # Create tables and seed on first run
    with app.app_context():
        from app.models import user, packaging, supplier, document, requirement, gap, task, audit_log
        from app.models.user import User
        db.create_all()

        # Ensure upload directory exists
        os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

        # Auto-seed if database is empty (first run)
        if config_name != 'testing' and User.query.count() == 0:
            from seeds.seed_data import seed_into_db
            seed_into_db(db)

    return app
