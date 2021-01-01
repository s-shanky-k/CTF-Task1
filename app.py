from flask import Flask, request, jsonify, make_response, render_template
from flask_restful import reqparse, abort
from flask_sqlalchemy import  SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
import jwt
import datetime
from functools import wraps
from sqlalchemy.sql import func
from sqlalchemy.types import DateTime, Integer


app = Flask(__name__)
app.config['SECRET_KEY'] = 'boomboom'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///records.db'


db = SQLAlchemy(app)

#DB MODELS
class User(db.Model):
    id = db.Column(db.Integer,primary_key = True)
    username = db.Column(db.String(50),unique=True)
    password = db.Column(db.String(50))


class Record(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50))
    createdAt = db.Column(DateTime(timezone=True), server_default=func.now())


record_search_args = reqparse.RequestParser()
record_search_args.add_argument("id",type=int,help="ID of record",required=False)
record_search_args.add_argument("name",type=str,help="Name of record",required=False)


def token_required(f):
    @wraps(f)
    def decorator(*args,**kwargs):
        token = request.headers['x-api-key']
        if not token:
            return jsonify({"message":"token is missing"}),401

        try:
            data = jwt.decode(token,app.config['SECRET_KEY'])
            #current_user = User.query.filter_by(username=data['username']).first()
        except:
            return jsonify({"message":"token is invalid"}),401
        
        return f(*args, **kwargs)
    return decorator


def getRecordById(record_id):
    record = Record.query.filter_by(id = record_id).first()
    if not record:
        return jsonify({"message":"No such record exits"})
    
    record_dict = {}
    record_dict['name'] = record.name
    record_dict['createdAt'] = record.createdAt

    return jsonify(record_dict)

def getRecordByName(name):
    records = Record.query.filter_by(name = name).all()

    if len(records) == 0:
        return jsonify({"message":"No such record exits"})
    
    output = []

    for record in records:
        record_dict = {}
        record_dict['name'] = record.name
        record_dict['createdAt'] = record.createdAt
        output.append(record_dict)

    return jsonify({"records":output})


@app.route('/')
def index():
    return render_template('index.html')


#Route to fetch all users
@app.route('/users',methods=['GET'])
@token_required
def get_all_user():
    users = User.query.all()
    output = []

    for user in users:
        user_data = {}
        user_data['username'] = user.username
        user_data['password'] = user.password
        output.append(user_data)

    return jsonify({"users":output})


#Route to signup
@app.route('/signup',methods=['POST'])
def create_user():
    data = request.get_json()

    user = User.query.filter_by(username = data['username']).first()

    if not user:
        hashed_password = generate_password_hash(data['password'],method='sha256')
        new_user = User(username = data['username'], password = hashed_password)
        db.session.add(new_user)
        db.session.commit()
        return jsonify({'message':"New User Created"})
    
    return jsonify({'message':"Username already exists"})


#Route for login
@app.route('/login')
def login():
    auth = request.authorization

    if not auth or not auth.password or not auth.username:
        return make_response('Could not verify',401, {'WWW-Authenticate':'Basic realm="Login Required!!"'})
    
    user = User.query.filter_by(username=auth.username).first()

    if not user:
        return make_response('Could not verify',401, {'WWW-Authenticate':'Basic realm="Login Required!!"'})

    if check_password_hash(user.password,auth.password):
        token = jwt.encode({'username':user.username,'exp':datetime.datetime.utcnow() + datetime.timedelta(minutes=30)},app.config['SECRET_KEY'])
        return jsonify({'token': token.decode('UTF-8')})

    return make_response('Could not verify',401, {'WWW-Authenticate':'Basic realm="Login Required!!"'})


#To list all records
@app.route('/record',methods=['GET'])
@token_required
def get_all_records():

    records = Record.query.filter_by().all()

    output = []

    for record in records:
        record_dict = {}
        record_dict['name'] = record.name
        record_dict['createdAt'] = record.createdAt
        output.append(record_dict)

    return jsonify({"records":output})


#To find a record based on Primary Key (record_id)
@app.route('/record/<record_id>',methods=['GET'])
@token_required
def get_one_records(record_id):

    record = Record.query.filter_by(id = record_id).first()

    if not record:
        return jsonify({"message":"No such record exits"})
    
    record_dict = {}
    record_dict['name'] = record.name
    record_dict['createdAt'] = record.createdAt

    return jsonify(record_dict)


#Route to Search either based on id or name
@app.route('/search',methods=['GET'])
@token_required
def search():
    args = record_search_args.parse_args()
    id = args["id"]
    name = args["name"]
    if(id is None and name is None and createdAt is None):
        abort(404, message="Invalid Arguments")
    elif(not(id is None)):
        return getRecordById(id)
    else:
        return getRecordByName(name)


#To add a record
@app.route('/record',methods=['POST'])
@token_required
def create_record():
    data = request.get_json()

    new_record = Record(name = data['name'])
    db.session.add(new_record)
    db.session.commit()

    return jsonify({"message":"New record created"})


#To Update a record
@app.route('/record/<record_id>',methods=['PATCH'])
@token_required
def complete_record(record_id):
    data = request.get_json()

    record = Record.query.filter_by(id = record_id).first()

    if not record:
        return jsonify({"message":"No such record exits"})

    record.name = data["new_name"]
    db.session.commit()
    return jsonify({"message":"Record updated"})


#To delete a record
@app.route('/record/<record_id>',methods=['DELETE'])
@token_required
def delete_record(record_id):
    record = Record.query.filter_by(id = record_id).first()

    if not record:
        return jsonify({"message":"No such record exits"})

    db.session.delete(record)
    db.session.commit()
    return jsonify({"message":"Record Deleted"})


if __name__ == "__main__":
    app.run(debug = True)