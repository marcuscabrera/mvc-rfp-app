from flask import Blueprint, request, jsonify, send_file, current_app
from flask_jwt_extended import jwt_required, get_jwt_identity
from werkzeug.utils import secure_filename
import os
import hashlib
import mimetypes
from datetime import datetime
import uuid
from src.models.user import User, db
from src.models.document import Document
from src.models.project import Project

documents_bp = Blueprint('documents', __name__)

ALLOWED_EXTENSIONS = {'pdf', 'doc', 'docx', 'txt', 'rtf'}

def allowed_file(filename):
    """Verifica se o arquivo tem extensão permitida"""
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def calculate_file_hash(file_path):
    """Calcula hash SHA-256 do arquivo"""
    hash_sha256 = hashlib.sha256()
    with open(file_path, "rb") as f:
        for chunk in iter(lambda: f.read(4096), b""):
            hash_sha256.update(chunk)
    return hash_sha256.hexdigest()

@documents_bp.route('', methods=['POST'])
@jwt_required()
def upload_document():
    """Upload de documento"""
    try:
        user_id = get_jwt_identity()
        user = User.query.get(user_id)
        
        if not user or not user.is_active:
            return jsonify({
                'error': {
                    'code': 'USER_NOT_FOUND',
                    'message': 'Usuário não encontrado ou inativo'
                }
            }), 404
        
        # Verificar se arquivo foi enviado
        if 'file' not in request.files:
            return jsonify({
                'error': {
                    'code': 'NO_FILE',
                    'message': 'Nenhum arquivo foi enviado'
                }
            }), 400
        
        file = request.files['file']
        if file.filename == '':
            return jsonify({
                'error': {
                    'code': 'NO_FILE_SELECTED',
                    'message': 'Nenhum arquivo foi selecionado'
                }
            }), 400
        
        # Validar extensão do arquivo
        if not allowed_file(file.filename):
            return jsonify({
                'error': {
                    'code': 'INVALID_FILE_TYPE',
                    'message': f'Tipo de arquivo não permitido. Extensões aceitas: {", ".join(ALLOWED_EXTENSIONS)}'
                }
            }), 400
        
        # Obter parâmetros adicionais
        project_id = request.form.get('project_id')
        document_type = request.form.get('document_type', 'rfp')
        name = request.form.get('name', file.filename)
        
        # Validar projeto se fornecido
        if project_id:
            project = Project.query.filter_by(
                id=project_id,
                organization_id=user.organization_id,
                is_active=True
            ).first()
            if not project:
                return jsonify({
                    'error': {
                        'code': 'PROJECT_NOT_FOUND',
                        'message': 'Projeto não encontrado'
                    }
                }), 404
        
        # Criar diretório de upload se não existir
        upload_folder = current_app.config['UPLOAD_FOLDER']
        org_folder = os.path.join(upload_folder, str(user.organization_id))
        os.makedirs(org_folder, exist_ok=True)
        
        # Gerar nome único para o arquivo
        filename = secure_filename(file.filename)
        unique_filename = f"{uuid.uuid4()}_{filename}"
        file_path = os.path.join(org_folder, unique_filename)
        
        # Salvar arquivo
        file.save(file_path)
        
        # Calcular informações do arquivo
        file_size = os.path.getsize(file_path)
        file_hash = calculate_file_hash(file_path)
        mime_type = mimetypes.guess_type(file_path)[0] or 'application/octet-stream'
        
        # Verificar se arquivo já existe (baseado no hash)
        existing_doc = Document.query.filter_by(
            organization_id=user.organization_id,
            file_hash=file_hash,
            is_active=True
        ).first()
        
        if existing_doc:
            # Remover arquivo duplicado
            os.remove(file_path)
            return jsonify({
                'error': {
                    'code': 'DUPLICATE_FILE',
                    'message': 'Arquivo já existe no sistema',
                    'existing_document': existing_doc.to_dict()
                }
            }), 409
        
        # Criar registro no banco de dados
        document = Document(
            organization_id=user.organization_id,
            project_id=project_id if project_id else None,
            name=name,
            original_filename=filename,
            file_path=file_path,
            file_size=file_size,
            mime_type=mime_type,
            file_hash=file_hash,
            document_type=document_type,
            uploaded_by=user.id
        )
        
        db.session.add(document)
        db.session.commit()
        
        # TODO: Iniciar processamento assíncrono do documento
        # process_document_async.delay(document.id)
        
        return jsonify(document.to_dict()), 201
    
    except Exception as e:
        db.session.rollback()
        return jsonify({
            'error': {
                'code': 'UPLOAD_ERROR',
                'message': 'Erro ao fazer upload do documento',
                'details': str(e)
            }
        }), 500

