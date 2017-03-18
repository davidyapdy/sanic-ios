from ..event import event
from app.models import *
from datetime import datetime, timedelta
import time


# creates a new event for a given user
# TODO: fix start and end dates to cooperate
@event.route('/event/new', methods=['POST'])
def create_event():
    data = request.json
    apikey = data["apikey"]
    initiator = Person.query.filter_by(apikey=apikey).first()
    if initiator is None:
        data = {
            "error": "Could not authenticate user"
        }
        resp = jsonify(data)
        resp.status_code = 500
        return resp
    category = data["category"]
    start = datetime.fromtimestamp(int(data["startdate"]))
    end = datetime.fromtimestamp(int(data["enddate"]))
    event = Event(category, initiator.id, initiator.university_id, start, end)

    db.session.add(event)
    try:
        db.session.commit()
        data = {
            "error": ""
        }
        resp = jsonify(data)
        resp.status_code = 200
        return resp
    except:
        data = {
            "error": "could not create event"
        }
        resp = jsonify(data)
        resp.status_code = 500
        return resp


# the current user proposes to join an event
@event.route('/event/propose', methods=['POST'])
def propose_join():
    data = request.json
    apikey = data["apikey"]
    user = Person.query.filter_by(apikey=apikey).first()
    if user is None:
        data = {
            "error": "Could not authenticate user"
        }
        resp = jsonify(data)
        resp.status_code = 500
        return resp

    event = Event.query.filter_by(id=int(data["event_id"])).first()
    if event is None:
        data = {
            "error": "Could not find event"
        }
        resp = jsonify(data)
        resp.status_code = 500
        return resp

    event.proposer_id = user.id
    db.session.add(event)
    try:
        db.session.commit()
        data = {
            "error": ""
        }
        resp = jsonify(data)
        resp.status_code = 200
        return resp
    except:
        data = {
            "error": "could not add proposed user"
        }
        resp = jsonify(data)
        resp.status_code = 500
        return resp


# the current user joins an event
@event.route('/event/join', methods=['POST'])
def join_event():
    data = request.json
    apikey = data["apikey"]
    user = Person.query.filter_by(apikey=apikey).first()
    if user is None:
        data = {
            "error": "Could not authenticate user"
        }
        resp = jsonify(data)
        resp.status_code = 500
        return resp

    event = Event.query.filter_by(id=int(data["event_id"])).first()
    if event is None:
        data = {
            "error": "Could not find event"
        }
        resp = jsonify(data)
        resp.status_code = 500
        return resp

    event.partner_id = user.id
    event.proposer_id = None
    db.session.add(event)
    try:
        db.session.commit()
        data = {
            "error": ""
        }
        resp = jsonify(data)
        resp.status_code = 200
        return resp
    except:
        data = {
            "error": "could not join event"
        }
        resp = jsonify(data)
        resp.status_code = 500
        return resp


# grabs all events currently going on from the user's university in a given category
@event.route('/event/<apikey>/<category>', methods=['GET'])
def get_events(apikey, category):
    # data = request.args # data = request.json
    # apikey = data['apikey']
    user = Person.query.filter_by(apikey=apikey).first()
    if user is None:
        data = {
            "error": "Could not authenticate user"
        }
        resp = jsonify(data)
        resp.status_code = 500
        return resp
    # category = data["category"]
    events = Event.query.filter_by(university_id=user.university_id, category=category).filter(Event.partner_id == None,
                                                                                               Event.enddate > datetime.now())
    jsondict = {}
    jsondict["events"] = []
    for event in events:
        eventjson = {}
        eventjson["id"] = str(event.id)
        eventjson["category"] = event.category
        initiator = Person.query.filter_by(id=event.init_id).first()
        print
        "about to initialize"
        initjson = {}
        print
        "initialized"
        initjson["id"] = str(initiator.id)
        initjson["name"] = initiator.name
        initjson["fbid"] = initiator.fbid
        initjson["mobile"] = initiator.mobile
        initjson["university_id"] = str(initiator.university_id)
        initjson["verified"] = str(initiator.verified)
        eventjson["initiator"] = initjson
        eventjson["startdate"] = time.mktime(event.startdate.timetuple())
        eventjson["enddate"] = time.mktime(event.enddate.timetuple())
        if event.messagedate:
            eventjson["messagedate"] = time.mktime(event.messagedate.timetuple())
        jsondict["events"].append(eventjson);
    resp = jsonify(jsondict)
    resp.status_code = 200
    return resp


