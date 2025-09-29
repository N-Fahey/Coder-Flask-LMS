from marshmallow_sqlalchemy import SQLAlchemyAutoSchema
from marshmallow import fields

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

    teacher = fields.Nested('TeacherSchema', dump_only=True, exclude=['id', 'courses'])
    enrolments = fields.List(fields.Nested('EnrolmentSchema', dump_only=True, only=['id', 'enrolment_date', 'student_id', 'student']))

class EnrolmentSchema(SQLAlchemyAutoSchema):
    class Meta:
        model = Enrolment
        load_instance = True
        include_fk = True
        fields = (
            'id',
            'enrolment_date',
            'student_id',
            'student',
            'course_id',
            'course'
        )
    
    student = fields.Nested('StudentSchema', dump_only=True, only=['name', 'email', 'address'])
    course = fields.Nested('CourseSchema', dump_only=True, only=['name', 'duration', 'teacher_id', 'teacher'])


student_schema = StudentSchema()
students_schema = StudentSchema(many=True)

teacher_schema = TeacherSchema()
teachers_schema = TeacherSchema(many=True)

course_schema = CourseSchema()
courses_schema = CourseSchema(many=True)

enrolment_schema = EnrolmentSchema()
enrolments_schema = EnrolmentSchema(many=True)
