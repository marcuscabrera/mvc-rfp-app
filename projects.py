from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from datetime import datetime
from src.models.user import User, db
from src.models.project import Project

projects_bp = Blueprint('projects', __name__)

@projects_bp.route('', methods=['GET'])
@jwt_required()
def list_projects():
    """Listar projetos"""
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
        status = request.args.get('status')
        search = request.args.get('search')
        sort = request.args.get('sort', 'created_at:desc')
        
        # Construir consulta
        query = Project.query.filter_by(
            organization_id=user.organization_id,
            is_active=True
        )
        
        if status:
            query = query.filter_by(status=status)
        
        if search:
            query = query.filter(
                Project.name.ilike(f'%{search}%') |
                Project.client_name.ilike(f'%{search}%') |
                Project.description.ilike(f'%{search}%')
            )
        
        # Ordenação
        if sort:
            sort_field, sort_order = sort.split(':') if ':' in sort else (sort, 'asc')
            if hasattr(Project, sort_field):
                order_by = getattr(Project, sort_field)
                if sort_order.lower() == 'desc':
                    order_by = order_by.desc()
                query = query.order_by(order_by)
        
        # Paginação
        projects = query.paginate(page=page, per_page=limit, error_out=False)
        
        # Incluir estatísticas dos projetos
        result_data = []
        for project in projects.items:
            project_data = project.to_dict()
            
            # Adicionar informações do criador e responsável
            if project.creator:
                project_data['created_by'] = {
                    'id': str(project.creator.id),
                    'name': project.creator.display_name
                }
            
            if project.assignee:
                project_data['assigned_to'] = {
                    'id': str(project.assignee.id),
                    'name': project.assignee.display_name
                }
            
            # Adicionar estatísticas
            project_data['stats'] = project.get_stats()
            
            result_data.append(project_data)
        
        return jsonify({
            'data': result_data,
            'pagination': {
                'page': page,
                'limit': limit,
                'total': projects.total,
                'pages': projects.pages
            }
        })
    
    except Exception as e:
        return jsonify({
            'error': {
                'code': 'LIST_ERROR',
                'message': 'Erro ao listar projetos',
                'details': str(e)
            }
        }), 500

@projects_bp.route('', methods=['POST'])
@jwt_required()
def create_project():
    """Criar novo projeto"""
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
        
        # Validar dados obrigatórios
        if not data.get('name'):
            return jsonify({
                'error': {
                    'code': 'MISSING_NAME',
                    'message': 'Nome do projeto é obrigatório'
                }
            }), 400
        
        # Validar usuário responsável se fornecido
        assigned_to = None
        if data.get('assigned_to'):
            assigned_user = User.query.filter_by(
                id=data['assigned_to'],
                organization_id=user.organization_id,
                is_active=True
            ).first()
            if not assigned_user:
                return jsonify({
                    'error': {
                        'code': 'INVALID_ASSIGNEE',
                        'message': 'Usuário responsável não encontrado'
                    }
                }), 400
            assigned_to = assigned_user.id
        
        # Criar projeto
        project = Project(
            organization_id=user.organization_id,
            name=data['name'],
            description=data.get('description'),
            rfp_title=data.get('rfp_title'),
            client_name=data.get('client_name'),
            submission_deadline=datetime.fromisoformat(data['submission_deadline'].replace('Z', '+00:00')) if data.get('submission_deadline') else None,
            estimated_value=data.get('estimated_value'),
            currency=data.get('currency', 'BRL'),
            priority=data.get('priority', 'medium'),
            tags=data.get('tags', []),
            metadata=data.get('metadata', {}),
            created_by=user.id,
            assigned_to=assigned_to
        )
        
        db.session.add(project)
        db.session.commit()
        
        return jsonify(project.to_dict()), 201
    
    except Exception as e:
        db.session.rollback()
        return jsonify({
            'error': {
                'code': 'CREATE_ERROR',
                'message': 'Erro ao criar projeto',
                'details': str(e)
            }
        }), 500

