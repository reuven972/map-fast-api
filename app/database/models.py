from sqlalchemy import Column, Integer, String, Text, ForeignKey, Boolean, Float, TIMESTAMP, UniqueConstraint, CheckConstraint
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy_utils import LtreeType
from sqlalchemy.orm import relationship
from app.database.db import Base
from datetime import datetime, UTC
import uuid

LTREE = LtreeType

# Table: organizations
class Organization(Base):
    __tablename__ = "organizations"
    id = Column(Integer, primary_key=True)
    name = Column(String(255), nullable=False)
    domain = Column(String(255))
    created_at = Column(TIMESTAMP, default=datetime.now(UTC))
    updated_at = Column(TIMESTAMP, default=datetime.now(UTC))
    users = relationship("User", back_populates="organization")
    mft_profiles = relationship("MFTProfile", back_populates="organization")
    argument_maps = relationship("ArgumentMap", back_populates="organization")

# Table: users
class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True)
    uuid = Column(UUID(as_uuid=True), default=uuid.uuid4, unique=True)
    organization_id = Column(Integer, ForeignKey("organizations.id", ondelete="CASCADE"))
    username = Column(String(100), nullable=False)
    email = Column(String(255))
    password_hash = Column(Text, nullable=False)
    role = Column(String(50), default="user")
    created_at = Column(TIMESTAMP, default=datetime.now(UTC))
    updated_at = Column(TIMESTAMP, default=datetime.now(UTC))
    organization = relationship("Organization", back_populates="users")
    created_argument_maps = relationship("ArgumentMap", back_populates="creator")
    user_profile_preferences = relationship("UserProfilePreference", back_populates="user")
    browser_extension_setting = relationship("BrowserExtensionSetting", back_populates="user", uselist=False)
    import_logs = relationship("ImportLog", back_populates="user")
    __table_args__ = (
        UniqueConstraint("organization_id", "username"),
        CheckConstraint("role IN ('admin', 'user', 'viewer')", name="ck_users_role"),
    )

# Table: mft_profiles
class MFTProfile(Base):
    __tablename__ = "mft_profiles"
    id = Column(Integer, primary_key=True)
    organization_id = Column(Integer, ForeignKey("organizations.id", ondelete="CASCADE"))
    name = Column(String(100), nullable=False)
    description = Column(Text)
    care_harm = Column(Float, default=0.0)
    fairness_cheating = Column(Float, default=0.0)
    loyalty_betrayal = Column(Float, default=0.0)
    authority_subversion = Column(Float, default=0.0)
    sanctity_degradation = Column(Float, default=0.0)
    is_default = Column(Boolean, default=False)
    created_at = Column(TIMESTAMP, default=datetime.now(UTC))
    updated_at = Column(TIMESTAMP, default=datetime.now(UTC))
    organization = relationship("Organization", back_populates="mft_profiles")
    user_profile_preferences = relationship("UserProfilePreference", back_populates="mft_profile")


# Table: user_profile_preferences
class UserProfilePreference(Base):
    __tablename__ = "user_profile_preferences"
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"))
    mft_profile_id = Column(Integer, ForeignKey("mft_profiles.id", ondelete="CASCADE"))
    is_default = Column(Boolean, default=False)
    created_at = Column(TIMESTAMP, default=datetime.now(UTC))
    user = relationship("User", back_populates="user_profile_preferences")
    mft_profile = relationship("MFTProfile", back_populates="user_profile_preferences")
    __table_args__ = (UniqueConstraint("user_id", "mft_profile_id"),)

# Table: argument_maps
class ArgumentMap(Base):
    __tablename__ = "argument_maps"
    id = Column(Integer, primary_key=True)
    uuid = Column(UUID(as_uuid=True), default=uuid.uuid4, unique=True)
    organization_id = Column(Integer,  ForeignKey("organizations.id", ondelete="CASCADE"), nullable=True)
    creator_id = Column(Integer, ForeignKey("users.id", ondelete="SET NULL"), nullable=True)
    title = Column(String(255), nullable=False)
    description = Column(Text)
    source_xml = Column(Text)
    version = Column(Integer, default=1)
    is_published = Column(Boolean, default=False)
    created_at = Column(TIMESTAMP, default=datetime.now(UTC))
    updated_at = Column(TIMESTAMP, default=datetime.now(UTC))
    organization = relationship("Organization", back_populates="argument_maps")
    creator = relationship("User", back_populates="created_argument_maps")
    statements = relationship("Statement", back_populates="argument_map")
    versions = relationship("ArgumentMapVersion", back_populates="argument_map")
    statement_relationships = relationship("StatementRelationship", back_populates="argument_map")
    cross_references_as_source = relationship(
        "CrossMapReference",
        foreign_keys="CrossMapReference.source_map_id",  # Chaîne pour gérer les forward references
        back_populates="source_map"
    )
    cross_references_as_target = relationship(
        "CrossMapReference",
        foreign_keys="CrossMapReference.target_map_id",  # Chaîne pour gérer les forward references
        back_populates="target_map"
    )    
    evidences = relationship("Evidence", back_populates="argument_map")
    entity_relationships = relationship("EntityRelationship", back_populates="argument_map")
    import_logs = relationship("ImportLog", back_populates="argument_map")

