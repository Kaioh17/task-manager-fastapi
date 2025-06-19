from sqlalchemy import Column, Integer, String, ForeignKey, DateTime, UniqueConstraint
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.sql.expression import text
from sqlalchemy.orm import relationship
from ..database import Base
import random
from sqlalchemy.sql.sqltypes import TIMESTAMP

# from datetime import datetime

# def random_idx():
#     return random.randint(1, 1000000)

class Organizations(Base):
    __tablename__ = "organizations"
    org_id = Column(Integer, primary_key=True, autoincrement=True, nullable=False, index=True)
    org_name = Column(String, nullable=False, unique=True, index=True) 
    org_description = Column(String, nullable=True)
    created_on = Column(TIMESTAMP(timezone = True), nullable=False
                        ,server_default=text('now()'))
    user = relationship("Users", back_populates="organization")

#organiztion settings 
class OrgSettings(Base):
    __tablename__ = "org_settings"
    id = Column(Integer, primary_key=True, autoincrement=True, nullable=False, index=True)
    org_id = Column(Integer, ForeignKey("organizations.org_id", ondelete="CASCADE"),unique=True, nullable=False, index=True)
    settings = Column(JSONB, nullable=False, default=dict)
    

class Users(Base):
    __tablename__ = "users"
    user_id = Column(Integer, primary_key=True, autoincrement=True, nullable=False, index=True)
    org_id = Column(Integer, ForeignKey("organizations.org_id", ondelete="CASCADE"), nullable=False, index=True)
    first_name = Column(String(200), nullable=False)
    last_name = Column(String(200), nullable=False)
    user_email = Column(String(200), nullable=False, unique=True, index=True)
    user_password = Column(String(200), nullable=False)
    user_role = Column(String, nullable=False, index=True)
    created_on = Column(TIMESTAMP(timezone = True), nullable=False
                        ,server_default=text('now()'))
    organization = relationship("Organizations", back_populates="user")
    
    

class Tasks(Base):
    __tablename__ = "tasks"
    task_id = Column(Integer, primary_key=True, autoincrement=True, nullable=False, index=True)
    org_id = Column(Integer, ForeignKey("organizations.org_id",  ondelete="CASCADE"), nullable=False, index=True)
    task_name = Column(String, nullable=False, index=True)
    task_description = Column(String, nullable=True)
    created_on = Column(TIMESTAMP(timezone = True), nullable=False
                        ,server_default=text('now()'))
    assignments = relationship("TaskAssignment", back_populates= "task")

class TaskAssignment(Base):
    __tablename__ = "task_assignments"
    assignment_id = Column(Integer, primary_key=True, autoincrement=True, nullable=False, index=True)
    task_id = Column(Integer, ForeignKey("tasks.task_id",  ondelete="CASCADE"), nullable=False, index=True)
    org_id = Column(Integer, ForeignKey("organizations.org_id",  ondelete="CASCADE"), nullable=False, index=True)
    user_id = Column(Integer, ForeignKey("users.user_id", ondelete="CASCADE"), nullable=False, index=True)
    task_name = Column(String, nullable=False, index=True)
    task_description = Column(String, nullable=True)
    due_date = Column(DateTime , nullable=False)
    task_status = Column(String, nullable=False, server_default=text("'pending'"), index=True)
    proof_of_completion = Column(String, nullable = True, server_default=text("'awaiting'"))
    assigned_by_id = Column(Integer, ForeignKey("users.user_id", ondelete="CASCADE"), nullable=False, index=True)
    created_on = Column(TIMESTAMP(timezone = True), nullable=False
                        ,server_default=text('now()'))
    
    __table_args__ = (
        UniqueConstraint('user_id', 'task_name', name = 'unique_user_task'),
    )

    task = relationship("Tasks", back_populates="assignments")

class AuditLog(Base):
    __tablename__ = "audit_log"
    assignment_id = Column(Integer, primary_key=True, autoincrement=True, nullable=False, index=True)
    task_id = Column(Integer, ForeignKey("tasks.task_id",  ondelete="CASCADE"), nullable=False, index=True)
    org_id = Column(Integer, ForeignKey("organizations.org_id",  ondelete="CASCADE"), nullable=False, index=True)
    user_id = Column(Integer, ForeignKey("users.user_id", ondelete="CASCADE"), nullable=False, index=True)
    task_name = Column(String, nullable=False, index=True)
    task_description = Column(String, nullable=True)
    task_status = Column(String, nullable=False, index=True)
    proof_of_completion = Column(String, nullable = True, server_default=text("'awaiting'"))
    completed_on = Column(TIMESTAMP(timezone = True), nullable=False
                        ,server_default=text('now()'))
    approved_by = Column(Integer, ForeignKey("users.user_id", ondelete="CASCADE"), nullable=True, index=True)
    assigned_on = Column(TIMESTAMP(timezone = True), nullable=False)

# Saves all completed and approved tasks in archive (deleted after a month)
class ApprovedTaskArchive(Base):
    __tablename__ = "approved_task_archives"
    assignment_id = Column(Integer, primary_key=True, autoincrement=True, nullable=False, index=True)
    task_id = Column(Integer, ForeignKey("tasks.task_id",  ondelete="CASCADE"), nullable=False, index=True)
    org_id = Column(Integer, ForeignKey("organizations.org_id",  ondelete="CASCADE"), nullable=False, index=True)
    user_id = Column(Integer, ForeignKey("users.user_id", ondelete="CASCADE"), nullable=False, index=True)
    task_name = Column(String, nullable=False, index=True)
    task_description = Column(String, nullable=True)
    task_status = Column(String, nullable=False, index=True)
    proof_of_completion = Column(String, nullable = True, server_default=text("'awaiting'"))
    completed_on = Column(TIMESTAMP(timezone = True), nullable=False)
    approved_by = Column(Integer, ForeignKey("users.user_id", ondelete="CASCADE"), nullable=False, index=True)
    assigned_on = Column(TIMESTAMP(timezone = True), nullable=False)
    created_on = Column(TIMESTAMP(timezone = True), nullable=False
                        ,server_default=text('now()'))

