from functools import wraps
from flask import request, jsonify, current_app
from flask_jwt_extended import verify_jwt_in_request, get_jwt_identity, get_jwt
import jwt
import logging
from src.models.user import User
from src.models.role import Role

logger = logging.getLogger(__name__)

def token_required(f):
    """Decorator para verificar se o token JWT é válido"""
    @wraps(f)
    def decorated(*args, **kwargs):
        try:
            verify_jwt_in_request()
            return f(*args, **kwargs)
        except Exception as e:
            logger.warning(f"Token inválido: {e}")
            return jsonify({
                'error': {
                    'code': 'INVALID_TOKEN',
                    'message': 'Token de acesso inválido ou expirado'
                }
            }), 401
    return decorated

def role_required(*required_roles):
    """Decorator para verificar se o usuário tem as permissões necessárias"""
    def decorator(f):
        @wraps(f)
        def decorated(*args, **kwargs):
            try:
                verify_jwt_in_request()
                user_id = get_jwt_identity()
                
                user = User.query.get(user_id)
                if not user or not user.is_active:
                    return jsonify({
                        'error': {
                            'code': 'USER_NOT_FOUND',
                            'message': 'Usuário não encontrado ou inativo'
                        }
                    }), 404
                
                user_roles = [role.name for role in user.get_roles()]
                
                # Verificar se o usuário tem pelo menos uma das permissões necessárias
                if not any(role in user_roles for role in required_roles):
                    return jsonify({
                        'error': {
                            'code': 'INSUFFICIENT_PERMISSIONS',
                            'message': f'Permissões insuficientes. Necessário: {", ".join(required_roles)}'
                        }
                    }), 403
                
                return f(*args, **kwargs)
                
            except Exception as e:
                logger.error(f"Erro na verificação de permissões: {e}")
                return jsonify({
                    'error': {
                        'code': 'PERMISSION_CHECK_ERROR',
                        'message': 'Erro ao verificar permissões'
                    }
                }), 500
        return decorated
    return decorator

def organization_access_required(f):
    """Decorator para verificar se o usuário tem acesso à organização"""
    @wraps(f)
    def decorated(*args, **kwargs):
        try:
            verify_jwt_in_request()
            user_id = get_jwt_identity()
            
            user = User.query.get(user_id)
            if not user or not user.is_active:
                return jsonify({
                    'error': {
                        'code': 'USER_NOT_FOUND',
                        'message': 'Usuário não encontrado ou inativo'
                    }
                }), 404
            
            # Verificar se a organização está ativa
            if not user.organization or not user.organization.is_active:
                return jsonify({
                    'error': {
                        'code': 'ORGANIZATION_INACTIVE',
                        'message': 'Organização inativa ou não encontrada'
                    }
                }), 403
            
            # Adicionar informações da organização ao contexto da requisição
            request.current_user = user
            request.current_organization = user.organization
            
            return f(*args, **kwargs)
            
        except Exception as e:
            logger.error(f"Erro na verificação de acesso à organização: {e}")
            return jsonify({
                'error': {
                    'code': 'ORGANIZATION_ACCESS_ERROR',
                    'message': 'Erro ao verificar acesso à organização'
                }
            }), 500
    return decorated

def validate_azure_token(token):
    """Valida token do Azure EntraID (implementação simplificada)"""
    try:
        # Em produção, deveria validar a assinatura usando as chaves públicas do Azure
        # e verificar claims como issuer, audience, etc.
        
        # Por simplicidade, apenas decodificamos sem verificação
        decoded_token = jwt.decode(
            token, 
            options={"verify_signature": False},
            algorithms=["RS256"]
        )
        
        return decoded_token
        
    except jwt.InvalidTokenError as e:
        logger.error(f"Token Azure inválido: {e}")
        return None

