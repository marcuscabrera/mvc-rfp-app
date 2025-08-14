import os
import sys
from dotenv import load_dotenv

# Carregar variáveis de ambiente
load_dotenv()

# DON'T CHANGE THIS !!!
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from flask import Flask, send_from_directory
from flask_cors import CORS
from flask_jwt_extended import JWTManager

# Importar modelos
from src.models.user import db
from src.models.organization import Organization
from src.models.role import Role, UserRole
from src.models.project import Project
from src.models.document import Document
from src.models.question import Question
from src.models.response import Response
from src.models.knowledge_base import KnowledgeBase

# Importar blueprints
from src.routes.auth import auth_bp
from src.routes.organizations import organizations_bp
from src.routes.users import users_bp
from src.routes.projects import projects_bp
from src.routes.documents import documents_bp
from src.routes.questions import questions_bp
from src.routes.responses import responses_bp
from src.routes.knowledge_base import knowledge_base_bp

app = Flask(__name__, static_folder=os.path.join(os.path.dirname(__file__), 'static'))

# Configurações
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', 'asdf#FGSgvasgf$5$WGT')
app.config['JWT_SECRET_KEY'] = os.getenv('JWT_SECRET_KEY', 'jwt-secret-string')
app.config['JWT_ACCESS_TOKEN_EXPIRES'] = int(os.getenv('JWT_ACCESS_TOKEN_EXPIRES', 3600))

# Configuração do banco de dados
database_url = os.getenv('DATABASE_URL', f"sqlite:///{os.path.join(os.path.dirname(__file__), 'database', 'app.db')}")
app.config['SQLALCHEMY_DATABASE_URI'] = database_url
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Configuração de upload
app.config['UPLOAD_FOLDER'] = os.getenv('UPLOAD_FOLDER', 'uploads')
app.config['MAX_CONTENT_LENGTH'] = int(os.getenv('MAX_CONTENT_LENGTH', 104857600))  # 100MB

# Inicializar extensões
CORS(app, origins=os.getenv('CORS_ORIGINS', '*').split(','))
jwt = JWTManager(app)
db.init_app(app)

# Registrar blueprints
app.register_blueprint(auth_bp, url_prefix='/api/auth')
app.register_blueprint(organizations_bp, url_prefix='/api/organizations')
app.register_blueprint(users_bp, url_prefix='/api/users')
app.register_blueprint(projects_bp, url_prefix='/api/projects')
app.register_blueprint(documents_bp, url_prefix='/api/documents')
app.register_blueprint(questions_bp, url_prefix='/api/questions')
app.register_blueprint(responses_bp, url_prefix='/api/responses')
app.register_blueprint(knowledge_base_bp, url_prefix='/api/knowledge-base')

# Criar tabelas
with app.app_context():
    db.create_all()

@app.route('/', defaults={'path': ''})
@app.route('/<path:path>')
def serve(path):
    static_folder_path = app.static_folder
    if static_folder_path is None:
            return "Static folder not configured", 404

    if path != "" and os.path.exists(os.path.join(static_folder_path, path)):
        return send_from_directory(static_folder_path, path)
    else:
        index_path = os.path.join(static_folder_path, 'index.html')
        if os.path.exists(index_path):
            return send_from_directory(static_folder_path, 'index.html')
        else:
            return "index.html not found", 404

@app.route('/api/health')
def health_check():
    return {'status': 'healthy', 'message': 'RFP Automation API is running'}

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
