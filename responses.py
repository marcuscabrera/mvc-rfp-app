from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from datetime import datetime
from src.models.user import User, db
from src.models.question import Question
from src.models.response import Response
from src.models.project import Project
from src.models.knowledge_base import KnowledgeBase
from src.services.ai_service import ai_service

responses_bp = Blueprint('responses', __name__)

@responses_bp.route('', methods=['GET'])
@jwt_required()
def list_responses():
    """Listar respostas"""
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
        question_id = request.args.get('question_id')
        status = request.args.get('status')
        response_type = request.args.get('response_type')
        
        # Construir consulta
        query = Response.query.join(Question).join(Project).filter(
            Project.organization_id == user.organization_id,
            Response.is_active == True
        )
        
        if question_id:
            query = query.filter(Response.question_id == question_id)
        
        if status:
            query = query.filter(Response.status == status)
        
        if response_type:
            query = query.filter(Response.response_type == response_type)
        
        # Paginação
        responses = query.order_by(Response.created_at.desc()).paginate(
            page=page, per_page=limit, error_out=False
        )
        
        return jsonify({
            'data': [response.to_dict() for response in responses.items],
            'pagination': {
                'page': page,
                'limit': limit,
                'total': responses.total,
                'pages': responses.pages
            }
        })
    
    except Exception as e:
        return jsonify({
            'error': {
                'code': 'LIST_ERROR',
                'message': 'Erro ao listar respostas',
                'details': str(e)
            }
        }), 500

@responses_bp.route('/<response_id>', methods=['GET'])
@jwt_required()
def get_response(response_id):
    """Obter detalhes de uma resposta"""
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
        
        response = Response.query.join(Question).join(Project).filter(
            Response.id == response_id,
            Project.organization_id == user.organization_id,
            Response.is_active == True
        ).first()
        
        if not response:
            return jsonify({
                'error': {
                    'code': 'RESPONSE_NOT_FOUND',
                    'message': 'Resposta não encontrada'
                }
            }), 404
        
        return jsonify(response.to_dict())
    
    except Exception as e:
        return jsonify({
            'error': {
                'code': 'GET_RESPONSE_ERROR',
                'message': 'Erro ao obter resposta',
                'details': str(e)
            }
        }), 500

@responses_bp.route('/generate/<question_id>', methods=['POST'])
@jwt_required()
def generate_response(question_id):
    """Gerar resposta para uma pergunta"""
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
        
        # Buscar pergunta
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
        
        # Obter parâmetros
        data = request.get_json() or {}
        ai_model = data.get('ai_model', 'gemini')
        use_knowledge_base = data.get('use_knowledge_base', True)
        max_words = data.get('max_words', question.max_words)
        tone = data.get('tone', 'professional')
        include_sources = data.get('include_sources', True)
        
        # Buscar documentos de contexto na base de conhecimento
        context_documents = []
        if use_knowledge_base:
            # Buscar documentos relevantes baseados nas palavras-chave da pergunta
            keywords = question.keywords or []
            if keywords:
                kb_items = KnowledgeBase.query.filter(
                    KnowledgeBase.organization_id == user.organization_id,
                    KnowledgeBase.is_active == True
                ).all()
                
                # Implementação simplificada de busca por relevância
                for item in kb_items[:3]:  # Limitar a 3 documentos
                    context_documents.append(f"Título: {item.title}\nConteúdo: {item.content[:500]}...")
                    if include_sources:
                        item.increment_usage()
        
        # Gerar resposta usando IA
        ai_response = ai_service.generate_response(
            question.question_text,
            context_documents,
            max_words,
            tone,
            question.document.language if question.document else 'pt-BR'
        )
        
        # Desmarcar resposta atual anterior
        current_response = question.get_current_response()
        if current_response:
            current_response.is_current = False
        
        # Criar nova resposta
        response = Response(
            question_id=question.id,
            response_text=ai_response['response_text'],
            response_type='generated',
            word_count=ai_response['word_count'],
            character_count=ai_response['character_count'],
            source_documents=ai_response.get('source_documents', []),
            confidence_score=ai_response.get('confidence_score'),
            generated_by=ai_response.get('generated_by'),
            generated_at=ai_response.get('generated_at'),
            created_by=user.id,
            status='draft',
            is_current=True
        )
        
        db.session.add(response)
        db.session.commit()
        
        return jsonify(response.to_dict()), 201
    
    except Exception as e:
        db.session.rollback()
        return jsonify({
            'error': {
                'code': 'GENERATION_ERROR',
                'message': 'Erro ao gerar resposta',
                'details': str(e)
            }
        }), 500

