from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from datetime import datetime
import uuid
from src.models.user import User, db
from src.models.document import Document
from src.models.project import Project
from src.models.question import Question
from src.services.ai_service import ai_service

questions_bp = Blueprint('questions', __name__)

@questions_bp.route('', methods=['GET'])
@jwt_required()
def list_questions():
    """Listar perguntas"""
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
        limit = min(request.args.get('limit', 50, type=int), 100)
        project_id = request.args.get('project_id')
        category = request.args.get('category')
        required = request.args.get('required', type=bool)
        search = request.args.get('search')
        
        # Validar projeto
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
        
        # Construir consulta
        query = Question.query.join(Project).filter(
            Project.organization_id == user.organization_id,
            Question.is_active == True
        )
        
        if project_id:
            query = query.filter(Question.project_id == project_id)
        
        if category:
            query = query.filter(Question.category == category)
        
        if required is not None:
            query = query.filter(Question.required == required)
        
        if search:
            query = query.filter(
                Question.question_text.ilike(f'%{search}%') |
                Question.section.ilike(f'%{search}%')
            )
        
        # Paginação
        questions = query.order_by(Question.extracted_at.desc()).paginate(
            page=page, per_page=limit, error_out=False
        )
        
        # Incluir resposta atual se solicitado
        result_data = []
        for question in questions.items:
            question_data = question.to_dict()
            current_response = question.get_current_response()
            if current_response:
                question_data['response'] = {
                    'id': str(current_response.id),
                    'response_text': current_response.response_text[:200] + '...' if len(current_response.response_text) > 200 else current_response.response_text,
                    'status': current_response.status,
                    'word_count': current_response.word_count,
                    'updated_at': current_response.updated_at.isoformat()
                }
            result_data.append(question_data)
        
        return jsonify({
            'data': result_data,
            'pagination': {
                'page': page,
                'limit': limit,
                'total': questions.total,
                'pages': questions.pages
            }
        })
    
    except Exception as e:
        return jsonify({
            'error': {
                'code': 'LIST_ERROR',
                'message': 'Erro ao listar perguntas',
                'details': str(e)
            }
        }), 500

@questions_bp.route('/<question_id>', methods=['GET'])
@jwt_required()
def get_question(question_id):
    """Obter detalhes de uma pergunta"""
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
        
        question = Question.query.join(Project).filter(
            Question.id == question_id,
            Project.organization_id == user.organization_id,
            Question.is_active == True
        ).first()
        
        if not question:
            return jsonify({
                'error': {
                    'code': 'QUESTION_NOT_FOUND',
                    'message': 'Pergunta não encontrada'
                }
            }), 404
        
        question_data = question.to_dict()
        
        # Incluir resposta atual
        current_response = question.get_current_response()
        if current_response:
            question_data['current_response'] = current_response.to_dict()
        
        # Incluir histórico de respostas se solicitado
        include_history = request.args.get('include_history', 'false').lower() == 'true'
        if include_history:
            history = question.get_response_history()
            question_data['response_history'] = [r.to_dict() for r in history]
        
        return jsonify(question_data)
    
    except Exception as e:
        return jsonify({
            'error': {
                'code': 'GET_QUESTION_ERROR',
                'message': 'Erro ao obter pergunta',
                'details': str(e)
            }
        }), 500

@questions_bp.route('/<question_id>', methods=['PATCH'])
@jwt_required()
def update_question(question_id):
    """Atualizar pergunta (revisão manual)"""
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
        
        question = Question.query.join(Project).filter(
            Question.id == question_id,
            Project.organization_id == user.organization_id,
            Question.is_active == True
        ).first()
        
        if not question:
            return jsonify({
                'error': {
                    'code': 'QUESTION_NOT_FOUND',
                    'message': 'Pergunta não encontrada'
                }
            }), 404
        
        data = request.get_json()
        
        # Atualizar campos permitidos
        if 'question_text' in data:
            question.question_text = data['question_text']
        
        if 'category' in data:
            question.category = data['category']
        
        if 'required' in data:
            question.required = data['required']
        
        if 'max_words' in data:
            question.max_words = data['max_words']
        
        if 'context' in data:
            question.context = data['context']
        
        # Marcar como revisado
        question.reviewed_by = user.id
        question.reviewed_at = datetime.utcnow()
        
        db.session.commit()
        
        return jsonify(question.to_dict())
    
    except Exception as e:
        db.session.rollback()
        return jsonify({
            'error': {
                'code': 'UPDATE_ERROR',
                'message': 'Erro ao atualizar pergunta',
                'details': str(e)
            }
        }), 500

