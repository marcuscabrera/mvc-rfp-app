from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy import text
import uuid
from datetime import datetime

db = SQLAlchemy()

class Organization(db.Model):
    __tablename__ = 'organizations'
    
    id = db.Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = db.Column(db.String(255), nullable=False, unique=True)
    domain = db.Column(db.String(255), unique=True)
    azure_tenant_id = db.Column(db.String(255), unique=True)
    subscription_tier = db.Column(db.Enum('basic', 'professional', 'enterprise', name='subscription_tier'), 
                                 nullable=False, default='basic')
    max_users = db.Column(db.Integer, nullable=False, default=10)
    max_projects = db.Column(db.Integer, nullable=False, default=50)
    storage_quota_gb = db.Column(db.Integer, nullable=False, default=10)
    ai_quota_monthly = db.Column(db.Integer, nullable=False, default=1000)
    settings = db.Column(db.JSON, default={})
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow)
    is_active = db.Column(db.Boolean, nullable=False, default=True)
    
    # Relacionamentos
    users = db.relationship('User', backref='organization', lazy=True, cascade='all, delete-orphan')
    projects = db.relationship('Project', backref='organization', lazy=True, cascade='all, delete-orphan')
    
    def __repr__(self):
        return f'<Organization {self.name}>'
    
    def to_dict(self):
        return {
            'id': str(self.id),
            'name': self.name,
            'domain': self.domain,
            'azure_tenant_id': self.azure_tenant_id,
            'subscription_tier': self.subscription_tier,
            'max_users': self.max_users,
            'max_projects': self.max_projects,
            'storage_quota_gb': self.storage_quota_gb,
            'ai_quota_monthly': self.ai_quota_monthly,
            'settings': self.settings,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None,
            'is_active': self.is_active
        }
    
    def get_usage_stats(self):
        """Retorna estatísticas de uso da organização"""
        from src.models.user import User
        from src.models.project import Project
        
        users_count = User.query.filter_by(organization_id=self.id, is_active=True).count()
        projects_count = Project.query.filter_by(organization_id=self.id, is_active=True).count()
        
        # TODO: Implementar cálculo de storage usado e chamadas de IA
        storage_used_gb = 0.0
        ai_calls_this_month = 0
        
        return {
            'users_count': users_count,
            'projects_count': projects_count,
            'storage_used_gb': storage_used_gb,
            'ai_calls_this_month': ai_calls_this_month
        }

