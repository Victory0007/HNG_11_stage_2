import uuid

from sqlalchemy import Table, Column, Integer, ForeignKey
from sqlalchemy.orm import relationship

from app.main import db

# Association table for many-to-many relationship
user_organization = Table('user_organization', db.Model.metadata,
                          Column('user_id', Integer, ForeignKey('users.id'), primary_key=True),
                          Column('org_id', Integer, ForeignKey('organizations.id'), primary_key=True)
                          )


class UserModel(db.Model):
    __tablename__ = "users"

    id = db.Column(db.Integer, primary_key=True)
    userId = db.Column(db.String(80), unique=True, default=lambda: str(uuid.uuid4()))
    firstName = db.Column(db.String(80), nullable=False)
    lastName = db.Column(db.String(80), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.String(255), nullable=False)
    phone = db.Column(db.String(20))

    organizations = relationship('OrgModel', secondary='user_organization', back_populates="users")

    def __init__(self, firstName, lastName, email, password, phone=None):
        self.firstName = firstName
        self.lastName = lastName
        self.email = email
        self.password = password
        self.phone = phone

    def to_dict(self):
        return {
            'userId': self.userId,
            'firstName': self.firstName,
            'lastName': self.lastName,
            'email': self.email,
            'phone': self.phone,
        }

    def validate_user(self):
        """User Validation"""
        errors = []
        if not isinstance(self.firstName, str):
            errors.append({
                'field': "firstName",
                'message': "First Name must be a string"
            })
        if not isinstance(self.lastName, str):
            errors.append({
                'field': "lastName",
                'message': "Last Name must be a string"
            })
        if not isinstance(self.email, str):
            errors.append({
                'field': "email",
                'message': "Email must be a string"
            })
        if not isinstance(self.password, str):
            errors.append({
                'field': "password",
                'message': "Password must be a string"
            })
        if self.phone and not isinstance(self.phone, str):
            errors.append({
                'field': "phone",
                'message': "Phone must be a string"
            })
        if not self.firstName:
            errors.append({
                "field": "firstName",
                "message": "First Name must not be null"
            })
        if not self.lastName:
            errors.append({
                "field": "lastName",
                "message": "Last Name must not be null"
            })
        if not self.email:
            errors.append({
                "field": "email",
                "message": 'Email field must not be null'
            })
        if self.email and '@' not in self.email:
            errors.append({
                "field": "email",
                "message": "Invalid email"
            })
        if not self.password:
            errors.append({
                "field": "password",
                "message": "Password field cannot be null"
            })
        if self.email:
            user = UserModel.query.filter_by(email=self.email).first()
            if user:
                errors.append({
                    "field": "email",
                    "message": "User already exists with this email address"
                })
        return errors

class OrgModel(db.Model):
    __tablename__ = "organizations"

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    orgId = db.Column(db.String(80), unique=True, default=lambda: str(uuid.uuid4()))
    name = db.Column(db.String(80), nullable=False)
    description = db.Column(db.String(255))

    users = relationship('UserModel', secondary=user_organization, back_populates="organizations")

    def to_dict(self):
        return {
            "orgId": self.orgId,
            "name": self.name,
            "description": self.description
        }
