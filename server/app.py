#!/usr/bin/env python3

from models import db, Activity, Camper, Signup
from flask_restful import Api, Resource
from flask_migrate import Migrate
from flask import Flask, make_response, jsonify, request
import os

BASE_DIR = os.path.abspath(os.path.dirname(__file__))
DATABASE = os.environ.get(
    "DB_URI", f"sqlite:///{os.path.join(BASE_DIR, 'app.db')}")


app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = DATABASE
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.json.compact = False

migrate = Migrate(app, db)

db.init_app(app)

api = Api(app)

@app.route('/')
def home():
    return ''

class Campers(Resource):
    def get(self):
        records_dict = [record.to_dict(rules=('-signups',)) for record in Camper.query.all()]
        return make_response(records_dict, 200)
    
    def post(self):
        request_dict = request.get_json()
        try:
            camper = Camper(
                name = request_dict.get('name'),
                age = request_dict.get('age')
            )
            db.session.add(camper)
            db.session.commit()
        except Exception as exc:
            return make_response(
                {'errors': ["validation errors"]},
                400
            )
        return make_response(camper.to_dict(rules=('-signups',)), 201)

class CamperByID(Resource):
    def get(self, id):
        record = Camper.query.filter_by(id=id).first()
        if record:
            return make_response(record.to_dict(), 200)
        return make_response(
            {'error': 'Camper not found'},
            404
        )
    
    def patch(self, id):
        record = Camper.query.filter_by(id=id).first()
        if record:
            request_dict = request.get_json()
            try:
                for key in request_dict:
                    setattr(record, key, request_dict[key])
                db.session.add(record)
                db.session.commit()
            except Exception as exc:
                return make_response(
                    {'errors': ["validation errors"]},
                    400
                )
            return make_response(record.to_dict(rules=('-signups',)), 202)
        return make_response(
            {'error': 'Camper not found'},
            404
        )

class Activities(Resource):
    def get(self):
        records_dict = [record.to_dict(rules=('-signups',)) for record in Activity.query.all()]
        return make_response(records_dict, 200)
    
class ActivityByID(Resource):
    def delete(self, id):
        record = Activity.query.filter_by(id=id).first()
        if record:
            db.session.delete(record)
            db.session.commit()
            return make_response({}, 204)
        return make_response(
            {'error': 'Activity not found'},
            404
        )
    
class Signups(Resource):
    def post(self):
        request_dict = request.get_json()
        try:
            signup = Signup(
                time = request_dict.get('time'),
                activity_id = request_dict.get('activity_id'),
                camper_id = request_dict.get('camper_id')
            )
            db.session.add(signup)
            db.session.commit()
        except Exception as exc:
            return make_response(
                {'errors': ["validation errors"]},
                400
            )
        return make_response(signup.to_dict(), 201)

api.add_resource(Campers, '/campers')
api.add_resource(CamperByID, '/campers/<int:id>')
api.add_resource(Activities, '/activities')
api.add_resource(ActivityByID, '/activities/<int:id>')
api.add_resource(Signups, '/signups')

if __name__ == '__main__':
    app.run(port=5555, debug=True)
