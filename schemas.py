from marshmallow import Schema, fields, validate, validates, ValidationError
from marshmallow_sqlalchemy import SQLAlchemyAutoSchema
from models import User, Task, Comment
from datetime import datetime

class UserSchema(Schema):
    username = fields.Str(required=True, validate=validate.Length(min=3, max=80))
    email = fields.Email(required=True)
    password = fields.Str(required=True, load_only=True, validate=validate.Length(min=6))

    @validates('password')
    def validate_password(self, password):
        if len(password) < 6:
            raise ValidationError("Password must be at least 6 characters long.")

class TaskSchema(SQLAlchemyAutoSchema):
    class Meta:
        model = Task
        load_instance = True

    title = fields.Str(required=True, validate=validate.Length(min=3, max=120))
    description = fields.Str(validate=validate.Length(max=500))
    due_date = fields.DateTime(required=True)
    priority = fields.Str(required=True, validate=validate.OneOf(["low", "medium", "high"]))

    @validates('due_date')
    def validate_due_date(self, due_date):
        if due_date < datetime.utcnow():
            raise ValidationError("Due date cannot be in the past.")

class CommentSchema(SQLAlchemyAutoSchema):
    class Meta:
        model = Comment
        load_instance = True

    content = fields.Str(required=True, validate=validate.Length(min=1, max=500))
    task_id = fields.Int(required=True)
    user_id = fields.Int(required=True)
