from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from src.models.user import User
from src.models.organization import Organization
from src.extensions.db import db

organizations_bp = Blueprint('organizations', __name__)

@organizations_bp.route('/organizations/current', methods=['GET'])
@jwt_required()
def get_current_organization():
    """Obter informações da organização atual"""
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
        
        organization = user.organization
        if not organization or not organization.is_active:
            return jsonify({
                'error': {
                    'code': 'ORGANIZATION_NOT_FOUND',
                    'message': 'Organização não encontrada ou inativa'
                }
            }), 404
        
        # Obter estatísticas de uso
        usage_stats = organization.get_usage_stats()
        
        org_data = organization.to_dict()
        org_data['usage'] = usage_stats
        
        return jsonify(org_data)
    
    except Exception as e:
        return jsonify({
            'error': {
                'code': 'GET_ORGANIZATION_ERROR',
                'message': 'Erro ao obter informações da organização',
                'details': str(e)
            }
        }), 500

@organizations_bp.route('/organizations/current', methods=['PATCH'])
@jwt_required()
def update_current_organization():
    """Atualizar configurações da organização atual"""
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
        
        # Verificar se usuário tem permissão para atualizar organização
        if not user.has_permission('manage_organization'):
            return jsonify({
                'error': {
                    'code': 'INSUFFICIENT_PERMISSIONS',
                    'message': 'Usuário não tem permissão para atualizar a organização'
                }
            }), 403
        
        organization = user.organization
        if not organization or not organization.is_active:
            return jsonify({
                'error': {
                    'code': 'ORGANIZATION_NOT_FOUND',
                    'message': 'Organização não encontrada ou inativa'
                }
            }), 404
        
        data = request.get_json()
        
        # Atualizar campos permitidos
        if 'settings' in data:
            # Mesclar configurações existentes com novas
            current_settings = organization.settings or {}
            new_settings = data['settings']
            current_settings.update(new_settings)
            organization.settings = current_settings
        
        db.session.commit()
        
        return jsonify(organization.to_dict())
    
    except Exception as e:
        db.session.rollback()
        return jsonify({
            'error': {
                'code': 'UPDATE_ORGANIZATION_ERROR',
                'message': 'Erro ao atualizar organização',
                'details': str(e)
            }
        }), 500
