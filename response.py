from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy import UniqueConstraint
import uuid
from datetime import datetime
from decimal import Decimal

db = SQLAlchemy()

class Response(db.Model):
    __tablename__ = 'responses'
    
    id = db.Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    question_id = db.Column(UUID(as_uuid=True), db.ForeignKey('questions.id'), nullable=False)
    version = db.Column(db.Integer, nullable=False, default=1)
    response_text = db.Column(db.Text, nullable=False)
    response_type = db.Column(db.Enum('generated', 'manual', 'hybrid', name='response_type'), default='generated')
    word_count = db.Column(db.Integer)
    character_count = db.Column(db.Integer)
    source_documents = db.Column(db.JSON, default=[])
    confidence_score = db.Column(db.Numeric(3, 2))
    generated_by = db.Column(db.String(50))
    generated_at = db.Column(db.DateTime)
    created_by = db.Column(UUID(as_uuid=True), db.ForeignKey('users.id'), nullable=False)
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow)
    reviewed_by = db.Column(UUID(as_uuid=True), db.ForeignKey('users.id'))
    reviewed_at = db.Column(db.DateTime)
    approved_by = db.Column(UUID(as_uuid=True), db.ForeignKey('users.id'))
    approved_at = db.Column(db.DateTime)
    status = db.Column(db.Enum('draft', 'in_review', 'approved', 'rejected', name='response_status'), default='draft')
    is_current = db.Column(db.Boolean, default=True)
    is_active = db.Column(db.Boolean, nullable=False, default=True)
    
    # Constraint para garantir apenas uma resposta atual por pergunta
    __table_args__ = (
        UniqueConstraint('question_id', 'is_current', name='unique_current_response'),
    )
    
    def __repr__(self):
        return f'<Response {self.question_id}:v{self.version}>'
    
    def to_dict(self):
        return {
            'id': str(self.id),
            'question_id': str(self.question_id),
            'version': self.version,
            'response_text': self.response_text,
            'response_type': self.response_type,
            'word_count': self.word_count,
            'character_count': self.character_count,
            'source_documents': self.source_documents,
            'confidence_score': float(self.confidence_score) if self.confidence_score else None,
            'generated_by': self.generated_by,
            'generated_at': self.generated_at.isoformat() if self.generated_at else None,
            'created_by': str(self.created_by),
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None,
            'reviewed_by': str(self.reviewed_by) if self.reviewed_by else None,
            'reviewed_at': self.reviewed_at.isoformat() if self.reviewed_at else None,
            'approved_by': str(self.approved_by) if self.approved_by else None,
            'approved_at': self.approved_at.isoformat() if self.approved_at else None,
            'status': self.status,
            'is_current': self.is_current,
            'is_active': self.is_active
        }
    
    def calculate_word_count(self):
        """Calcula e atualiza a contagem de palavras"""
        if self.response_text:
            self.word_count = len(self.response_text.split())
            self.character_count = len(self.response_text)
        else:
            self.word_count = 0
            self.character_count = 0

