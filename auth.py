from flask import Blueprint, request, jsonify, redirect, url_for, session
from flask_jwt_extended import create_access_token, jwt_required, get_jwt_identity
import requests
import os
from datetime import datetime, timedelta
from src.models.user import User, db
from src.models.organization import Organization

auth_bp = Blueprint('auth', __name__)

# Configurações do Azure EntraID
AZURE_CLIENT_ID = os.getenv('AZURE_CLIENT_ID')
AZURE_CLIENT_SECRET = os.getenv('AZURE_CLIENT_SECRET')
AZURE_TENANT_ID = os.getenv('AZURE_TENANT_ID')
AZURE_REDIRECT_URI = os.getenv('AZURE_REDIRECT_URI')

@auth_bp.route('/login')
def login():
    """Inicia o fluxo de autenticação OAuth2 com Azure EntraID"""
    try:
        # URL de autorização do Azure EntraID
        authorization_url = (
            f"https://login.microsoftonline.com/{AZURE_TENANT_ID}/oauth2/v2.0/authorize"
            f"?client_id={AZURE_CLIENT_ID}"
            f"&response_type=code"
            f"&redirect_uri={AZURE_REDIRECT_URI}"
            f"&response_mode=query"
            f"&scope=openid profile email User.Read"
            f"&state=12345"  # Em produção, usar um valor aleatório e validar
        )
        
        return redirect(authorization_url)
    
    except Exception as e:
        return jsonify({
            'error': {
                'code': 'AUTH_ERROR',
                'message': 'Erro ao iniciar autenticação',
                'details': str(e)
            }
        }), 500

@auth_bp.route('/callback')
def callback():
    """Callback do OAuth2 - troca o código por tokens"""
    try:
        # Obter código de autorização
        code = request.args.get('code')
        if not code:
            return jsonify({
                'error': {
                    'code': 'MISSING_CODE',
                    'message': 'Código de autorização não encontrado'
                }
            }), 400
        
        # Trocar código por tokens
        token_url = f"https://login.microsoftonline.com/{AZURE_TENANT_ID}/oauth2/v2.0/token"
        token_data = {
            'client_id': AZURE_CLIENT_ID,
            'client_secret': AZURE_CLIENT_SECRET,
            'code': code,
            'redirect_uri': AZURE_REDIRECT_URI,
            'grant_type': 'authorization_code'
        }
        
        token_response = requests.post(token_url, data=token_data)
        token_response.raise_for_status()
        tokens = token_response.json()
        
        # Obter informações do usuário
        user_info_url = "https://graph.microsoft.com/v1.0/me"
        headers = {'Authorization': f"Bearer {tokens['access_token']}"}
        user_response = requests.get(user_info_url, headers=headers)
        user_response.raise_for_status()
        user_data = user_response.json()
        
        # Processar usuário
        user = process_user_login(user_data, tokens)
        
        # Criar token JWT interno
        access_token = create_access_token(
            identity=str(user.id),
            expires_delta=timedelta(seconds=int(os.getenv('JWT_ACCESS_TOKEN_EXPIRES', 3600)))
        )
        
        return jsonify({
            'access_token': access_token,
            'token_type': 'Bearer',
            'expires_in': int(os.getenv('JWT_ACCESS_TOKEN_EXPIRES', 3600)),
            'user': user.to_dict()
        })
    
    except requests.RequestException as e:
        return jsonify({
            'error': {
                'code': 'EXTERNAL_API_ERROR',
                'message': 'Erro ao comunicar com Azure EntraID',
                'details': str(e)
            }
        }), 502
    
    except Exception as e:
        return jsonify({
            'error': {
                'code': 'AUTH_ERROR',
                'message': 'Erro no processo de autenticação',
                'details': str(e)
            }
        }), 500

def process_user_login(user_data, tokens):
    """Processa o login do usuário e cria/atualiza registro no banco"""
    try:
        azure_object_id = user_data['id']
        email = user_data['mail'] or user_data['userPrincipalName']
        
        # Buscar usuário existente
        user = User.query.filter_by(azure_object_id=azure_object_id).first()
        
        if user:
            # Atualizar informações do usuário existente
            user.email = email
            user.first_name = user_data.get('givenName', '')
            user.last_name = user_data.get('surname', '')
            user.display_name = user_data.get('displayName', email)
            user.job_title = user_data.get('jobTitle')
            user.last_login_at = datetime.utcnow()
            
        else:
            # Criar novo usuário
            # Primeiro, determinar a organização baseada no domínio do email
            domain = email.split('@')[1] if '@' in email else None
            organization = None
            
            if domain:
                organization = Organization.query.filter_by(domain=domain).first()
            
            if not organization:
                # Criar organização padrão se não existir
                organization = Organization(
                    name=f"Organização {domain or 'Padrão'}",
                    domain=domain
                )
                db.session.add(organization)
                db.session.flush()  # Para obter o ID
            
            user = User(
                organization_id=organization.id,
                azure_object_id=azure_object_id,
                email=email,
                first_name=user_data.get('givenName', ''),
                last_name=user_data.get('surname', ''),
                display_name=user_data.get('displayName', email),
                job_title=user_data.get('jobTitle'),
                last_login_at=datetime.utcnow()
            )
            db.session.add(user)
        
        db.session.commit()
        return user
    
    except Exception as e:
        db.session.rollback()
        raise e

@auth_bp.route('/refresh', methods=['POST'])
def refresh():
    """Renovar token de acesso (implementação simplificada)"""
    try:
        data = request.get_json()
        refresh_token = data.get('refresh_token')
        
        if not refresh_token:
            return jsonify({
                'error': {
                    'code': 'MISSING_REFRESH_TOKEN',
                    'message': 'Refresh token é obrigatório'
                }
            }), 400
        
        # Em uma implementação completa, validaríamos o refresh token
        # Por simplicidade, retornamos erro
        return jsonify({
            'error': {
                'code': 'NOT_IMPLEMENTED',
                'message': 'Refresh token não implementado nesta versão'
            }
        }), 501
    
    except Exception as e:
        return jsonify({
            'error': {
                'code': 'REFRESH_ERROR',
                'message': 'Erro ao renovar token',
                'details': str(e)
            }
        }), 500

@auth_bp.route('/logout', methods=['POST'])
@jwt_required()
def logout():
    """Logout do usuário"""
    try:
        # Em uma implementação completa, invalidaríamos o token
        # Por simplicidade, apenas retornamos sucesso
        return '', 204
    
    except Exception as e:
        return jsonify({
            'error': {
                'code': 'LOGOUT_ERROR',
                'message': 'Erro ao fazer logout',
                'details': str(e)
            }
        }), 500

@auth_bp.route('/me')
@jwt_required()
def get_current_user():
    """Obter informações do usuário atual"""
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
        
        return jsonify(user.to_dict())
    
    except Exception as e:
        return jsonify({
            'error': {
                'code': 'USER_INFO_ERROR',
                'message': 'Erro ao obter informações do usuário',
                'details': str(e)
            }
        }), 500

