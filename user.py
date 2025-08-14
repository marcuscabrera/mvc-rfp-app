from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy import text, UniqueConstraint
import uuid
from datetime import datetime

db = SQLAlchemy()

class User(db.Model):
    __tablename__ = 'users'
    
    id = db.Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    organization_id = db.Column(UUID(as_uuid=True), db.ForeignKey('organizations.id'), nullable=False)
    azure_object_id = db.Column(db.String(255), unique=True, nullable=False)
    email = db.Column(db.String(255), nullable=False)
    first_name = db.Column(db.String(100), nullable=False)
    last_name = db.Column(db.String(100), nullable=False)
    display_name = db.Column(db.String(255), nullable=False)
    job_title = db.Column(db.String(255))
    department = db.Column(db.String(255))
    phone = db.Column(db.String(50))
    timezone = db.Column(db.String(50), default='UTC')
    language = db.Column(db.String(10), default='pt-BR')
    preferences = db.Column(db.JSON, default={})
    last_login_at = db.Column(db.DateTime)
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow)
    is_active = db.Column(db.Boolean, nullable=False, default=True)
    
    # Constraint para garantir email único por organização
    __table_args__ = (
        UniqueConstraint('organization_id', 'email', name='unique_email_per_organization'),
    )
    
    # Relacionamentos
    user_roles = db.relationship('UserRole', backref='user', lazy=True, cascade='all, delete-orphan')
    created_projects = db.relationship('Project', foreign_keys='Project.created_by', backref='creator', lazy=True)
    assigned_projects = db.relationship('Project', foreign_keys='Project.assigned_to', backref='assignee', lazy=True)
    
    def __repr__(self):
        return f'<User {self.email}>'
    
    def to_dict(self):
        return {
            'id': str(self.id),
            'organization_id': str(self.organization_id),
            'azure_object_id': self.azure_object_id,
            'email': self.email,
            'first_name': self.first_name,
            'last_name': self.last_name,
            'display_name': self.display_name,
            'job_title': self.job_title,
            'department': self.department,
            'phone': self.phone,
            'timezone': self.timezone,
            'language': self.language,
            'preferences': self.preferences,
            'last_login_at': self.last_login_at.isoformat() if self.last_login_at else None,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None,
            'is_active': self.is_active
        }
    
    def get_roles(self):
        """Retorna lista de papéis do usuário"""
        from src.models.role import Role
        return [ur.role for ur in self.user_roles if ur.is_active]
    
    def has_permission(self, permission):
        """Verifica se o usuário tem uma permissão específica"""
        roles = self.get_roles()
        for role in roles:
            if permission in role.permissions:
                return True
        return False
