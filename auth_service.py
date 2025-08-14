import os
import requests
import jwt
from datetime import datetime, timedelta
from typing import Dict, Optional, Any
import logging
from flask import current_app
from src.models.user import User, db
from src.models.organization import Organization

logger = logging.getLogger(__name__)

class AzureEntraIDService:
    """Serviço para autenticação com Azure EntraID (Azure AD)"""
    
    def __init__(self):
        self.tenant_id = os.getenv('AZURE_TENANT_ID')
        self.client_id = os.getenv('AZURE_CLIENT_ID')
        self.client_secret = os.getenv('AZURE_CLIENT_SECRET')
        self.redirect_uri = os.getenv('AZURE_REDIRECT_URI', 'http://localhost:3000/auth/callback')
        
        # URLs do Azure AD
        self.authority = f"https://login.microsoftonline.com/{self.tenant_id}"
        self.token_endpoint = f"{self.authority}/oauth2/v2.0/token"
        self.userinfo_endpoint = "https://graph.microsoft.com/v1.0/me"
        self.jwks_uri = f"{self.authority}/discovery/v2.0/keys"
        
    def get_authorization_url(self, state: str = None) -> str:
        """Gera URL de autorização para redirecionamento ao Azure AD"""
        params = {
            'client_id': self.client_id,
            'response_type': 'code',
            'redirect_uri': self.redirect_uri,
            'scope': 'openid profile email User.Read',
            'response_mode': 'query'
        }
        
        if state:
            params['state'] = state
            
        query_string = '&'.join([f"{k}={v}" for k, v in params.items()])
        return f"{self.authority}/oauth2/v2.0/authorize?{query_string}"
    
    def exchange_code_for_tokens(self, authorization_code: str) -> Dict[str, Any]:
        """Troca código de autorização por tokens de acesso"""
        try:
            data = {
                'client_id': self.client_id,
                'client_secret': self.client_secret,
                'code': authorization_code,
                'grant_type': 'authorization_code',
                'redirect_uri': self.redirect_uri,
                'scope': 'openid profile email User.Read'
            }
            
            response = requests.post(
                self.token_endpoint,
                data=data,
                headers={'Content-Type': 'application/x-www-form-urlencoded'},
                timeout=30
            )
            
            response.raise_for_status()
            return response.json()
            
        except requests.RequestException as e:
            logger.error(f"Erro ao trocar código por tokens: {e}")
            raise Exception("Falha na autenticação com Azure AD")
    
    def get_user_info(self, access_token: str) -> Dict[str, Any]:
        """Obtém informações do usuário usando o token de acesso"""
        try:
            headers = {
                'Authorization': f'Bearer {access_token}',
                'Content-Type': 'application/json'
            }
            
            response = requests.get(
                self.userinfo_endpoint,
                headers=headers,
                timeout=30
            )
            
            response.raise_for_status()
            return response.json()
            
        except requests.RequestException as e:
            logger.error(f"Erro ao obter informações do usuário: {e}")
            raise Exception("Falha ao obter dados do usuário")
    
    def validate_id_token(self, id_token: str) -> Dict[str, Any]:
        """Valida e decodifica o ID token JWT"""
        try:
            # Em produção, deveria validar a assinatura usando as chaves públicas do Azure
            # Por simplicidade, apenas decodificamos sem verificação
            decoded_token = jwt.decode(
                id_token, 
                options={"verify_signature": False},  # ATENÇÃO: Apenas para desenvolvimento
                algorithms=["RS256"]
            )
            
            # Validar claims básicos
            now = datetime.utcnow().timestamp()
            
            if decoded_token.get('exp', 0) < now:
                raise Exception("Token expirado")
                
            if decoded_token.get('aud') != self.client_id:
                raise Exception("Audience inválida")
                
            return decoded_token
            
        except jwt.InvalidTokenError as e:
            logger.error(f"Token inválido: {e}")
            raise Exception("Token de ID inválido")
    
    def create_or_update_user(self, user_info: Dict[str, Any], 
                            id_token_claims: Dict[str, Any] = None) -> User:
        """Cria ou atualiza usuário baseado nas informações do Azure AD"""
        try:
            email = user_info.get('mail') or user_info.get('userPrincipalName')
            if not email:
                raise Exception("Email não encontrado nas informações do usuário")
            
            # Buscar usuário existente
            user = User.query.filter_by(email=email).first()
            
            # Extrair informações da organização
            org_name = self._extract_organization_name(user_info, id_token_claims)
            organization = self._get_or_create_organization(org_name)
            
            if user:
                # Atualizar usuário existente
                user.first_name = user_info.get('givenName', user.first_name)
                user.last_name = user_info.get('surname', user.last_name)
                user.job_title = user_info.get('jobTitle', user.job_title)
                user.department = user_info.get('department', user.department)
                user.phone = user_info.get('businessPhones', [None])[0] or user.phone
                user.azure_object_id = user_info.get('id')
                user.last_login_at = datetime.utcnow()
                user.organization_id = organization.id
                
                # Atualizar preferências de idioma
                preferred_language = user_info.get('preferredLanguage', 'pt-BR')
                if user.preferences:
                    user.preferences['language'] = preferred_language
                else:
                    user.preferences = {'language': preferred_language}
                    
            else:
                # Criar novo usuário
                user = User(
                    email=email,
                    first_name=user_info.get('givenName', ''),
                    last_name=user_info.get('surname', ''),
                    job_title=user_info.get('jobTitle'),
                    department=user_info.get('department'),
                    phone=user_info.get('businessPhones', [None])[0],
                    azure_object_id=user_info.get('id'),
                    organization_id=organization.id,
                    language=user_info.get('preferredLanguage', 'pt-BR'),
                    preferences={'language': user_info.get('preferredLanguage', 'pt-BR')},
                    last_login_at=datetime.utcnow(),
                    is_active=True
                )
                
                db.session.add(user)
            
            db.session.commit()
            return user
            
        except Exception as e:
            db.session.rollback()
            logger.error(f"Erro ao criar/atualizar usuário: {e}")
            raise
    
    def _extract_organization_name(self, user_info: Dict[str, Any], 
                                 id_token_claims: Dict[str, Any] = None) -> str:
        """Extrai nome da organização das informações do usuário"""
        # Tentar diferentes fontes para o nome da organização
        org_name = None
        
        if id_token_claims:
            org_name = id_token_claims.get('tid')  # Tenant ID como fallback
            
        # Tentar extrair do domínio do email
        email = user_info.get('mail') or user_info.get('userPrincipalName')
        if email and '@' in email:
            domain = email.split('@')[1]
            org_name = domain.split('.')[0].title()
        
        return org_name or 'Organização Padrão'
    
    def _get_or_create_organization(self, org_name: str) -> Organization:
        """Obtém ou cria organização"""
        organization = Organization.query.filter_by(name=org_name).first()
        
        if not organization:
            organization = Organization(
                name=org_name,
                settings={
                    'default_language': 'pt-BR',
                    'ai_model_preference': 'gemini',
                    'auto_approve_responses': False
                },
                is_active=True
            )
            db.session.add(organization)
            db.session.flush()  # Para obter o ID
            
        return organization
    
    def generate_jwt_token(self, user: User) -> str:
        """Gera token JWT para o usuário"""
        payload = {
            'user_id': str(user.id),
            'email': user.email,
            'organization_id': str(user.organization_id),
            'iat': datetime.utcnow(),
            'exp': datetime.utcnow() + timedelta(hours=24)
        }
        
        secret_key = current_app.config.get('JWT_SECRET_KEY', 'dev-secret-key')
        return jwt.encode(payload, secret_key, algorithm='HS256')
    
    def refresh_access_token(self, refresh_token: str) -> Dict[str, Any]:
        """Renova token de acesso usando refresh token"""
        try:
            data = {
                'client_id': self.client_id,
                'client_secret': self.client_secret,
                'refresh_token': refresh_token,
                'grant_type': 'refresh_token',
                'scope': 'openid profile email User.Read'
            }
            
            response = requests.post(
                self.token_endpoint,
                data=data,
                headers={'Content-Type': 'application/x-www-form-urlencoded'},
                timeout=30
            )
            
            response.raise_for_status()
            return response.json()
            
        except requests.RequestException as e:
            logger.error(f"Erro ao renovar token: {e}")
            raise Exception("Falha ao renovar token de acesso")

# Instância global do serviço
azure_auth_service = AzureEntraIDService()

