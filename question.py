from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.dialects.postgresql import UUID
import uuid
from datetime import datetime
from decimal import Decimal

db = SQLAlchemy()

class Question(db.Model):
    __tablename__ = 'questions'
    
    id = db.Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    project_id = db.Column(UUID(as_uuid=True), db.ForeignKey('projects.id'), nullable=False)
    document_id = db.Column(UUID(as_uuid=True), db.ForeignKey('documents.id'), nullable=False)
    question_text = db.Column(db.Text, nullable=False)
    question_number = db.Column(db.String(50))
    section = db.Column(db.String(255))
    category = db.Column(db.String(100))
    question_type = db.Column(db.Enum('open', 'multiple_choice', 'yes_no', 'numeric', 'date', 'file_upload', name='question_type'), default='open')
    required = db.Column(db.Boolean, default=False)
    max_words = db.Column(db.Integer)
    context = db.Column(db.Text)
    keywords = db.Column(db.JSON, default=[])
    confidence_score = db.Column(db.Numeric(3, 2))
    page_number = db.Column(db.Integer)
    position_in_page = db.Column(db.Integer)
    extracted_by = db.Column(db.String(50))
    extracted_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    reviewed_by = db.Column(UUID(as_uuid=True), db.ForeignKey('users.id'))
    reviewed_at = db.Column(db.DateTime)
    is_active = db.Column(db.Boolean, nullable=False, default=True)
    
    # Relacionamentos
    responses = db.relationship('Response', backref='question', lazy=True, cascade='all, delete-orphan')
    
    def __repr__(self):
        return f'<Question {self.question_number or self.id}>'
    
    def to_dict(self):
        return {
            'id': str(self.id),
            'project_id': str(self.project_id),
            'document_id': str(self.document_id),
            'question_text': self.question_text,
            'question_number': self.question_number,
            'section': self.section,
            'category': self.category,
            'question_type': self.question_type,
            'required': self.required,
            'max_words': self.max_words,
            'context': self.context,
            'keywords': self.keywords,
            'confidence_score': float(self.confidence_score) if self.confidence_score else None,
            'page_number': self.page_number,
            'position_in_page': self.position_in_page,
            'extracted_by': self.extracted_by,
            'extracted_at': self.extracted_at.isoformat() if self.extracted_at else None,
            'reviewed_by': str(self.reviewed_by) if self.reviewed_by else None,
            'reviewed_at': self.reviewed_at.isoformat() if self.reviewed_at else None,
            'is_active': self.is_active
        }
    
    def get_current_response(self):
        """Retorna a resposta atual da pergunta"""
        from src.models.response import Response
        return Response.query.filter_by(
            question_id=self.id,
            is_current=True,
            is_active=True
        ).first()
    
    def get_response_history(self):
        """Retorna histórico de respostas da pergunta"""
        from src.models.response import Response
        return Response.query.filter_by(
            question_id=self.id,
            is_active=True
        ).order_by(Response.version.desc()).all()