# Table: argument_map_versions
class ArgumentMapVersion(Base):
    __tablename__ = "argument_map_versions"
    id = Column(Integer, primary_key=True)
    argument_map_id = Column(Integer, ForeignKey("argument_maps.id", ondelete="CASCADE"))
    version = Column(Integer, nullable=False)
    creator_id = Column(Integer, ForeignKey("users.id", ondelete="SET NULL"))
    source_xml = Column(Text)
    change_description = Column(Text)
    created_at = Column(TIMESTAMP, default=datetime.now(UTC))
    argument_map = relationship("ArgumentMap", back_populates="versions")
    creator = relationship("User")
    __table_args__ = (UniqueConstraint("argument_map_id", "version"),)

# Table: statements
class Statement(Base):
    __tablename__ = "statements"
    id = Column(Integer, primary_key=True)
    uuid = Column(UUID(as_uuid=True), default=uuid.uuid4, unique=True)
    argument_map_id = Column(Integer, ForeignKey("argument_maps.id", ondelete="CASCADE"))
    external_id = Column(String(100))
    statement_text = Column(Text, nullable=False)
    statement_type = Column(String(50))
    position = Column(Integer)
    path = Column(LTREE)
    depth = Column(Integer, default=0)
    created_at = Column(TIMESTAMP, default=datetime.now(UTC))
    updated_at = Column(TIMESTAMP, default=datetime.now(UTC))
    argument_map = relationship("ArgumentMap", back_populates="statements")
    moralbert_scores = relationship("MoralBERTScore", back_populates="statement")
    outgoing_relationships = relationship("StatementRelationship", foreign_keys="[StatementRelationship.from_statement_id]", back_populates="from_statement")
    incoming_relationships = relationship("StatementRelationship", foreign_keys="[StatementRelationship.to_statement_id]", back_populates="to_statement")
    cross_references = relationship("CrossMapReference", back_populates="source_statement")

# Table: moralbert_scores
class MoralBERTScore(Base):
    __tablename__ = "moralbert_scores"
    id = Column(Integer, primary_key=True)
    statement_id = Column(Integer, ForeignKey("statements.id", ondelete="CASCADE"))
    care_harm_score = Column(Float)
    fairness_cheating_score = Column(Float)
    loyalty_betrayal_score = Column(Float)
    authority_subversion_score = Column(Float)
    sanctity_degradation_score = Column(Float)
    imported_at = Column(TIMESTAMP, default=datetime.now(UTC))
    updated_at = Column(TIMESTAMP, default=datetime.now(UTC))
    statement = relationship("Statement", back_populates="moralbert_scores")


# Table: statement_relationships
class StatementRelationship(Base):
    __tablename__ = "statement_relationships"
    id = Column(Integer, primary_key=True)
    uuid = Column(UUID(as_uuid=True), default=uuid.uuid4, unique=True)
    argument_map_id = Column(Integer, ForeignKey("argument_maps.id", ondelete="CASCADE"))
    from_statement_id = Column(Integer, ForeignKey("statements.id", ondelete="CASCADE"))
    to_statement_id = Column(Integer, ForeignKey("statements.id", ondelete="CASCADE"))
    relationship_type = Column(String(50))
    convergence_group_id = Column(UUID(as_uuid=True))
    strength = Column(Float)
    created_at = Column(TIMESTAMP, default=datetime.now(UTC))
    argument_map = relationship("ArgumentMap", back_populates="statement_relationships")
    from_statement = relationship("Statement", foreign_keys=[from_statement_id], back_populates="outgoing_relationships")
    to_statement = relationship("Statement", foreign_keys=[to_statement_id], back_populates="incoming_relationships") 
    __table_args__ = (
        UniqueConstraint("from_statement_id", "to_statement_id"),
        CheckConstraint("strength BETWEEN 0 AND 1", name="ck_statement_relationships_strength"),
    )

