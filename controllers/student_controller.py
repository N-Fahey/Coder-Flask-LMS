from flask import Blueprint, jsonify, request
from sqlalchemy.exc import IntegrityError
from psycopg2 import errorcodes

from init import db
from models import Student
from views import student_schema, students_schema

students_bp = Blueprint('students', __name__, url_prefix='/students')

# Get All Students
@students_bp.route('/')
def get_students():
    stmt = db.select(Student)
    students_list = db.session.scalars(stmt)

    data = students_schema.dump(students_list)

    if not data:
        return {'message': "No student records found."}, 404

    return jsonify(data)

# Get Single Student
@students_bp.route('/<int:student_id>')
def get_a_student(student_id:int):
    stmt = db.select(Student).where(Student.id == student_id)
    student = db.session.scalar(stmt)

    if not student:
        return {'message': "No student record found."}, 404

    data = student_schema.dump(student)
    return jsonify(data)

#Create Single Student
@students_bp.route('/', methods=['POST'])
def create_a_student():
    try:
        data = request.get_json()
        new_student = Student(
            name = data.get('name'),
            email = data.get('email'),
            address = data.get('address')
        )
        
        db.session.add(new_student)
        db.session.commit()

        return_dict = {
            'message': "New student created.",
            'student': student_schema.dump(new_student)
        }
        return jsonify(return_dict), 201
    
    except IntegrityError as e:
        match e.orig.pgcode:
            case errorcodes.NOT_NULL_VIOLATION:
                return jsonify({'message': f"Required field: '{e.orig.diag.column_name}' cannot be null."}), 400
            case errorcodes.UNIQUE_VIOLATION:
                return jsonify({'message': f"{e.orig.diag.message_detail}"}), 409
            case _:
                return jsonify({'message': f"An unexpected database error occured."}), 400
    
    except:
        return jsonify({'message': "An unexpected error occured"}), 500

# Update Single Student
@students_bp.route('/<int:student_id>', methods=['PUT', 'PATCH'])
def update_a_student(student_id:int):
    try:
        stmt = db.select(Student).where(Student.id == student_id)
        student = db.session.scalar(stmt)
        if not student:
            return {'message': f"Student with ID {student_id} doesn't exist."}, 400

        data = request.get_json()

        student.name = data.get('name', student.name)
        student.email = data.get('email', student.email)
        student.address = data.get('address', student.address)

        db.session.commit()

        return_dict = {
                'message': f"Student {student.name} updated.",
                'student': student_schema.dump(student)
            }
        
        return return_dict
    except IntegrityError as e:
        match e.orig.pgcode:
            case errorcodes.UNIQUE_VIOLATION:
                return jsonify({'message': f"{e.orig.diag.message_detail}", 'input':data}), 409
            case _:
                return jsonify({'message': f"An unexpected data error occured."}), 400
    except:
        return jsonify({'message': "An unexpected error occured"}), 500


# Delete Single Student
@students_bp.route('/<int:student_id>', methods=['DELETE'])
def delete_a_student(student_id:int):
    stmt = db.select(Student).where(Student.id == student_id)
    existing_student = db.session.scalar(stmt)
    if not existing_student:
        return {'message': f"Student with ID {student_id} doesn't exist."}, 400

    db.session.delete(existing_student)
    db.session.commit()

    return jsonify({'message': f"Student {existing_student.name} deleted."})