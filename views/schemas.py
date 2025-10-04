from marshmallow_sqlalchemy import SQLAlchemyAutoSchema, auto_field
from marshmallow import fields, validate, validates, ValidationError

from models import Student, Teacher, Course, Enrolment

class StudentSchema(SQLAlchemyAutoSchema):
    class Meta:
        model = Student
        load_instance = True
        fields = (
            'id',
            'name',
            'email',
            'address',
            'enrolments'
        )

    enrolments = fields.List(fields.Nested('EnrolmentSchema', exclude=['student']))

class TeacherSchema(SQLAlchemyAutoSchema):
    class Meta:
        model = Teacher
        load_instance = True
        fields = (
            'id',
            'name',
            'department',
            'address',
            'courses'
        )
    
    department = auto_field(validate=validate.And(
        validate.OneOf([
            'IT',
            'Science',
            'Business',
            'Language'
        ], error='Invalid department supplied')
    ))

    courses = fields.List(fields.Nested('CourseSchema', dump_only=True, exclude=['teacher', 'teacher_id']))

class CourseSchema(SQLAlchemyAutoSchema):
    class Meta:
        model = Course
        load_instance = True
        include_fk = True
        fields = (
            'id',
            'name',
            'duration',
            'teacher_id',
            'teacher',
            'enrolments'
        )
        load_only = (
            'teacher_id',
        )
    
    name = auto_field(validate=validate.And(
        validate.Length(min=3, max=50, error='Course must be between 3 & 50 characters.'),
        validate.Regexp(regex=r"^[A-Z][A-Za-z0-9 ]*$", error='Name must start with a capital letter & contain only: [A-Z][a-z][0-9][space]')
    ))

    @validates('duration')
    def validate_duration(self, duration, data_key):
        min_range = 1
        max_range = 6
        if duration < min_range or duration > max_range:
            raise ValidationError(f'Duration must be between {min_range} - {max_range}')

    teacher = fields.Nested('TeacherSchema', dump_only=True, exclude=['courses'])
    enrolments = fields.List(fields.Nested('EnrolmentSchema', dump_only=True, only=['id', 'enrolment_date', 'student']))

class EnrolmentSchema(SQLAlchemyAutoSchema):
    class Meta:
        model = Enrolment
        load_instance = True
        include_fk = True
        fields = (
            'id',
            'enrolment_date',
            'student',
            'course'
        )
    
    student = fields.Nested('StudentSchema', dump_only=True, only=['id', 'name', 'email', 'address'])
    course = fields.Nested('CourseSchema', dump_only=True, only=['id', 'name', 'duration', 'teacher'])


student_schema = StudentSchema()
students_schema = StudentSchema(many=True)

teacher_schema = TeacherSchema()
teachers_schema = TeacherSchema(many=True)

course_schema = CourseSchema()
courses_schema = CourseSchema(many=True)

enrolment_schema = EnrolmentSchema()
enrolments_schema = EnrolmentSchema(many=True)
