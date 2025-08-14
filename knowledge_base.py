from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.dialects.postgresql import UUID
import uuid
from datetime import datetime

db = SQLAlchemy()

class KnowledgeBase(db.Model):
    __tablename__ = 'knowledge_base'
    
    id = db.Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    organization_id = db.Column(UUID(as_uuid=True), db.ForeignKey('organizations.id'), nullable=False)
    title = db.Column(db.String(255), nullable=False)
    content = db.Column(db.Text, nullable=False)
    content_type = db.Column(db.Enum('company_info', 'service_description', 'case_study', 'technical_spec', 
                                   'methodology', 'team_bio', 'certification', 'reference', name='content_type'), nullable=False)
    category = db.Column(db.String(100))
    tags = db.Column(db.JSON, default=[])
    source_document_id = db.Column(UUID(as_uuid=True), db.ForeignKey('documents.id'))
    source_url = db.Column(db.String(500))
    language = db.Column(db.String(10), default='pt-BR')
    keywords = db.Column(db.JSON, default=[])
    # embedding_vector seria implementado com extensão pgvector em PostgreSQL
    # embedding_vector = db.Column(db.ARRAY(db.Float))
    usage_count = db.Column(db.Integer, default=0)
    last_used_at = db.Column(db.DateTime)
    created_by = db.Column(UUID(as_uuid=True), db.ForeignKey('users.id'), nullable=False)
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow)
    is_active = db.Column(db.Boolean, nullable=False, default=True)
    
    def __repr__(self):
        return f'<KnowledgeBase {self.title}>'
    
    def to_dict(self):
        return {
            'id': str(self.id),
            'organization_id': str(self.organization_id),
            'title': self.title,
            'content': self.content,
            'content_type': self.content_type,
            'category': self.category,
            'tags': self.tags,
            'source_document_id': str(self.source_document_id) if self.source_document_id else None,
            'source_url': self.source_url,
            'language': self.language,
            'keywords': self.keywords,
            'usage_count': self.usage_count,
            'last_used_at': self.last_used_at.isoformat() if self.last_used_at else None,
            'created_by': str(self.created_by),
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None,
            'is_active': self.is_active
        }
    
    def increment_usage(self):
        """Incrementa o contador de uso"""
        self.usage_count += 1
        self.last_used_at = datetime.utcnow()
    
    def get_content_preview(self, max_length=200):
        """Retorna uma prévia do conteúdo"""
        if len(self.content) <= max_length:
            return self.content
        
        return self.content[:max_length] + "..."

