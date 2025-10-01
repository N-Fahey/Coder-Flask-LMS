from flask import Blueprint, jsonify, request
from sqlalchemy.exc import IntegrityError, DataError
from psycopg2 import errorcodes

from init import db
from models import Enrolment
from views import enrolment_schema, enrolments_schema

enrolments_bp = Blueprint('enrolments', __name__, url_prefix='/enrolments')

@enrolments_bp.route('/')
def get_enrolments():
    enrolment_id = request.args.get('enrolment_id', type=int)
    student_id = request.args.get('student_id', type=int)

    stmt = db.select(Enrolment)

    if enrolment_id:
        stmt = stmt.where(Enrolment.enrolment_id == enrolment_id)
    if student_id:
        stmt = stmt.where(Enrolment.student_id == student_id)

    enrolments = db.session.scalars(stmt)

    data = enrolments_schema.dump(enrolments)

    if not data:
        return jsonify({'message': "No enrolments found."}), 404
    
    return jsonify(data)

@enrolments_bp.route('/', methods=['POST'])
def create_enrolment():
    try:
        data = request.get_json()

        new_enrolment = Enrolment(
            student_id=data.get('student_id'),
            enrolment_id=data.get('enrolment_id'),
            enrolment_date=data.get('enrolment_date')
            )

        db.session.add(new_enrolment)
        db.session.commit()

        return jsonify(enrolment_schema.dump(new_enrolment)), 201
    
    except IntegrityError as e:
        match e.orig.pgcode:
            case errorcodes.NOT_NULL_VIOLATION:
                return jsonify({'message': f"Required field: '{e.orig.diag.column_name}' cannot be null."}), 400
            case errorcodes.FOREIGN_KEY_VIOLATION:
                return jsonify({'message': f"{e.orig.diag.message_detail}", 'input':data}), 409
            case errorcodes.UNIQUE_VIOLATION:
                return jsonify({'message': f"Enrolment already exists", 'input':data}), 409
            case _:
                return jsonify({'message': f"An unexpected data error occured."}), 400
    except:
        return jsonify({'message': "An unexpected error occured"}), 500

@enrolments_bp.route('/<int:enrolment_id>', methods=['PUT', 'PATCH'])
def update_enrolment(enrolment_id:int):
    stmt = db.select(Enrolment).where(Enrolment.id == enrolment_id)
    enrolment = db.session.scalar(stmt)
    data = enrolment_schema.dump(enrolment)

    if not data:
        return {'message': f"No enrolment with ID {enrolment_id}"}, 404
    
    try:
        body = request.get_json()

        enrolment.student_id = body.get('student_id', enrolment.student_id)
        enrolment.course_id = body.get('course_id', enrolment.course_id)
        enrolment.enrolment_date = body.get('enrolment_date', enrolment.enrolment_date)

        db.session.commit()

        return jsonify(enrolment_schema.dump(enrolment))
    
    except IntegrityError as e:
        match e.orig.pgcode:
            case errorcodes.NOT_NULL_VIOLATION:
                return jsonify({'message': f"Required field: '{e.orig.diag.column_name}' cannot be null."}), 400
            case errorcodes.UNIQUE_VIOLATION:
                return jsonify({'message': f"{e.orig.diag.message_detail}", 'input':data}), 409
            case errorcodes.FOREIGN_KEY_VIOLATION:
                return jsonify({'message': f"Invalid teacher selected.", 'input':data}), 409
            case _:
                return jsonify({'message': f"An unexpected IntegrityError occured: {e.detail}"}), 400
    except DataError as e:
        return jsonify({'message': f"An unexpected data error occured: {e}"}), 400
    except Exception as e:
        return jsonify({'message': f"An unexpected error occured: {e}"}), 500

@enrolments_bp.route('/<int:enrolment_id>', methods=['DELETE'])
def delete_enrolment(enrolment_id:int):
    stmt = db.select(Enrolment).where(Enrolment.id == enrolment_id)
    enrolment = db.session.scalar(stmt)

    data = enrolment_schema.dump(enrolment)

    if not data:
        return {'message': f"No enrolment with ID {enrolment_id}"}, 404

    db.session.delete(enrolment)
    db.session.commit()

    return jsonify({'message': f"Enrolment '{enrolment_id}' deleted."})