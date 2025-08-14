from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from src.models.user import User, db
from src.models.role import Role, UserRole

users_bp = Blueprint('users', __name__)

@users_bp.route('', methods=['GET'])
@jwt_required()
def list_users():
    """Listar usuários da organização"""
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
        
        # Verificar permissão
        if not user.has_permission('view_users'):
            return jsonify({
                'error': {
                    'code': 'INSUFFICIENT_PERMISSIONS',
                    'message': 'Usuário não tem permissão para visualizar outros usuários'
                }
            }), 403
        
        # Parâmetros de consulta
        page = request.args.get('page', 1, type=int)
        limit = min(request.args.get('limit', 20, type=int), 100)
        search = request.args.get('search')
        role = request.args.get('role')
        
        # Construir consulta
        query = User.query.filter_by(
            organization_id=user.organization_id,
            is_active=True
        )
        
        if search:
            query = query.filter(
                User.first_name.ilike(f'%{search}%') |
                User.last_name.ilike(f'%{search}%') |
                User.email.ilike(f'%{search}%')
            )
        
        if role:
            query = query.join(UserRole).join(Role).filter(
                Role.name == role,
                UserRole.is_active == True
            )
        
        # Paginação
        users = query.order_by(User.created_at.desc()).paginate(
            page=page, per_page=limit, error_out=False
        )
        
        # Incluir papéis dos usuários
        result_data = []
        for u in users.items:
            user_data = u.to_dict()
            roles = [role.name for role in u.get_roles()]
            user_data['roles'] = roles
            result_data.append(user_data)
        
        return jsonify({
            'data': result_data,
            'pagination': {
                'page': page,
                'limit': limit,
                'total': users.total,
                'pages': users.pages
            }
        })
    
    except Exception as e:
        return jsonify({
            'error': {
                'code': 'LIST_ERROR',
                'message': 'Erro ao listar usuários',
                'details': str(e)
            }
        }), 500

@users_bp.route('/me', methods=['GET'])
@jwt_required()
def get_current_user():
    """Obter perfil do usuário atual"""
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
        
        user_data = user.to_dict()
        roles = [role.name for role in user.get_roles()]
        user_data['roles'] = roles
        
        return jsonify(user_data)
    
    except Exception as e:
        return jsonify({
            'error': {
                'code': 'GET_USER_ERROR',
                'message': 'Erro ao obter perfil do usuário',
                'details': str(e)
            }
        }), 500

@users_bp.route('/me', methods=['PATCH'])
@jwt_required()
def update_current_user():
    """Atualizar perfil do usuário atual"""
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
        
        # Atualizar campos permitidos
        if 'job_title' in data:
            user.job_title = data['job_title']
        
        if 'department' in data:
            user.department = data['department']
        
        if 'phone' in data:
            user.phone = data['phone']
        
        if 'timezone' in data:
            user.timezone = data['timezone']
        
        if 'language' in data:
            user.language = data['language']
        
        if 'preferences' in data:
            # Mesclar preferências existentes com novas
            current_preferences = user.preferences or {}
            new_preferences = data['preferences']
            current_preferences.update(new_preferences)
            user.preferences = current_preferences
        
        db.session.commit()
        
        return jsonify(user.to_dict())
    
    except Exception as e:
        db.session.rollback()
        return jsonify({
            'error': {
                'code': 'UPDATE_ERROR',
                'message': 'Erro ao atualizar perfil do usuário',
                'details': str(e)
            }
        }), 500

