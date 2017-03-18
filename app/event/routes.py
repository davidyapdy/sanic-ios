from ..university import university
from app.models import *


##  returns empty string if you get a db error
# TODO: add app API authentication. DONE
@university.route('/new', methods=['POST'])
def create_uni():
    data = request.json
    checkapi = data["apikey"]
    if not checkapi == universal:
        data = {
            "error": "could not authenticate API key"
        }
        resp = jsonify(data)
        resp.status_code = 500
        return resp
    name = data["name"]
    uni = University(name)
    db.session.add(uni)
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
            "error": "could not create university"
        }
        resp = jsonify(data)
        resp.status_code = 500
        return resp


@university.route('/all/<apikey>', methods=['GET'])
def all_unis(apikey):
    # data = request.json
    checkapi = apikey
    if not checkapi == universal:
        data = {
            "error": "could not authenticate API key"
        }
        resp = jsonify(data)
        resp.status_code = 500
        return resp
    unis = University.query.all()
    jsondict = {}
    jsondict["unis"] = []
    for uni in unis:
        unijson = {}
        unijson["name"] = uni.name
        unijson["id"] = str(uni.id)
        jsondict["unis"].append(unijson);
    resp = jsonify(jsondict)
    resp.status_code = 200
    return resp


