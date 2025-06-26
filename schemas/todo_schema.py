from extensions import ma
from marshmallow import fields, validates_schema, ValidationError, validate, EXCLUDE

class ToDoCreateSchema(ma.Schema):
    class Meta:
        unknown = EXCLUDE

    task = fields.Str(
        required=True,
        validate=validate.Length(min=1, max=200, error="Task must be between 1 and 200 characters")
    )
    description = fields.Str(
        required=True,
        validate=validate.Length(min=1, max=500, error="Description must be between 1 and 500 characters")
    )

class ToDoQuerySchema(ma.Schema):
    class Meta:
        unknown = EXCLUDE

    date = fields.Str(
        required=False,
        validate=validate.Regexp(r'^\d{4}-\d{2}-\d{2}$', error="Date must be in YYYY-MM-DD format")
    )

class ToDoResponseSchema(ma.Schema):
    uid = fields.Str()
    task = fields.Str()
    description = fields.Str()
    created_at = fields.DateTime()
    modified_at = fields.DateTime()
    status = fields.Str()
    user_uid = fields.Str()

class ToDoUpdateSchema(ma.Schema):
    class Meta:
        unknown = EXCLUDE

    task = fields.Str(
        required=False,
        validate=validate.Length(min=1, max=200, error="Task must be between 1 and 200 characters")
    )
    description = fields.Str(
        required=False,
        validate=validate.Length(min=1, max=500, error="Description must be between 1 and 500 characters")
    )
    status = fields.Str(
        required=False,
        validate=validate.OneOf(["in progress", "completed"], error="Status must be 'in progress' or 'completed'")
    )

    @validates_schema
    def validate_at_least_one(self, data, **kwargs):
        if not data:
            raise ValidationError("At least one field (task, description, or status) must be provided.")