def check_rate_limit(user_id, endpoint, limit=100, window=3600):
    """Verifica rate limiting por usuário e endpoint"""
    try:
        # Implementação simplificada de rate limiting
        # Em produção, usaria Redis ou similar para armazenar contadores
        
        # Por enquanto, sempre permite
        return True
        
    except Exception as e:
        logger.error(f"Erro no rate limiting: {e}")
        return True  # Em caso de erro, permite a requisição

def audit_log(action, resource_type=None, resource_id=None, details=None):
    """Decorator para log de auditoria"""
    def decorator(f):
        @wraps(f)
        def decorated(*args, **kwargs):
            try:
                # Executar função
                result = f(*args, **kwargs)
                
                # Log de auditoria
                user_id = None
                try:
                    verify_jwt_in_request()
                    user_id = get_jwt_identity()
                except:
                    pass
                
                audit_data = {
                    'user_id': user_id,
                    'action': action,
                    'resource_type': resource_type,
                    'resource_id': resource_id,
                    'details': details,
                    'ip_address': request.remote_addr,
                    'user_agent': request.headers.get('User-Agent'),
                    'timestamp': datetime.utcnow().isoformat()
                }
                
                logger.info(f"Audit log: {audit_data}")
                
                return result
                
            except Exception as e:
                # Log de erro também
                logger.error(f"Erro na ação {action}: {e}")
                raise
                
        return decorated
    return decorator

class SecurityHeaders:
    """Middleware para adicionar headers de segurança"""
    
    @staticmethod
    def add_security_headers(response):
        """Adiciona headers de segurança à resposta"""
        response.headers['X-Content-Type-Options'] = 'nosniff'
        response.headers['X-Frame-Options'] = 'DENY'
        response.headers['X-XSS-Protection'] = '1; mode=block'
        response.headers['Strict-Transport-Security'] = 'max-age=31536000; includeSubDomains'
        response.headers['Content-Security-Policy'] = "default-src 'self'"
        response.headers['Referrer-Policy'] = 'strict-origin-when-cross-origin'
        return response

def validate_request_data(required_fields=None, optional_fields=None):
    """Decorator para validar dados da requisição"""
    def decorator(f):
        @wraps(f)
        def decorated(*args, **kwargs):
            try:
                data = request.get_json()
                
                if not data:
                    return jsonify({
                        'error': {
                            'code': 'MISSING_DATA',
                            'message': 'Dados da requisição são obrigatórios'
                        }
                    }), 400
                
                # Verificar campos obrigatórios
                if required_fields:
                    missing_fields = [field for field in required_fields if field not in data]
                    if missing_fields:
                        return jsonify({
                            'error': {
                                'code': 'MISSING_REQUIRED_FIELDS',
                                'message': f'Campos obrigatórios ausentes: {", ".join(missing_fields)}'
                            }
                        }), 400
                
                # Filtrar apenas campos permitidos
                allowed_fields = (required_fields or []) + (optional_fields or [])
                if allowed_fields:
                    filtered_data = {k: v for k, v in data.items() if k in allowed_fields}
                    request.validated_data = filtered_data
                else:
                    request.validated_data = data
                
                return f(*args, **kwargs)
                
            except Exception as e:
                logger.error(f"Erro na validação de dados: {e}")
                return jsonify({
                    'error': {
                        'code': 'VALIDATION_ERROR',
                        'message': 'Erro na validação dos dados'
                    }
                }), 400
                
        return decorated
    return decorator

def cors_headers(f):
    """Decorator para adicionar headers CORS"""
    @wraps(f)
    def decorated(*args, **kwargs):
        response = f(*args, **kwargs)
        
        # Se a resposta for um tuple (data, status_code), converter para Response
        if isinstance(response, tuple):
            from flask import make_response
            response = make_response(response)
        
        # Adicionar headers CORS
        response.headers['Access-Control-Allow-Origin'] = '*'
        response.headers['Access-Control-Allow-Methods'] = 'GET, POST, PUT, DELETE, OPTIONS'
        response.headers['Access-Control-Allow-Headers'] = 'Content-Type, Authorization'
        response.headers['Access-Control-Max-Age'] = '3600'
        
        return response
    return decorated

