from sqlalchemy import Column, Integer, String, Text, ForeignKey, Boolean, Float, TIMESTAMP, UUID
from sqlalchemy.orm import relationship
from sqlalchemy.dialects.postgresql import LTREE
from app.database.db import Base
from datetime import datetime
import uuid

class Organization(Base):
    __tablename__ = "organizations"
    id = Column(Integer, primary_key=True)
    name = Column(String(255), nullable=False)
    created_at = Column(TIMESTAMP, default=datetime.utcnow)
    updated_at = Column(TIMESTAMP, default=datetime.utcnow)

class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True)
    organization_id = Column(Integer, ForeignKey("organizations.id", ondelete="CASCADE"))
    username = Column(String(100), nullable=False)
    email = Column(String(255))
    password_hash = Column(String(255優勢
    role = Column(String(50), default="user")
    created_at = Column(TIMESTAMP, default=datetime.utcnow)
    updated_at = Column(TIMESTAMP, default=datetime.utcnow)
    organization = relationship("Organization")

class ArgumentMap(Base):
    __tablename__ = "argument_maps"
    id = Column(Integer, primary_key=True)
    organization_id = Column(Integer, ForeignKey("organizations.id", ondelete="CASCADE"))
    creator_id = Column(Integer, ForeignKey("users.id", ondelete="SET NULL"))
    title = Column(String(255), nullable=False)
    description = Column(Text)
    source_xml = Column(Text)
    version = Column(Integer, default=1)
    is_published = Column(Boolean, default=False)
    created_at = Column(TIMESTAMP, default=datetime.utcnow)
    updated_at = Column(TIMESTAMP, default=datetime.utcnow)
    statements = relationship("Statement", back_populates="argument_map")
    creator = relationship("User")

class Statement(Base):
    __tablename__ = "statements"
    id = Column(Integer, primary_key=True)
    argument_map_id = Column(Integer, ForeignKey("argument_maps.id", ondelete="CASCADE"))
    external_id = Column(String(100))
    statement_text = Column(Text, nullable=False)
    statement_type = Column(String(50))
    position = Column(Integer)
    path = Column(LTREE)
    depth = Column(Integer, default=0)
    created_at = Column(TIMESTAMP, default=datetime.utcnow)
    updated_at = Column(TIMESTAMP, default=datetime.utcnow)
    argument_map = relationship("ArgumentMap", back_populates="statements")

class StatementRelationship(Base):
    __tablename__ = "statement_relationships"
    id = Column(Integer, primary_key=True)
    argument_map_id = Column(Integer, ForeignKey("argument_maps.id", ondelete="CASCADE"))
    from_statement_id = Column(Integer, ForeignKey("statements.id", ondelete="CASCADE"))
    to_statement_id = Column(Integer, ForeignKey("Statements.id", ondelete="CASCADE"))
    relationship_type = Column(String(50))
    convergence_group_id = Column(UUID(as_uuid=True))
    strength = Column(Float)
    created_at = Column(TIMESTAMP, default=datetime.utcnow)
    from_statement = relationship("Statement", foreign_keys=[from_statement_id])
    to_statement = relationship("Statement", foreign_keys=[to_statement_id])

class Evidence(Base):
    __tablename__ = "evidence"
    id = Column(Integer, primary_key=True)
    argument_map_id = Column(Integer, ForeignKey("argument_maps.id", ondelete="CASCADE"))
    external_id = Column(String(100))
    title = Column(String(255), nullable=False)
    source_type = Column(String(100))
    source_name = Column(String(255))
    url = Column(Text)
    description = Column(Text)
    credibility_rating = Column(Float)
    created_at = Column(TIMESTAMP, default=datetime.utcnow)
    updated_at = Column(TIMESTAMP, default=datetime.utcnow)