from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.dialects.postgresql import UUID
import uuid
from datetime import datetime

db = SQLAlchemy()

class Document(db.Model):
    __tablename__ = 'documents'
    
    id = db.Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    organization_id = db.Column(UUID(as_uuid=True), db.ForeignKey('organizations.id'), nullable=False)
    project_id = db.Column(UUID(as_uuid=True), db.ForeignKey('projects.id'))
    name = db.Column(db.String(255), nullable=False)
    original_filename = db.Column(db.String(255), nullable=False)
    file_path = db.Column(db.String(500), nullable=False)
    file_size = db.Column(db.BigInteger, nullable=False)
    mime_type = db.Column(db.String(100), nullable=False)
    file_hash = db.Column(db.String(64), nullable=False)
    document_type = db.Column(db.Enum('rfp', 'knowledge_base', 'template', 'reference', name='document_type'), nullable=False)
    language = db.Column(db.String(10), default='pt-BR')
    page_count = db.Column(db.Integer)
    word_count = db.Column(db.Integer)
    processing_status = db.Column(db.Enum('pending', 'processing', 'completed', 'failed', name='processing_status'), default='pending')
    extracted_text = db.Column(db.Text)
    metadata = db.Column(db.JSON, default={})
    uploaded_by = db.Column(UUID(as_uuid=True), db.ForeignKey('users.id'), nullable=False)
    uploaded_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    processed_at = db.Column(db.DateTime)
    is_active = db.Column(db.Boolean, nullable=False, default=True)
    
    # Relacionamentos
    questions = db.relationship('Question', backref='document', lazy=True)
    
    def __repr__(self):
        return f'<Document {self.name}>'
    
    def to_dict(self):
        return {
            'id': str(self.id),
            'organization_id': str(self.organization_id),
            'project_id': str(self.project_id) if self.project_id else None,
            'name': self.name,
            'original_filename': self.original_filename,
            'file_path': self.file_path,
            'file_size': self.file_size,
            'mime_type': self.mime_type,
            'file_hash': self.file_hash,
            'document_type': self.document_type,
            'language': self.language,
            'page_count': self.page_count,
            'word_count': self.word_count,
            'processing_status': self.processing_status,
            'metadata': self.metadata,
            'uploaded_by': str(self.uploaded_by),
            'uploaded_at': self.uploaded_at.isoformat() if self.uploaded_at else None,
            'processed_at': self.processed_at.isoformat() if self.processed_at else None,
            'is_active': self.is_active
        }
    
    def get_text_preview(self, max_length=500):
        """Retorna uma prévia do texto extraído"""
        if not self.extracted_text:
            return None
        
        if len(self.extracted_text) <= max_length:
            return self.extracted_text
        
        return self.extracted_text[:max_length] + "..."

