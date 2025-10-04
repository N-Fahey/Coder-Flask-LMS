from flask import Flask, jsonify
from sqlalchemy.exc import IntegrityError, DataError
from marshmallow import ValidationError
from psycopg2 import errorcodes

def register_error_handlers(app:Flask):
    @app.errorhandler(ValidationError)
    def handle_validation_error(e:ValidationError):
        return jsonify(e.messages), 400
    
    @app.errorhandler(IntegrityError)
    def handle_integrity_error(e:IntegrityError):
        if not hasattr(e, 'orig') and not e.orig:
            return jsonify({'message': f"An unexpected IntegrityError error occured.", 'error': f'{e}'}), 400
        
        match e.orig.pgcode:
            case errorcodes.NOT_NULL_VIOLATION:
                return jsonify({'message': f"Required field: '{e.orig.diag.column_name}' cannot be null."}), 400
            case errorcodes.FOREIGN_KEY_VIOLATION:
                return jsonify({'message': f"{e.orig.diag.message_detail}"}), 409
            case errorcodes.UNIQUE_VIOLATION:
                return jsonify({'message': f"Enrolment already exists"}), 409
            case _:
                return jsonify({'message': f"An unexpected data error occured."}), 400
    
    @app.errorhandler(DataError)
    def handle_data_error(e:DataError):
        return jsonify({'message': f"An unexpected data error occured: {e}"}), 400
    
    @app.errorhandler(404)
    def handle_404_error(e:Exception):
        return {'message': f"Requested resource does not exist"}, 404
    
    @app.errorhandler(500)
    def handle_500_error(e:Exception):
        return {'message': f"A server error occured"}, 500