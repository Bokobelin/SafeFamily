"""Core models for Safe Family application."""

import uuid
from datetime import datetime, timezone

from werkzeug.security import check_password_hash, generate_password_hash

from src.safe_family.core.extensions import db


class User(db.Model):
    """User model for Safe Family application."""

    __tablename__ = "users"

    id = db.Column(db.String(), primary_key=True, default=(uuid.uuid4))
    username = db.Column(db.String(), nullable=False)
    email = db.Column(db.String(), unique=True, nullable=False)
    password_hash = db.Column(db.String(256), nullable=False)
    role = db.Column(db.String(20))
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))
    updated_at = db.Column(
        db.DateTime,
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
    )

    def __repr__(self) -> str:
        """Return a string representation of the User."""
        return f"<User(username='{self.username}', Role: '{self.role}', email='{self.email}')>"

    def get_id(self):
        """Return the user ID."""
        return self.id

    def set_password(self, password):
        """Set the user's password."""
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        """Check if the provided password matches the stored password hash."""
        return check_password_hash(self.password_hash, password)

    def change_password(self, old_password, new_password):
        """Change the user's password."""
        if self.check_password(old_password):
            self.password_hash = generate_password_hash(new_password)
            self.save()
            return True
        return False

    @classmethod
    def get_user_by_username(cls, username):
        """Get a user by their username."""
        return cls.query.filter_by(username=username).first()

    def save(self):
        """Save the user to the database."""
        db.session.add(self)
        db.session.commit()

    def delete(self):
        """Delete the user from the database."""
        db.session.delete(self)
        db.session.commit()


class TokenBlocklist(db.Model):
    """Model for storing revoked JWT tokens."""

    __tablename__ = "token_blocklist"

    id = db.Column(db.Integer, primary_key=True)
    jti = db.Column(db.String(), nullable=False, index=True)
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))

    def __repr__(self) -> str:
        """Return a string representation of the TokenBlocklist."""
        return f"<TokenBlocklist(jti='{self.jti}')>"

    def save(self):
        """Save the token blocklist entry to the database."""
        db.session.add(self)
        db.session.commit()