@responses_bp.route('/<response_id>', methods=['PATCH'])
@jwt_required()
def update_response(response_id):
    """Atualizar resposta"""
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
        
        response = Response.query.join(Question).join(Project).filter(
            Response.id == response_id,
            Project.organization_id == user.organization_id,
            Response.is_active == True
        ).first()
        
        if not response:
            return jsonify({
                'error': {
                    'code': 'RESPONSE_NOT_FOUND',
                    'message': 'Resposta não encontrada'
                }
            }), 404
        
        data = request.get_json()
        
        # Atualizar campos permitidos
        if 'response_text' in data:
            response.response_text = data['response_text']
            response.calculate_word_count()
            
            # Se o texto foi editado, marcar como híbrido
            if response.response_type == 'generated':
                response.response_type = 'hybrid'
        
        if 'status' in data:
            response.status = data['status']
        
        db.session.commit()
        
        return jsonify(response.to_dict())
    
    except Exception as e:
        db.session.rollback()
        return jsonify({
            'error': {
                'code': 'UPDATE_ERROR',
                'message': 'Erro ao atualizar resposta',
                'details': str(e)
            }
        }), 500

@responses_bp.route('/<response_id>/approve', methods=['POST'])
@jwt_required()
def approve_response(response_id):
    """Aprovar resposta"""
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
        
        response = Response.query.join(Question).join(Project).filter(
            Response.id == response_id,
            Project.organization_id == user.organization_id,
            Response.is_active == True
        ).first()
        
        if not response:
            return jsonify({
                'error': {
                    'code': 'RESPONSE_NOT_FOUND',
                    'message': 'Resposta não encontrada'
                }
            }), 404
        
        data = request.get_json() or {}
        
        # Aprovar resposta
        response.status = 'approved'
        response.approved_by = user.id
        response.approved_at = datetime.utcnow()
        
        db.session.commit()
        
        return jsonify({
            'message': 'Resposta aprovada com sucesso',
            'response': response.to_dict()
        })
    
    except Exception as e:
        db.session.rollback()
        return jsonify({
            'error': {
                'code': 'APPROVAL_ERROR',
                'message': 'Erro ao aprovar resposta',
                'details': str(e)
            }
        }), 500

@responses_bp.route('/<response_id>/reject', methods=['POST'])
@jwt_required()
def reject_response(response_id):
    """Rejeitar resposta"""
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
        
        response = Response.query.join(Question).join(Project).filter(
            Response.id == response_id,
            Project.organization_id == user.organization_id,
            Response.is_active == True
        ).first()
        
        if not response:
            return jsonify({
                'error': {
                    'code': 'RESPONSE_NOT_FOUND',
                    'message': 'Resposta não encontrada'
                }
            }), 404
        
        data = request.get_json() or {}
        
        # Rejeitar resposta
        response.status = 'rejected'
        response.reviewed_by = user.id
        response.reviewed_at = datetime.utcnow()
        
        db.session.commit()
        
        return jsonify({
            'message': 'Resposta rejeitada',
            'response': response.to_dict()
        })
    
    except Exception as e:
        db.session.rollback()
        return jsonify({
            'error': {
                'code': 'REJECTION_ERROR',
                'message': 'Erro ao rejeitar resposta',
                'details': str(e)
            }
        }), 500

@responses_bp.route('/question/<question_id>/versions', methods=['GET'])
@jwt_required()
def get_response_versions(question_id):
    """Listar versões de resposta para uma pergunta"""
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
        
        # Buscar pergunta
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
        
        # Obter versões
        current_response = question.get_current_response()
        history = question.get_response_history()
        
        result = {
            'current': current_response.to_dict() if current_response else None,
            'history': [r.to_dict() for r in history if not r.is_current]
        }
        
        return jsonify(result)
    
    except Exception as e:
        return jsonify({
            'error': {
                'code': 'GET_VERSIONS_ERROR',
                'message': 'Erro ao obter versões da resposta',
                'details': str(e)
            }
        }), 500

