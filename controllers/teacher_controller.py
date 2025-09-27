from flask import Blueprint, jsonify, request
from sqlalchemy.exc import IntegrityError
from psycopg2 import errorcodes

from init import db
from models import Teacher
from views import teacher_schema, teachers_schema

teachers_bp = Blueprint('teachers', __name__, url_prefix='/teachers')

# Get All Teachers
@teachers_bp.route('/')
def get_teachers():
    department = request.args.get('department')

    stmt = db.select(Teacher)
    if department:
        stmt = stmt.where(Teacher.department == department)

    teachers = db.session.scalars(stmt)

    data = teachers_schema.dump(teachers)

    if not data:
        return {'message': "No teacher records found."}, 404

    return jsonify(data)

# Get Single Teacher
@teachers_bp.route('/<int:teacher_id>')
def get_a_teacher(teacher_id:int):
    stmt = db.select(Teacher).where(Teacher.id == teacher_id)
    teacher = db.session.scalar(stmt)

    if not teacher:
        return {'message': "No teacher record found."}, 404

    data = teacher_schema.dump(teacher)
    return jsonify(data)

# Create Single Teacher
@teachers_bp.route('/', methods=['POST'])
def create_a_teacher():
    try:
        data = request.get_json()
        new_teacher = Teacher(
            name = data.get('name'),
            department = data.get('department'),
            address = data.get('address')
        )
        
        db.session.add(new_teacher)
        db.session.commit()

        return_dict = {
            'message': "New teacher created.",
            'teacher': teacher_schema.dump(new_teacher)
        }
        return jsonify(return_dict), 201
    
    except IntegrityError as e:
        match e.orig.pgcode:
            case errorcodes.NOT_NULL_VIOLATION:
                return jsonify({'message': f"Required field: '{e.orig.diag.column_name}' cannot be null."}), 400
            case _:
                return jsonify({'message': f"An unexpected database error occured."}), 400
    
    except:
        return jsonify({'message': "An unexpected error occured"}), 500

# Update Single Teacher
@teachers_bp.route('/<int:teacher_id>', methods=['PUT', 'PATCH'])
def update_a_teacher(teacher_id:int):
    try:
        stmt = db.select(Teacher).where(Teacher.id == teacher_id)
        teacher = db.session.scalar(stmt)
        if not teacher:
            return {'message': f"Teacher with ID {teacher_id} doesn't exist."}, 400

        data = request.get_json()

        teacher.name = data.get('name', teacher.name)
        teacher.department = data.get('department', teacher.department)
        teacher.address = data.get('address', teacher.address)

        db.session.commit()

        return_dict = {
                'message': f"Teacher {teacher.name} updated.",
                'teacher': teacher_schema.dump(teacher)
            }
        
        return return_dict
    
    except IntegrityError as e:
        match e.orig.pgcode:
            case _:
                return jsonify({'message': f"An unexpected data error occured."}), 400
    except:
        return jsonify({'message': "An unexpected error occured"}), 500
    
# Delete Single Teacher
@teachers_bp.route('/<int:teacher_id>', methods=['DELETE'])
def delete_a_teacher(teacher_id:int):
    stmt = db.select(Teacher).where(Teacher.id == teacher_id)
    existing_teacher = db.session.scalar(stmt)
    if not existing_teacher:
        return {'message': f"Teacher with ID {teacher_id} doesn't exist."}, 400

    db.session.delete(existing_teacher)
    db.session.commit()

    return jsonify({'message': f"Teacher {existing_teacher.name} deleted."})