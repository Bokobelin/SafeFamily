"""Schemas for serializing and deserializing core models."""

from marshmallow import Schema, fields


class UserSchema(Schema):
    """Schema for serializing and deserializing User objects."""

    id = fields.String()
    username = fields.String(required=True)
    email = fields.Email(required=True)
