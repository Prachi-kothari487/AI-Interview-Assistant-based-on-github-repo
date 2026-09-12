from sqlalchemy import (
    Column,
    BigInteger,
    String,
    Text,
    Enum,
    TIMESTAMP,
    ForeignKey
)

from sqlalchemy.sql import func

from database.connection import Base


# ==========================================
# USER MODEL
# ==========================================

class User(Base):

    __tablename__ = "users"

    id = Column(
        BigInteger,
        primary_key=True,
        autoincrement=True
    )

    name = Column(
        String(100),
        nullable=False
    )

    email = Column(
        String(255),
        nullable=False,
        unique=True
    )

    password_hash = Column(
        String(255),
        nullable=False
    )

    created_at = Column(
        TIMESTAMP,
        server_default=func.current_timestamp()
    )


# ==========================================
# PROJECT MODEL
# ==========================================

class Project(Base):

    __tablename__ = "projects"

    id = Column(
        BigInteger,
        primary_key=True,
        autoincrement=True
    )

    user_id = Column(
        BigInteger,
        ForeignKey("users.id"),
        nullable=False
    )

    name = Column(
        String(255),
        nullable=False
    )

    github_url = Column(
        Text,
        nullable=True
    )

    source_type = Column(
        Enum("github", "zip"),
        nullable=False
    )

    status = Column(
        Enum(
            "pending",
            "analyzing",
            "completed",
            "failed"
        ),
        default="pending"
    )

    created_at = Column(
        TIMESTAMP,
        server_default=func.current_timestamp()
    )


# ==========================================
# PROJECT FILE MODEL
# ==========================================

class ProjectFile(Base):

    __tablename__ = "project_files"

    id = Column(
        BigInteger,
        primary_key=True,
        autoincrement=True
    )

    project_id = Column(
        BigInteger,
        ForeignKey("projects.id"),
        nullable=False
    )

    file_path = Column(
        Text,
        nullable=False
    )

    file_name = Column(
        String(255),
        nullable=False
    )

    extension = Column(
        String(50),
        nullable=True
    )

    language = Column(
        String(100),
        nullable=True
    )

    size = Column(
        BigInteger,
        nullable=True
    )


# ==========================================
# PROJECT TECHNOLOGY MODEL
# ==========================================

class ProjectTechnology(Base):

    __tablename__ = "project_technologies"

    id = Column(
        BigInteger,
        primary_key=True,
        autoincrement=True
    )

    project_id = Column(
        BigInteger,
        ForeignKey("projects.id"),
        nullable=False
    )

    technology = Column(
        String(100),
        nullable=False
    )

    category = Column(
        String(100),
        nullable=True
    )


# ==========================================
# PROJECT MODULE MODEL
# ==========================================

class ProjectModule(Base):

    __tablename__ = "project_modules"

    id = Column(
        BigInteger,
        primary_key=True,
        autoincrement=True
    )

    project_id = Column(
        BigInteger,
        ForeignKey("projects.id"),
        nullable=False
    )

    module_name = Column(
        String(255),
        nullable=False
    )

    description = Column(
        Text,
        nullable=True
    )