@documents_bp.route('', methods=['GET'])
@jwt_required()
def list_documents():
    """Listar documentos"""
    try:
        user_id = get_jwt_identity()
        user = User.query.get(user_id)
        
        if not user or not user.is_active:
            return jsonify({
                'error': {
                    'code': 'USER_NOT_FOUND',
                    'message': 'Usuário não encontrado ou inativo'
                }
            }), 404
        
        # Parâmetros de consulta
        page = request.args.get('page', 1, type=int)
        limit = min(request.args.get('limit', 20, type=int), 100)
        project_id = request.args.get('project_id')
        document_type = request.args.get('document_type')
        processing_status = request.args.get('processing_status')
        search = request.args.get('search')
        
        # Construir consulta
        query = Document.query.filter_by(
            organization_id=user.organization_id,
            is_active=True
        )
        
        if project_id:
            query = query.filter_by(project_id=project_id)
        
        if document_type:
            query = query.filter_by(document_type=document_type)
        
        if processing_status:
            query = query.filter_by(processing_status=processing_status)
        
        if search:
            query = query.filter(
                Document.name.ilike(f'%{search}%') |
                Document.original_filename.ilike(f'%{search}%')
            )
        
        # Paginação
        documents = query.order_by(Document.uploaded_at.desc()).paginate(
            page=page, per_page=limit, error_out=False
        )
        
        return jsonify({
            'data': [doc.to_dict() for doc in documents.items],
            'pagination': {
                'page': page,
                'limit': limit,
                'total': documents.total,
                'pages': documents.pages
            }
        })
    
    except Exception as e:
        return jsonify({
            'error': {
                'code': 'LIST_ERROR',
                'message': 'Erro ao listar documentos',
                'details': str(e)
            }
        }), 500

@documents_bp.route('/<document_id>', methods=['GET'])
@jwt_required()
def get_document(document_id):
    """Obter detalhes de um documento"""
    try:
        user_id = get_jwt_identity()
        user = User.query.get(user_id)
        
        if not user or not user.is_active:
            return jsonify({
                'error': {
                    'code': 'USER_NOT_FOUND',
                    'message': 'Usuário não encontrado ou inativo'
                }
            }), 404
        
        document = Document.query.filter_by(
            id=document_id,
            organization_id=user.organization_id,
            is_active=True
        ).first()
        
        if not document:
            return jsonify({
                'error': {
                    'code': 'DOCUMENT_NOT_FOUND',
                    'message': 'Documento não encontrado'
                }
            }), 404
        
        return jsonify(document.to_dict())
    
    except Exception as e:
        return jsonify({
            'error': {
                'code': 'GET_DOCUMENT_ERROR',
                'message': 'Erro ao obter documento',
                'details': str(e)
            }
        }), 500

@documents_bp.route('/<document_id>/download', methods=['GET'])
@jwt_required()
def download_document(document_id):
    """Download de documento"""
    try:
        user_id = get_jwt_identity()
        user = User.query.get(user_id)
        
        if not user or not user.is_active:
            return jsonify({
                'error': {
                    'code': 'USER_NOT_FOUND',
                    'message': 'Usuário não encontrado ou inativo'
                }
            }), 404
        
        document = Document.query.filter_by(
            id=document_id,
            organization_id=user.organization_id,
            is_active=True
        ).first()
        
        if not document:
            return jsonify({
                'error': {
                    'code': 'DOCUMENT_NOT_FOUND',
                    'message': 'Documento não encontrado'
                }
            }), 404
        
        if not os.path.exists(document.file_path):
            return jsonify({
                'error': {
                    'code': 'FILE_NOT_FOUND',
                    'message': 'Arquivo físico não encontrado'
                }
            }), 404
        
        return send_file(
            document.file_path,
            as_attachment=True,
            download_name=document.original_filename,
            mimetype=document.mime_type
        )
    
    except Exception as e:
        return jsonify({
            'error': {
                'code': 'DOWNLOAD_ERROR',
                'message': 'Erro ao fazer download do documento',
                'details': str(e)
            }
        }), 500

@documents_bp.route('/<document_id>/text', methods=['GET'])
@jwt_required()
def get_document_text(document_id):
    """Obter texto extraído do documento"""
    try:
        user_id = get_jwt_identity()
        user = User.query.get(user_id)
        
        if not user or not user.is_active:
            return jsonify({
                'error': {
                    'code': 'USER_NOT_FOUND',
                    'message': 'Usuário não encontrado ou inativo'
                }
            }), 404
        
        document = Document.query.filter_by(
            id=document_id,
            organization_id=user.organization_id,
            is_active=True
        ).first()
        
        if not document:
            return jsonify({
                'error': {
                    'code': 'DOCUMENT_NOT_FOUND',
                    'message': 'Documento não encontrado'
                }
            }), 404
        
        if document.processing_status != 'completed':
            return jsonify({
                'error': {
                    'code': 'DOCUMENT_NOT_PROCESSED',
                    'message': 'Documento ainda não foi processado'
                }
            }), 400
        
        return jsonify({
            'extracted_text': document.extracted_text,
            'word_count': document.word_count,
            'language': document.language
        })
    
    except Exception as e:
        return jsonify({
            'error': {
                'code': 'GET_TEXT_ERROR',
                'message': 'Erro ao obter texto do documento',
                'details': str(e)
            }
        }), 500