# our participant text messaged the event host
@event.route('/event/text', methods=['POST'])
def event_text():
    data = request.json
    apikey = data["apikey"]
    event = Event.query.filter_by(id=int(data["event_id"])).first()
    if event is None or event.proposer_id is None:
        data = {
            "error": "Could not find event"
        }
        resp = jsonify(data)
        resp.status_code = 500
        return resp

    user = Person.query.filter_by(apikey=apikey, id=int(event.proposer_id)).first()
    if user is None:
        data = {
            "error": "Could not authenticate user"
        }
        resp = jsonify(data)
        resp.status_code = 500
        return resp

    event.messagedate = datetime.now()
    db.session.add(event)
    try:
        db.session.commit()
        data = {
            "error": ""
        }
        resp = jsonify(data)
        resp.status_code = 200
        return resp
    except:
        data = {
            "error": "could not add message info"
        }
        resp = jsonify(data)
        resp.status_code = 500
        return resp


# return a hash of all events for which a user must be prompted on
@event.route('/event/prompt/<apikey>', methods=['GET'])
def prompt_on_event(apikey):
    # data = request.json
    # apikey = data["apikey"]
    user = Person.query.filter_by(apikey=apikey).first()
    if user is None:
        data = {
            "error": "Could not authenticate user"
        }
        resp = jsonify(data)
        resp.status_code = 500
        return resp
    events = Event.query.filter(Event.partner_id == user.id, Event.messagedate < datetime.now() - timedelta(
        minutes=5))  # remind if prompted > 5 minutes ago
    jsondict = {}
    jsondict["events"] = []
    for event in events:
        eventjson = {}
        eventjson["category"] = event.category
        initiator = Person.query.filter_by(id=event.init_id).first()
        eventjson["init"] = initiator.fbid
        partner = Person.query.filter_by(id=event.partner_id).first()
        if partner:
            eventjson["partner"] = partner.fbid
        eventjson["startdate"] = time.mktime(event.startdate.timetuple())
        eventjson["enddate"] = time.mktime(event.enddate.timetuple())
        if event.messagedate:
            eventjson["messagedate"] = time.mktime(event.messagedate.timetuple())
        jsondict["events"].append(eventjson);
    resp = jsonify(jsondict)
    resp.status_code = 200
    return resp


# get news feed
@event.route('/event/newsfeed/<apikey>', methods=['GET'])
def newsfeed():
    # data = request.json
    # apikey = data["apikey"]
    user = Person.query.filter_by(apikey=apikey).first()
    if user is None:
        data = {
            "error": "Could not authenticate user"
        }
        resp = jsonify(data)
        resp.status_code = 500
        return resp
    events = Event.query.filter_by(university_id=user.university_id).filter(Event.partner_id != None).order_by(
        Event.enddate.desc()).limit(10).all()
    jsondict = {}
    jsondict["events"] = []
    for event in events:
        eventjson = {}
        eventjson["category"] = event.category
        initiator = Person.query.filter_by(id=event.init_id).first()
        initjson = {}
        initjson["id"] = str(initiator.id)
        initjson["name"] = initiator.name
        initjson["fbid"] = initiator.fbid
        initjson["mobile"] = initiator.mobile
        initjson["university_id"] = str(initiator.university_id)
        initjson["verified"] = str(initiator.verified)
        eventjson["initiator"] = initjson
        partner = Person.query.filter_by(id=event.partner_id).first()
        if partner:
            partjson = {}
            partjson["id"] = str(partner.id)
            partjson["name"] = partner.name
            partjson["fbid"] = partner.fbid
            partjson["mobile"] = partner.mobile
            partjson["university_id"] = str(partner.university_id)
            partjson["verified"] = str(partner.verified)
            eventjson["partner"] = partJSON
        eventjson["startdate"] = time.mktime(event.startdate.timetuple())
        eventjson["enddate"] = time.mktime(event.enddate.timetuple())
        if event.messagedate:
            eventjson["messagedate"] = time.mktime(event.messagedate.timetuple())
        jsondict["events"].append(eventjson);
    resp = jsonify(jsondict)
    resp.status_code = 200
    return resp
