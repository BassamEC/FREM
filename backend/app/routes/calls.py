from flask import Blueprint, request, jsonify
from datetime import datetime
from app import db, socketio
from app.models import Call

calls_bp = Blueprint('calls', __name__)

# covert to dictionary
def call_to_dict(call):
    return {
        'id': call.id,
        'coordinates': call.coordinates,
        'place': call.place,
        'timestamp': call.timestamp.isoformat() if call.timestamp else None,
    }
    
@calls_bp.route('/', methods=['GET'])
def get_calls():
    calls = Call.query.all()
    return jsonify([call_to_dict(call) for call in calls]), 200

@calls_bp.route('/<int:call_id>', methods=['GET'])
def get_call(call_id):
    call = Call.query.get_or_404(call_id)
    return jsonify(call_to_dict(call)), 200

@calls_bp.route('/', methods=['POST'])
def create_call():
    data = request.get_json()
    coordinates = data.get('coordinates')
    place = data.get('place')

    if not coordinates:
        return jsonify({'error': 'coordinates is required'}), 400

    new_call = Call(
        coordinates=coordinates,
        place=place,
        timestamp=datetime.utcnow()
    )

    db.session.add(new_call)
    db.session.commit()

    socketio.emit("new_call", call_to_dict(new_call))
     
    return jsonify(call_to_dict(new_call)), 201

@calls_bp.route('/<int:call_id>', methods=['DELETE'])
def delete_call(call_id):
    call = Call.query.get_or_404(call_id)
    db.session.delete(call)
    db.session.commit()
    return jsonify({'message': 'Call deleted successfully'}), 200