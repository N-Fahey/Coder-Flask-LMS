from flask import Blueprint, jsonify, request
from sqlalchemy.exc import IntegrityError, DataError
from marshmallow import ValidationError
from psycopg2 import errorcodes

from init import db
from models import Course
from views import course_schema, courses_schema

courses_bp = Blueprint('courses', __name__, url_prefix='/courses')

@courses_bp.route('/')
def get_courses():
    stmt = db.select(Course)

    courses_list = db.session.scalars(stmt)

    data = courses_schema.dump(courses_list)

    if not data:
        return {'message': "No courses found."}, 404
    
    return jsonify(data)

@courses_bp.route('/<int:course_id>')
def get_course(course_id:int):
    stmt = db.select(Course).where(Course.id == course_id)

    course = db.session.scalar(stmt)
    data = course_schema.dump(course)

    if not data:
        return {'message': f"No course with ID {course_id}"}, 404
    
    return jsonify(data)

@courses_bp.route('/', methods=['POST'])
def create_course():
    try:
        data = request.get_json()

        new_course = Course(name=data.get('name'), duration=data.get('duration'), teacher_id=data.get('teacher_id'))

        db.session.add(new_course)
        db.session.commit()

        return jsonify(course_schema.dump(new_course)), 201
    except IntegrityError as e:
        match e.orig.pgcode:
            case errorcodes.NOT_NULL_VIOLATION:
                return jsonify({'message': f"Required field: '{e.orig.diag.column_name}' cannot be null."}), 400
            case errorcodes.UNIQUE_VIOLATION:
                return jsonify({'message': f"{e.orig.diag.message_detail}", 'input':data}), 409
            case errorcodes.FOREIGN_KEY_VIOLATION:
                return jsonify({'message': f"Invalid teacher selected.", 'input':data}), 409
            case _:
                return jsonify({'message': f"An unexpected data error occured."}), 400
    except:
        return jsonify({'message': "An unexpected error occured"}), 500

@courses_bp.route('/<int:course_id>', methods=['DELETE'])
def delete_course(course_id:int):
    stmt = db.select(Course).where(Course.id == course_id)
    course = db.session.scalar(stmt)

    data = course_schema.dump(course)

    if not data:
        return {'message': f"No course with ID {course_id}"}, 404

    db.session.delete(course)
    db.session.commit()

    return jsonify({'message': f"Course '{data['name']}' deleted."})

@courses_bp.route('/<int:course_id>', methods=['PUT', 'PATCH'])
def update_course(course_id:int):
    course = db.session.get(Course, course_id)

    if not course:
        return {'message': f"No course with ID {course_id}"}, 404
    
    input_data = course_schema.dump(course)

    try:
        body = request.get_json()
        course = course_schema.load(body, instance=course, session=db.session, partial=True)
        db.session.commit()

        return jsonify(course_schema.dump(course))
    
    except ValidationError as e:
        return jsonify({'message': f'Invalid input.',
                        
                        'errors': e.normalized_messages()}), 400
    except IntegrityError as e:
        match e.orig.pgcode:
            case errorcodes.NOT_NULL_VIOLATION:
                return jsonify({'message': f"Required field: '{e.orig.diag.column_name}' cannot be null."}), 400
            case errorcodes.UNIQUE_VIOLATION:
                return jsonify({'message': f"{e.orig.diag.message_detail}", 'input':input_data}), 409
            case errorcodes.FOREIGN_KEY_VIOLATION:
                return jsonify({'message': f"Invalid teacher selected.", 'input':input_data}), 409
            case _:
                return jsonify({'message': f"An unexpected IntegrityError occured: {e.detail}"}), 400
    except DataError as e:
        return jsonify({'message': f"An unexpected data error occured: {e}"}), 400
    except Exception as e:
        return jsonify({'message': f"An unexpected error occured: {e}"}), 500
        