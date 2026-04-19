"""
SAI Rolotech AI Hub - Database Models
SQLAlchemy Models
"""

from sqlalchemy import create_engine, Column, Integer, String, Text, DateTime, ForeignKey, Boolean
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relationship
from datetime import datetime
import os

Base = declarative_base()

# ==================== USERS ====================

class User(Base):
    __tablename__ = 'users'

    id = Column(Integer, primary_key=True)
    telegram_id = Column(String(50), unique=True, nullable=True)
    name = Column(String(100), nullable=False)
    phone = Column(String(20), nullable=True)
    role = Column(String(20), default='user')  # user, admin
    created_at = Column(DateTime, default=datetime.utcnow)

    # Relationships
    memories = relationship("Memory", back_populates="user")
    tasks = relationship("Task", back_populates="user")
    leads = relationship("Lead", back_populates="assigned_user")
    audit_logs = relationship("AuditLog", back_populates="user")

    def to_dict(self):
        return {
            "id": self.id,
            "telegram_id": self.telegram_id,
            "name": self.name,
            "phone": self.phone,
            "role": self.role,
            "created_at": self.created_at.isoformat() if self.created_at else None
        }


# ==================== MEMORY ====================

class Memory(Base):
    __tablename__ = 'memory'

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey('users.id'), nullable=False)
    key = Column(String(100), nullable=False)
    value = Column(Text, nullable=False)
    memory_type = Column(String(50), default='fact')  # fact, preference, learning
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    user = relationship("User", back_populates="memories")

    def to_dict(self):
        return {
            "id": self.id,
            "user_id": self.user_id,
            "key": self.key,
            "value": self.value,
            "type": self.memory_type,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None
        }


# ==================== TASKS ====================

class Task(Base):
    __tablename__ = 'tasks'

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey('users.id'), nullable=False)
    source = Column(String(50), nullable=False)  # telegram, dashboard, webhook
    intent = Column(String(100), nullable=False)
    target_tool = Column(String(50), nullable=False)  # hermes, crm, interpreter, n8n
    status = Column(String(20), default='pending')  # pending, running, completed, failed
    input_payload = Column(Text)
    output_payload = Column(Text)
    error_message = Column(Text)
    created_at = Column(DateTime, default=datetime.utcnow)
    completed_at = Column(DateTime, nullable=True)

    # Relationships
    user = relationship("User", back_populates="tasks")

    def to_dict(self):
        return {
            "id": self.id,
            "user_id": self.user_id,
            "source": self.source,
            "intent": self.intent,
            "target_tool": self.target_tool,
            "status": self.status,
            "input": self.input_payload,
            "output": self.output_payload,
            "error": self.error_message,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "completed_at": self.completed_at.isoformat() if self.completed_at else None
        }


# ==================== LEADS ====================

class Lead(Base):
    __tablename__ = 'leads'

    id = Column(Integer, primary_key=True)
    name = Column(String(100), nullable=False)
    mobile = Column(String(20))
    email = Column(String(100))
    source = Column(String(50))  # telegram, facebook, website, call
    stage = Column(String(50), default='new')  # new, contacted, qualified, proposal, won, lost
    assigned_to_id = Column(Integer, ForeignKey('users.id'))
    notes = Column(Text)
    follow_up_date = Column(DateTime, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    assigned_user = relationship("User", back_populates="leads")

    def to_dict(self):
        return {
            "id": self.id,
            "name": self.name,
            "mobile": self.mobile,
            "email": self.email,
            "source": self.source,
            "stage": self.stage,
            "assigned_to": self.assigned_user.name if self.assigned_user else None,
            "notes": self.notes,
            "follow_up": self.follow_up_date.isoformat() if self.follow_up_date else None,
            "created_at": self.created_at.isoformat() if self.created_at else None
        }


# ==================== AUDIT LOGS ====================

class AuditLog(Base):
    __tablename__ = 'audit_logs'

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey('users.id'), nullable=False)
    action = Column(String(100), nullable=False)
    tool_used = Column(String(50))
    payload = Column(Text)
    status = Column(String(20), default='success')  # success, failed
    ip_address = Column(String(50))
    timestamp = Column(DateTime, default=datetime.utcnow)

    # Relationships
    user = relationship("User", back_populates="audit_logs")

    def to_dict(self):
        return {
            "id": self.id,
            "user_id": self.user_id,
            "action": self.action,
            "tool": self.tool_used,
            "payload": self.payload,
            "status": self.status,
            "ip": self.ip_address,
            "timestamp": self.timestamp.isoformat() if self.timestamp else None
        }


# ==================== DATABASE INIT ====================

def init_db(db_url=None):
    """Initialize database"""
    if db_url is None:
        db_url = os.getenv('DATABASE_URL', 'sqlite:///./data/sairolotech.db')

    engine = create_engine(db_url)
    Base.metadata.create_all(engine)
    Session = sessionmaker(bind=engine)
    return Session()


def get_session():
    """Get database session"""
    return init_db()