@questions_bp.route('/extract-from-document/<document_id>', methods=['POST'])
@jwt_required()
def extract_questions_from_document(document_id):
    """Processar documento para extrair perguntas"""
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
        
        # Buscar documento
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
        
        if not document.extracted_text:
            return jsonify({
                'error': {
                    'code': 'NO_TEXT_AVAILABLE',
                    'message': 'Texto não disponível para extração'
                }
            }), 400
        
        # Obter parâmetros
        data = request.get_json() or {}
        ai_model = data.get('ai_model', 'gemini')
        language = data.get('language', document.language or 'pt-BR')
        
        # Extrair perguntas usando IA
        extracted_questions = ai_service.extract_questions_from_text(
            document.extracted_text,
            document.document_type,
            language
        )
        
        # Salvar perguntas no banco de dados
        saved_questions = []
        for q_data in extracted_questions:
            question = Question(
                project_id=document.project_id,
                document_id=document.id,
                question_text=q_data['question_text'],
                question_number=q_data.get('question_number'),
                section=q_data.get('section'),
                category=q_data.get('category', 'general'),
                question_type=q_data.get('question_type', 'open'),
                required=q_data.get('required', False),
                max_words=q_data.get('max_words'),
                context=q_data.get('context'),
                keywords=q_data.get('keywords', []),
                confidence_score=q_data.get('confidence_score', 0.8),
                extracted_by=ai_model,
                extracted_at=datetime.utcnow()
            )
            
            db.session.add(question)
            saved_questions.append(question)
        
        db.session.commit()
        
        return jsonify({
            'message': f'{len(saved_questions)} perguntas extraídas com sucesso',
            'questions_count': len(saved_questions),
            'questions': [q.to_dict() for q in saved_questions]
        }), 201
    
    except Exception as e:
        db.session.rollback()
        return jsonify({
            'error': {
                'code': 'EXTRACTION_ERROR',
                'message': 'Erro ao extrair perguntas',
                'details': str(e)
            }
        }), 500

@questions_bp.route('/bulk-extract', methods=['POST'])
@jwt_required()
def bulk_extract_questions():
    """Extrair perguntas de múltiplos documentos"""
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
        
        data = request.get_json()
        document_ids = data.get('document_ids', [])
        
        if not document_ids:
            return jsonify({
                'error': {
                    'code': 'NO_DOCUMENTS',
                    'message': 'Lista de documentos é obrigatória'
                }
            }), 400
        
        results = []
        total_questions = 0
        
        for doc_id in document_ids:
            try:
                # Buscar documento
                document = Document.query.filter_by(
                    id=doc_id,
                    organization_id=user.organization_id,
                    is_active=True
                ).first()
                
                if not document:
                    results.append({
                        'document_id': doc_id,
                        'status': 'error',
                        'message': 'Documento não encontrado'
                    })
                    continue
                
                if document.processing_status != 'completed' or not document.extracted_text:
                    results.append({
                        'document_id': doc_id,
                        'status': 'error',
                        'message': 'Documento não processado ou sem texto'
                    })
                    continue
                
                # Extrair perguntas
                extracted_questions = ai_service.extract_questions_from_text(
                    document.extracted_text,
                    document.document_type,
                    document.language or 'pt-BR'
                )
                
                # Salvar perguntas
                for q_data in extracted_questions:
                    question = Question(
                        project_id=document.project_id,
                        document_id=document.id,
                        question_text=q_data['question_text'],
                        question_number=q_data.get('question_number'),
                        section=q_data.get('section'),
                        category=q_data.get('category', 'general'),
                        question_type=q_data.get('question_type', 'open'),
                        required=q_data.get('required', False),
                        max_words=q_data.get('max_words'),
                        context=q_data.get('context'),
                        keywords=q_data.get('keywords', []),
                        confidence_score=q_data.get('confidence_score', 0.8),
                        extracted_by='gemini',
                        extracted_at=datetime.utcnow()
                    )
                    db.session.add(question)
                
                results.append({
                    'document_id': doc_id,
                    'status': 'success',
                    'questions_count': len(extracted_questions)
                })
                
                total_questions += len(extracted_questions)
            
            except Exception as e:
                results.append({
                    'document_id': doc_id,
                    'status': 'error',
                    'message': str(e)
                })
        
        db.session.commit()
        
        return jsonify({
            'message': f'Processamento concluído. {total_questions} perguntas extraídas.',
            'total_questions': total_questions,
            'results': results
        })
    
    except Exception as e:
        db.session.rollback()
        return jsonify({
            'error': {
                'code': 'BULK_EXTRACTION_ERROR',
                'message': 'Erro no processamento em lote',
                'details': str(e)
            }
        }), 500

