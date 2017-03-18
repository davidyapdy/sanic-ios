from ..person import person
from app.models import *


# returns empty string if there is a db error, or api is wrong
@person.route('/new', methods=['POST'])
def create_user():
    data = request.json
    checkapi = data["apikey"]
    if not checkapi == universal:
        data = {
            "error": "could not authenticate API key"
        }
        resp = jsonify(data)
        resp.status_code = 500
        return resp
    fbid = data["fbid"]
    uni = University.query.filter_by(name=data["university"]).first()
    if uni is None:
        data = {
            "error": "could not find University"
        }
        resp = jsonify(data)
        resp.status_code = 500
        return resp
    apikey = id_generator()
    user = Person(fbid, data["name"], apikey, uni.id)
    db.session.add(user)
    try:
        db.session.commit()
        data = {
            "apikey": apikey,
            "error": ""
        }
        resp = jsonify(data)
        resp.status_code = 200
        return resp
    except:
        data = {
            "error": "could not create user"
        }
        resp = jsonify(data)
        resp.status_code = 500
        return resp


# grabs user based on API key
@person.route('/<apikey>', methods=['GET'])
def get_user(apikey):
    # data = request.json
    # apikey = data["apikey"]
    user = Person.query.filter_by(apikey=apikey).first()
    if user is None:
        data = {
            "error": "could not find user"
        }
        resp = jsonify(data)
        resp.status_code = 500
        return resp
    jsondict = {}
    jsondict["id"] = str(user.id)
    jsondict["fbid"] = user.fbid
    jsondict["name"] = user.name
    jsondict["mobile"] = user.mobile
    jsondict["university_id"] = str(user.university_id)
    jsondict["verified"] = str(user.verified)
    resp = jsonify(jsondict)
    resp.status_code = 200
    return resp


# updates a user's phone number
@person.route('/mobile', methods=['POST'])
def update_mobile():
    data = request.json
    apikey = data["apikey"]
    num = data["mobile"]
    user = Person.query.filter_by(apikey=apikey).first()
    if user is None:
        data = {
            "error": "could not find user"
        }
        resp = jsonify(data)
        resp.status_code = 500
        return resp
    user.mobile = num
    db.session.add(user)
    try:
        db.session.commit()
        data = {
            "error": ""
        }
        resp = jsonify(data)
        resp.status_code = 200
        client = TwilioRestClient(account_sid, auth_token)
        message = client.sms.messages.create(body="Welcome to Merge! Please text back 'Yes' to confirm", to=num,
                                             from_="+15616669720")
        return resp
    except:
        data = {
            "error": "could not update mobile"
        }
        resp = jsonify(data)
        resp.status_code = 500
        return resp


# used for twilio confirmation
@person.route('/twilio', methods=['POST'])
def receive_confirmation():
    print
    'here'
    from_number = request.values.get('From', None)
    print
    'here2'
    user = Person.query.filter_by(mobile=from_number).first()
    if user is None:
        data = {
            "error": "could not verify number"
        }
        resp = jsonify(data)
        resp.status_code = 500
        return resp
    body = request.values.get('Body', None)
    if not body == "Yes":
        data = {
            "error": "could not verify number"
        }
        resp = jsonify(data)
        resp.status_code = 500
        return resp
    user.verified = True
    db.session.add(user)
    try:
        db.session.commit()
        message = "Confirmed! We hope you enjoy our service!"
        resp = twilio.twiml.Response()
        resp.sms(message)
        return str(resp)
    except:
        data = {
            "error": "could not update number"
        }
        resp = jsonify(data)
        resp.status_code = 500
        return resp


@person.route('/verified/<apikey>', methods=['GET'])
def check_confirmation(apikey):
    # data = request.json
    # apikey = data["apikey"]
    user = Person.query.filter_by(apikey=apikey).first()
    if user is None:
        data = {
            "error": "could not authenticate user"
        }
        resp = jsonify(data)
        resp.status_code = 500
        return resp
    if user.verified == True:
        data = {
            "error": ""
        }
        resp = jsonify(data)
        resp.status_code = 500
        return resp
    data = {
        "error": "user is not verified"
    }
    resp = jsonify(data)
    resp.status_code = 500
    return resp