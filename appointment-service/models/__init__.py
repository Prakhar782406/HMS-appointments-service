"""
Models package initialization
"""
from .db import db
from .user import User
from .appointment import Appointment

__all__ = ['db', 'User', 'Appointment']

