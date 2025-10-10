from marshmallow import Schema, fields


class UserSchema(Schema):
    id = fields.String()
    username = fields.String(required=True)
    email = fields.Email(required=True)
