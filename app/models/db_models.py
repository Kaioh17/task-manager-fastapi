from sqlalchemy import Column, Integer, String, ForeignKey
from sqlalchemy.sql.expression import text

from ..database import Base
import random
from sqlalchemy.sql.sqltypes import TIMESTAMP

# def random_idx():
#     return random.randint(1, 1000000)

class Organizations(Base):
    __tablename__ = "organizations"
    org_id = Column(Integer, primary_key=True, server_default=text("floor(random() * 1000000 + 1)::int"), nullable=False)
    org_name = Column(String, nullable=False, unique=True) 
    org_description = Column(String, nullable=True)
    created_on = Column(TIMESTAMP(timezone = True), nullable=False
                        ,server_default=text('now()'))

class Users(Base):
    __tablename__ = "users"
    user_id = Column(Integer, primary_key=True, server_default=text("floor(random() * 1000000 + 1)::int"), nullable=False)
    org_id = Column(Integer, ForeignKey("organizations.org_id", ondelete="CASCADE"), nullable=False)
    first_name = Column(String(200), nullable=False)
    last_name = Column(String(200), nullable=False)
    user_email = Column(String(200), nullable=False, unique=True)
    user_password = Column(String(200), nullable=False)
    user_role = Column(String, nullable=False)
    created_on = Column(TIMESTAMP(timezone = True), nullable=False
                        ,server_default=text('now()'))

class Tasks(Base):
    __tablename__ = "tasks"
    task_id = Column(Integer, primary_key=True, server_default=text("floor(random() * 1000000 + 1)::int"), nullable=False)
    org_id = Column(Integer, ForeignKey("organizations.org_id",  ondelete="CASCADE"), nullable=False)
    task_name = Column(String, nullable=False)
    task_description = Column(String, nullable=True)
    created_on = Column(TIMESTAMP(timezone = True), nullable=False
                        ,server_default=text('now()'))
class TaskAssignment(Base):
    __tablename__ = "task_assignments"
    task_id = Column(Integer, primary_key=True, server_default=text("floor(random() * 1000000 + 1)::int"), nullable=False)
    org_id = Column(Integer, ForeignKey("organizations.org_id",  ondelete="CASCADE"), nullable=False)
    user_id = Column(Integer, ForeignKey("users.user_id", ondelete="CASCADE"), nullable=False)
    task_name = Column(String, nullable=False)
    task_description = Column(String, nullable=True)
    due_date = Column(String, nullable=False)
    task_status = Column(String, nullable=False)
    proof_of_completion = Column(String, nullable = False)
    created_on = Column(TIMESTAMP(timezone = True), nullable=False
                        ,server_default=text('now()'))
    
class AUditLog(Base):
    __tablename__ = "audit_log"
    assignment_id = Column(Integer, primary_key=True, server_default=text("floor(random() * 1000000 + 1)::int"), nullable=False)
    task_id = Column(Integer, ForeignKey("organizations.org_id",  ondelete="CASCADE"), nullable=False)
    org_id = Column(Integer, ForeignKey("organizations.org_id",  ondelete="CASCADE"), nullable=False)
    user_id = Column(Integer, ForeignKey("users.user_id", ondelete="CASCADE"), nullable=False)
    task_name = Column(String, nullable=False)
    task_description = Column(String, nullable=True)
    task_status = Column(String, nullable=False)
    completed_on = Column(TIMESTAMP(timezone = True), nullable=False
                        ,server_default=text('now()'))
    assigned_on = Column(TIMESTAMP(timezone = True), nullable=False)