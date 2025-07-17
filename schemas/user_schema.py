import re
from extensions import ma
from marshmallow import fields, validate, ValidationError, EXCLUDE, validates

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
    mobile_number = fields.Str(required=True)
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
    
    @validates("mobile_number")
    def validate_mobile_number(self, value):
        if not value.startswith("+"):
            raise ValidationError("Mobile number must include the country code (e.g., +91XXXXXXXXXX)")
        pattern = r'^\+\d{10,15}$'
        if not re.fullmatch(pattern, value):
            raise ValidationError("Invalid mobile number format. Must be in E.164 format, e.g., +919876543210")
        

class LoginSchema(ma.Schema):
    class Meta:
        unknown = EXCLUDE

    email = fields.Email(required=True, error_messages={"required": "Email is required", "invalid": "Invalid email address"})
    password = fields.Str(required=True, load_only=True, error_messages={"required": "Password is required"})
