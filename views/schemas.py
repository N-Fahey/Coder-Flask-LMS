from marshmallow_sqlalchemy import SQLAlchemyAutoSchema
from marshmallow import fields

from models import Student, Teacher, Course

class StudentSchema(SQLAlchemyAutoSchema):
    class Meta:
        model = Student
        load_instance = True

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
            'teacher'
        )
    teacher = fields.Nested('TeacherSchema', dump_only=True, exclude=['id', 'courses'])

student_schema = StudentSchema()
students_schema = StudentSchema(many=True)

teacher_schema = TeacherSchema()
teachers_schema = TeacherSchema(many=True)

course_schema = CourseSchema()
courses_schema = CourseSchema(many=True)




