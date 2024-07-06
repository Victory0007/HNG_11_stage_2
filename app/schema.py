from marshmallow import Schema, fields


class UserRegSchema(Schema):
    userId = fields.Str(dump_only=True)
    firstName = fields.Str(required=True)
    lastName = fields.Str(required=True)
    email = fields.Str(required=True)
    password = fields.Str(required=True, load_only=True)
    phone = fields.Str(required=True)


class UserLoginSchema(Schema):
    email = fields.Str(required=True)
    password = fields.Str(required=True, load_only=True)


class OrgSchema(Schema):
    orgId = fields.Str(dump_only=True)
    name = fields.Str(required=True)
    description = fields.Str()
