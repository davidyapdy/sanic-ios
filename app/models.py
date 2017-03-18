from sqlalchemy import Column, String, Integer, Boolean, DateTime, ForeignKey, JSON
from sqlalchemy.ext.declarative import declarative_base
import random
import string

Base = declarative_base()

def id_generator(size=32, chars=(string.ascii_uppercase + string.ascii_lowercase
                                 + string.digits)):
    return ''.join(random.choice(chars) for x in range(size))


class Person(Base):
    id = Column(Integer, primary_key=True)
    fbid = Column(String, unique=True)
    name = Column(String(128))  # user's name on Facebook
    mobile = Column(String(16))  # consecutive digits, no dashes / parens
    apikey = Column(String(32), unique=True)
    university_id = Column(Integer, ForeignKey('university.id'))
    verified = Column(Boolean, default=False)

    def events():
        return Event.query.filter_by(or_(initiator=self.id, partner=self.id))

    def __init__(self, fbid, name, apikey, university_id):
        self.fbid = fbid
        self.name = name
        self.apikey = apikey
        self.university_id = university_id


class University(Base):
    id = Column(Integer, primary_key=True)
    name = Column(String, unique=True)
    users = relationship('Person', backref='university', lazy='dynamic')

    def __init__(self, name):
        self.name = name


class Event(Base):
    id = Column(Integer, primary_key=True)
    category = Column(String(32))
    init_id = Column(Integer, ForeignKey('person.id'))
    proposer_id = Column(Integer, ForeignKey('person.id'), nullable=True)
    partner_id = Column(Integer, ForeignKey('person.id'), nullable=True)
    university_id = Column(Integer, ForeignKey('university.id'))
    startdate = Column(DateTime)
    enddate = Column(DateTime)
    messagedate = Column(DateTime, nullable=True)

    def __init__(self, category, init_id, university_id, startdate, enddate):
        self.category = category
        self.init_id = init_id
        self.university_id = university_id
        self.startdate = startdate
        self.enddate = enddate