from flask import request, jsonify
from playstorescrapperapp import app, db
from datetime import date
from playstorescrapperapp.models import User, App, Category, CategoryMapping
from functools import wraps
import play_scraper
import json
import jwt
import datetime



@app.route("/")
def home():
    return "Howdy ! Nothing here. Go <a href='http://google.com'>here</a>"



def token_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        token = None

        if 'Authorization' in request.headers:
            auth = request.headers['Authorization']
            tok = auth.split(" ")
            token = tok[1]

        if not token:
            return jsonify({"message" : "Token is missing"}), 403

        try:
            data = jwt.decode(token, app.config['SECRET_KEY'])
            username = data['user']
            user = User.query.filter_by(username = username).first()
            if user == None:
                return jsonify({"message" : "Invalid Token"}), 403
        except:
            return jsonify({"message" : "Invalid Token"}), 403
        return f(*args, **kwargs)
    return decorated



@app.route("/login", methods=['POST'])
def login():
    try:
        reqdata_dict = request.get_json()
        user_object = User.query.filter_by(username = reqdata_dict['username'], password = reqdata_dict['password']).first()
    except:
        return jsonify({"message" : "Invalid Request Format"}), 403
    else:
        if user_object == None:
            return jsonify({"message" : "Invalid User Name Or Password"}), 403
        else:
            token = jwt.encode({'user':user_object.username, 'exp':datetime.datetime.utcnow()+datetime.timedelta(hours = app.config['JWT_TOKEN_EXPIRY_HOURS'])}, app.config['SECRET_KEY'])
            debug(token.decode('UTF-8'))
            return jsonify({"token" : token.decode('UTF-8')})



@app.route("/refresh_token")
@token_required
def refresh_token():
    auth = request.headers['Authorization']
    tok = auth.split(" ")
    token = tok[1]
    data = jwt.decode(token, app.config['SECRET_KEY'])
    username = data['user']
    token = jwt.encode({'user':username, 'exp':datetime.datetime.utcnow()+datetime.timedelta(hours = app.config['JWT_TOKEN_EXPIRY_HOURS'])}, app.config['SECRET_KEY'])
    debug("newtoken: "+ token.decode('UTF-8'))
    return jsonify({"new_token" : token.decode('UTF-8')})



@app.route("/get_app/<appstore_id>/")
@token_required
def getapp(appstore_id):
    refresh_days = app.config['SCRAPPER_REFRESH_DAYS']
    today = date.today()
    invalid_message = {
        "message" : "Invalid"
    }

    app_object = App.query.filter_by(appstoreid = appstore_id).first()
    if app_object == None:
        debug("does not exist in database, have to create new record")
        debug("hitting playscrapper")
        app_object = App()
        try:
            playstore_dict = play_scraper.details(appstore_id)
        except:
            debug("not valid appstore id, returning invalid message")
            app_object.appstoreid = appstore_id
            app_object.valid=False
            app_object.json=""
            app_object.lastChecked = today
            db.session.add(app_object)
            db.session.commit()
            return jsonify(invalid_message)
        else:
            debug("valid, creating new record in database, returning json")
            app_object.appstoreid = appstore_id
            app_object.valid=True
            app_object.json=json.dumps(playstore_dict)
            app_object.lastChecked = today
            db.session.add(app_object)
            db.session.commit()  
            response = app.response_class(
                response=app_object.json,
                status=200,
                mimetype='application/json'
            )
            refresh_category_mappings(app_object.id)
            return response
    else:
        debug("exists in database")
        if app_object.valid==True:
            debug("valid object")
            delta = today - app_object.lastChecked
            delta_days = delta.days
            debug("checked "+str(delta_days)+" days ago")
            if delta_days < refresh_days:
                debug("checked recently, returning from database")
                response = app.response_class(
                    response=app_object.json,
                    status=200,
                    mimetype='application/json'
                )
                return response
            else:
                debug("hitting playscrapper and refreshing data in database")
                try:
                    playstore_dict = play_scraper.details(appstore_id)
                except:
                    debug("not valid anymore, returning invalid message")
                    app_object.valid=False
                    app_object.json=""
                    app_object.lastChecked = today
                    db.session.commit()
                    refresh_category_mappings(app_object.id)
                    return jsonify(invalid_message)
                else:
                    debug("valid data, refreshing data in database, returning json")
                    app_object.valid=True
                    app_object.json=json.dumps(playstore_dict)
                    app_object.lastChecked = today
                    db.session.commit()
                    response = app.response_class(
                        response=app_object.json,
                        status=200,
                        mimetype='application/json'
                    )
                    refresh_category_mappings(app_object.id)
                    return response
        else:
            debug("invalid object")
            delta = today - app_object.lastChecked
            delta_days = delta.days
            debug("checked "+str(delta_days)+" days ago")
            if delta_days < refresh_days:
                debug("checked recently, returning from database")
                return jsonify(invalid_message)
            else:
                debug("hitting playscrapper and refreshing data in database")
                try:
                    playstore_dict = play_scraper.details(appstore_id)
                except:
                    debug("not valid, returning invalid message")
                    app_object.valid=False
                    app_object.json=""
                    app_object.lastChecked = today
                    db.session.commit()
                    refresh_category_mappings(app_object.id)
                    return jsonify(invalid_message)
                else:
                    debug("valid, refreshing data in database")
                    app_object.valid=True
                    app_object.json=json.dumps(playstore_dict)
                    app_object.lastChecked = today
                    db.session.commit()
                    response = app.response_class(
                        response=app_object.json,
                        status=200,
                        mimetype='application/json'
                    )
                    refresh_category_mappings(app_object.id)
                    return response



@app.route("/categories")
@token_required
def categories():
    categories = Category.query.all()
    cat_list = []
    for c in categories:
        cat_list.append({"categoryId":c.id, "categoryName": c.categoryName})
    return jsonify(cat_list)



@app.route("/get_apps_by_category/<category_id>/")
@token_required
def get_apps_by_category(category_id):
    maps = CategoryMapping.query.filter_by(categoryId = category_id).all()
    list = []
    for m in maps:
        app_id = m.appId
        app_object = App.query.filter_by(id=app_id).first()
        mydict = json.loads(app_object.json)
        list.append(mydict)
    return jsonify(list)



def refresh_category_mappings(app_id):
    debug("updating category mappings for AppID "+str(app_id))
    CategoryMapping.query.filter_by(appId= app_id).delete()
    db.session.commit()
    app_object = App.query.filter_by(id = app_id).first()
    if app_object.valid == False:
        return
    json_dict = json.loads(app_object.json)
    categories = json_dict['category']
    for cat in categories:
        c = Category.query.filter_by(categoryName = cat).first()
        if c == None:
            continue
        else:
            c1 = CategoryMapping(appId = app_object.id, categoryId= c.id)
            db.session.add(c1)
    db.session.commit()



def debug(message):
    if app.debug:
        print("\033[92m DEBUG: {}\033[00m" .format(message))