# Table: cross_map_references
class CrossMapReference(Base):
    __tablename__ = "cross_map_references"
    id = Column(Integer, primary_key=True)
    source_map_id = Column(Integer, ForeignKey("argument_maps.id"))
    target_map_id = Column(Integer, ForeignKey("argument_maps.id"))
    source_statement_id = Column(Integer, ForeignKey("statements.id", ondelete="CASCADE"))
    reference_type = Column(String(50))
    description = Column(Text)
    created_at = Column(TIMESTAMP, default=datetime.now(UTC))
    source_map = relationship(
        "ArgumentMap",
        foreign_keys=[source_map_id],  # Colonne définie localement, pas de forward reference
        back_populates="cross_references_as_source"
    )
    target_map = relationship(
        "ArgumentMap",
        foreign_keys=[target_map_id],  # Colonne définie localement, pas de forward reference
        back_populates="cross_references_as_target"
    )
    source_statement = relationship("Statement", back_populates="cross_references")
    __table_args__ = (UniqueConstraint("source_statement_id", "target_map_id"),)

# Table: evidence
class Evidence(Base):
    __tablename__ = "evidence"
    id = Column(Integer, primary_key=True)
    uuid = Column(UUID(as_uuid=True), default=uuid.uuid4, unique=True)
    argument_map_id = Column(Integer, ForeignKey("argument_maps.id", ondelete="CASCADE"))
    external_id = Column(String(100))
    title = Column(String(255), nullable=False)
    source_type = Column(String(100))
    source_name = Column(String(255))
    url = Column(Text)
    description = Column(Text)
    credibility_rating = Column(Float)
    created_at = Column(TIMESTAMP, default=datetime.now(UTC))
    updated_at = Column(TIMESTAMP, default=datetime.now(UTC))
    argument_map = relationship("ArgumentMap", back_populates="evidences")
    __table_args__ = (
        UniqueConstraint("argument_map_id", "external_id"),
    )

# Table: entity_relationships
class EntityRelationship(Base):
    __tablename__ = "entity_relationships"
    id = Column(Integer, primary_key=True)
    uuid = Column(UUID(as_uuid=True), default=uuid.uuid4, unique=True)
    argument_map_id = Column(Integer, ForeignKey("argument_maps.id", ondelete="CASCADE"))
    from_type = Column(String(50))
    from_id = Column(Integer, nullable=False)
    to_type = Column(String(50))
    to_id = Column(Integer, nullable=False)
    relationship_type = Column(String(50))
    created_at = Column(TIMESTAMP, default=datetime.now(UTC))
    argument_map = relationship("ArgumentMap", back_populates="entity_relationships")
    __table_args__ = (UniqueConstraint("from_type", "from_id", "to_type", "to_id"),)

# Table: browser_extension_settings
class BrowserExtensionSetting(Base):
    __tablename__ = "browser_extension_settings"
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), unique=True)
    default_mft_profile_id = Column(Integer, ForeignKey("mft_profiles.id", ondelete="SET NULL"))
    auto_generate_counter_arguments = Column(Boolean, default=True)
    show_evidence = Column(Boolean, default=True)
    show_critiques = Column(Boolean, default=True)
    max_results = Column(Integer, default=5)
    created_at = Column(TIMESTAMP, default=datetime.now(UTC))
    updated_at = Column(TIMESTAMP, default=datetime.now(UTC))
    user = relationship("User", back_populates="browser_extension_setting")
    default_mft_profile = relationship("MFTProfile")

# Table: import_logs
class ImportLog(Base):
    __tablename__ = "import_logs"
    id = Column(Integer, primary_key=True)
    argument_map_id = Column(Integer, ForeignKey("argument_maps.id", ondelete="CASCADE"))
    user_id = Column(Integer, ForeignKey("users.id", ondelete="SET NULL"))
    success = Column(Boolean, nullable=False)
    message = Column(Text)
    error_details = Column(JSONB)
    import_type = Column(String(50), default="xml")
    created_at = Column(TIMESTAMP, default=datetime.now(UTC))
    argument_map = relationship("ArgumentMap", back_populates="import_logs")
    user = relationship("User", back_populates="import_logs")

# Table: xml_schema_definitions
class XMLSchemaDefinition(Base):
    __tablename__ = "xml_schema_definitions"
    id = Column(Integer, primary_key=True)
    name = Column(String(255), nullable=False)
    version = Column(String(50), nullable=False)
    schema_type = Column(String(50))
    schema_content = Column(Text, nullable=False)
    description = Column(Text)
    is_active = Column(Boolean, default=True)
    created_at = Column(TIMESTAMP, default=datetime.now(UTC))
    updated_at = Column(TIMESTAMP, default=datetime.now(UTC))
    __table_args__ = (
        UniqueConstraint("name", "version", "schema_type"),
        CheckConstraint("schema_type IN ('XSD', 'SCHEMATRON')", name="ck_xml_schema_definitions_schema_type"),
    )