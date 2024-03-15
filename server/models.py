from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import MetaData
from sqlalchemy.orm import validates
from sqlalchemy.ext.associationproxy import association_proxy
from sqlalchemy_serializer import SerializerMixin

convention = {
    "ix": "ix_%(column_0_label)s",
    "uq": "uq_%(table_name)s_%(column_0_name)s",
    "ck": "ck_%(table_name)s_%(constraint_name)s",
    "fk": "fk_%(table_name)s_%(column_0_name)s_%(referred_table_name)s",
    "pk": "pk_%(table_name)s"
}

metadata = MetaData(naming_convention=convention)

db = SQLAlchemy(metadata=metadata)


class Activity(db.Model, SerializerMixin):
    __tablename__ = 'activities'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String)
    difficulty = db.Column(db.Integer)

    # Add relationship
    signups = db.relationship('Signup', back_populates='activity', cascade='all, delete-orphan')
    campers = association_proxy('signups', 'camper', 
                                creator=lambda camper_obj: Signup(camper=camper_obj))
    
    # Add serialization rules
    serialize_rules = ('-signups.activity',)
    
    def __repr__(self):
        return f'<Activity {self.id}: {self.name}>'


class Camper(db.Model, SerializerMixin):
    __tablename__ = 'campers'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String, nullable=False)
    age = db.Column(db.Integer)

    # Add relationship
    signups = db.relationship('Signup', back_populates='camper', cascade='all, delete-orphan')
    activities = association_proxy('signups', 'activity', 
                                   creator=lambda activity_obj: Signup(activity=activity_obj))
    
    # Add serialization rules
    serialize_rules = ('-signups.camper',)
    
    # Add validation
    @validates('name', 'age')
    def validate(self, key, value):
        if key == 'name':
            if value is None or value == '':
                raise ValueError("Camper's name must be a none empty string.")
        elif key == 'age':
            if value < 8 or value > 18:
                raise ValueError("Camper's age must be in between 8 and 18.")
        return value
    
    def __repr__(self):
        return f'<Camper {self.id}: {self.name}>'


class Signup(db.Model, SerializerMixin):
    __tablename__ = 'signups'

    id = db.Column(db.Integer, primary_key=True)
    time = db.Column(db.Integer)

    # Add relationships
    activity_id = db.Column(db.Integer, db.ForeignKey('activities.id'))
    camper_id = db.Column(db.Integer, db.ForeignKey('campers.id'))

    activity = db.relationship('Activity', back_populates='signups')
    camper = db.relationship('Camper', back_populates='signups')
    
    # Add serialization rules
    serialize_rules = ('-activity.signups', '-camper.signups',)
    
    # Add validation
    @validates('time')
    def validate(self, key, value):
        if key == 'time':
            if value < 0 or value > 23:
                raise ValueError('Signup time must be in between 0 and 23.')
        return value
    
    def __repr__(self):
        return f'<Signup {self.id}>'


# add any models you may need.
