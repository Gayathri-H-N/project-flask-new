from extensions import ma
from marshmallow import fields, validate, ValidationError, EXCLUDE

class UserSchema(ma.Schema):
    class Meta:
        unknown = EXCLUDE

    username = fields.Str(
        required=True,
        validate=[
            validate.Length(min=3, error="Username must be at least 3 characters long"),
            validate.Regexp(r'^[a-zA-Z0-9]+$', error="Username must be alphanumeric")
        ]
    )
    first_name = fields.Str(
        required=True,
        validate=[
            validate.Regexp(r'^[a-zA-Z]+$', error="First name must contain only letters")
        ]
    )
    last_name = fields.Str(
        required=True,
        validate=[
            validate.Regexp(r'^[a-zA-Z]+$', error="Last name must contain only letters")
        ]
    )
    email = fields.Email(required=True, error_messages={"invalid": "Invalid email address"})
    mobile_number = fields.Str(
        required=True,
        validate=validate.Regexp(r'^[6-9]\d{9}$', error="Mobile number must start with 6-9 and have 10 digits")
    )
    password = fields.Str(
    required=True,
    load_only=True,
    validate=[
        validate.Length(min=6, error="Password must be at least 6 characters long"),
        validate.Regexp(
            r'^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)(?=.*[^a-zA-Z0-9]).+$',
            error=(
                "Password must contain at least one uppercase letter, "
                "one lowercase letter, one number, and one special character"
            )
        )
    ]
)

class LoginSchema(ma.Schema):
    class Meta:
        unknown = EXCLUDE

    email = fields.Email(required=True, error_messages={"required": "Email is required", "invalid": "Invalid email address"})
    password = fields.Str(required=True, load_only=True, error_messages={"required": "Password is required"})