@projects_bp.route('/<project_id>', methods=['GET'])
@jwt_required()
def get_project(project_id):
    """Obter detalhes de um projeto"""
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
        
        project_data = project.to_dict()
        
        # Adicionar informações detalhadas
        if project.creator:
            project_data['created_by'] = {
                'id': str(project.creator.id),
                'name': project.creator.display_name,
                'email': project.creator.email
            }
        
        if project.assignee:
            project_data['assigned_to'] = {
                'id': str(project.assignee.id),
                'name': project.assignee.display_name,
                'email': project.assignee.email
            }
        
        # Adicionar estatísticas
        project_data['stats'] = project.get_stats()
        
        return jsonify(project_data)
    
    except Exception as e:
        return jsonify({
            'error': {
                'code': 'GET_PROJECT_ERROR',
                'message': 'Erro ao obter projeto',
                'details': str(e)
            }
        }), 500

@projects_bp.route('/<project_id>', methods=['PATCH'])
@jwt_required()
def update_project(project_id):
    """Atualizar projeto"""
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
        
        data = request.get_json()
        
        # Atualizar campos permitidos
        if 'name' in data:
            project.name = data['name']
        
        if 'description' in data:
            project.description = data['description']
        
        if 'rfp_title' in data:
            project.rfp_title = data['rfp_title']
        
        if 'client_name' in data:
            project.client_name = data['client_name']
        
        if 'submission_deadline' in data:
            if data['submission_deadline']:
                project.submission_deadline = datetime.fromisoformat(data['submission_deadline'].replace('Z', '+00:00'))
            else:
                project.submission_deadline = None
        
        if 'estimated_value' in data:
            project.estimated_value = data['estimated_value']
        
        if 'currency' in data:
            project.currency = data['currency']
        
        if 'priority' in data:
            project.priority = data['priority']
        
        if 'status' in data:
            project.status = data['status']
        
        if 'tags' in data:
            project.tags = data['tags']
        
        if 'metadata' in data:
            # Mesclar metadados existentes com novos
            current_metadata = project.metadata or {}
            new_metadata = data['metadata']
            current_metadata.update(new_metadata)
            project.metadata = current_metadata
        
        if 'assigned_to' in data:
            if data['assigned_to']:
                assigned_user = User.query.filter_by(
                    id=data['assigned_to'],
                    organization_id=user.organization_id,
                    is_active=True
                ).first()
                if not assigned_user:
                    return jsonify({
                        'error': {
                            'code': 'INVALID_ASSIGNEE',
                            'message': 'Usuário responsável não encontrado'
                        }
                    }), 400
                project.assigned_to = assigned_user.id
            else:
                project.assigned_to = None
        
        db.session.commit()
        
        return jsonify(project.to_dict())
    
    except Exception as e:
        db.session.rollback()
        return jsonify({
            'error': {
                'code': 'UPDATE_ERROR',
                'message': 'Erro ao atualizar projeto',
                'details': str(e)
            }
        }), 500

@projects_bp.route('/<project_id>', methods=['DELETE'])
@jwt_required()
def delete_project(project_id):
    """Excluir projeto (soft delete)"""
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
        
        # Verificar permissão (apenas criador ou admin pode excluir)
        if project.created_by != user.id and not user.has_permission('delete_projects'):
            return jsonify({
                'error': {
                    'code': 'INSUFFICIENT_PERMISSIONS',
                    'message': 'Usuário não tem permissão para excluir este projeto'
                }
            }), 403
        
        # Soft delete
        project.is_active = False
        
        db.session.commit()
        
        return '', 204
    
    except Exception as e:
        db.session.rollback()
        return jsonify({
            'error': {
                'code': 'DELETE_ERROR',
                'message': 'Erro ao excluir projeto',
                'details': str(e)
            }
        }), 500

