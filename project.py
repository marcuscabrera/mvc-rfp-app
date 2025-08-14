from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.dialects.postgresql import UUID
import uuid
from datetime import datetime
from decimal import Decimal

db = SQLAlchemy()

class Project(db.Model):
    __tablename__ = 'projects'
    
    id = db.Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    organization_id = db.Column(UUID(as_uuid=True), db.ForeignKey('organizations.id'), nullable=False)
    name = db.Column(db.String(255), nullable=False)
    description = db.Column(db.Text)
    rfp_title = db.Column(db.String(500))
    client_name = db.Column(db.String(255))
    submission_deadline = db.Column(db.DateTime)
    estimated_value = db.Column(db.Numeric(15, 2))
    currency = db.Column(db.String(3), default='BRL')
    priority = db.Column(db.Enum('low', 'medium', 'high', 'critical', name='priority'), default='medium')
    status = db.Column(db.Enum('draft', 'in_progress', 'review', 'ready_to_submit', 'submitted', 'won', 'lost', 'cancelled', name='project_status'), 
                      nullable=False, default='draft')
    tags = db.Column(db.JSON, default=[])
    metadata = db.Column(db.JSON, default={})
    created_by = db.Column(UUID(as_uuid=True), db.ForeignKey('users.id'), nullable=False)
    assigned_to = db.Column(UUID(as_uuid=True), db.ForeignKey('users.id'))
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow)
    is_active = db.Column(db.Boolean, nullable=False, default=True)
    
    # Relacionamentos
    documents = db.relationship('Document', backref='project', lazy=True)
    questions = db.relationship('Question', backref='project', lazy=True)
    
    def __repr__(self):
        return f'<Project {self.name}>'
    
    def to_dict(self):
        return {
            'id': str(self.id),
            'organization_id': str(self.organization_id),
            'name': self.name,
            'description': self.description,
            'rfp_title': self.rfp_title,
            'client_name': self.client_name,
            'submission_deadline': self.submission_deadline.isoformat() if self.submission_deadline else None,
            'estimated_value': float(self.estimated_value) if self.estimated_value else None,
            'currency': self.currency,
            'priority': self.priority,
            'status': self.status,
            'tags': self.tags,
            'metadata': self.metadata,
            'created_by': str(self.created_by),
            'assigned_to': str(self.assigned_to) if self.assigned_to else None,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None,
            'is_active': self.is_active
        }
    
    def get_stats(self):
        """Retorna estatísticas do projeto"""
        from src.models.question import Question
        from src.models.response import Response
        
        questions_count = Question.query.filter_by(project_id=self.id, is_active=True).count()
        responses_count = Response.query.join(Question).filter(
            Question.project_id == self.id,
            Question.is_active == True,
            Response.is_current == True,
            Response.is_active == True
        ).count()
        
        completion_percentage = (responses_count / questions_count * 100) if questions_count > 0 else 0
        
        return {
            'questions_count': questions_count,
            'responses_count': responses_count,
            'completion_percentage': round(completion_percentage, 1)
        }

