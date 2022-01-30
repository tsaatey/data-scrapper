from marshmallow import Schema, fields


class APIResponseSchema(Schema):
    status = fields.Boolean()
    message = fields.Str()
    data = fields.Str()
