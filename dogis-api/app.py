from flask import Flask, jsonify, abort, make_response, request
import json
import numpy as np
import shapefile
import pymongo
myclient = pymongo.MongoClient("mongodb://localhost:27017/")
mydb = myclient["mongo_1"]

 
app = Flask(__name__)

@app.route('/dogis/api/v1.0/getusers', methods=['POST'])
def upload_info():
    user_info = request.get_json()
    user_name = user_info['user']
    user_password = user_info['password']
    mycol = mydb["users"]
    mydoc = mycol.find(user_info)
    if mydoc.count()>0:
        return '1'
    else:
        que=mycol.find({'user':user_name})
        if que.count() ==1:
            return '-1'
        else :
            mycol.insert_one(user_info)
            return '0'

@app.route('/dogis/api/v1.0/uploadshp', methods=['GET'])
def uploadshp():
    # information = request.get_json()
    f = open("wuhancity2.json",'rb')
    text = f.read()
    dic = json.loads(text)
    # with open("wuhancity.json",'r') as load_f:
    #     new_dict = json.load(load_f,)
    return dic


@app.route('/dogis/api/v1.0/upload', methods=['POST'])
def upload():
    information = request.get_json()
    mycol = mydb["collection_1"]
    mycol.insert_one(information)
    return 'ok'

@app.route('/dogis/api/v1.0/delete', methods=['POST'])
def delete():
    id = request.get_json()
    myid = id['id']
    mycol = mydb["collection_1"]
    myquery = { "name": myid }
    mycol.delete_one(myquery)
    return 'ok'


@app.route('/dogis/api/v1.0/init', methods=['GET'])
def init():
    mycol = mydb["collection_1"]
    mydoc = mycol.find()
    arr=[]
    geojson={ "type": "FeatureCollection",
            "features": []}
    
    for i,x in enumerate(mydoc):
        geojson["features"].append({
            "type": "Feature",
            "properties":{
                "id":i,
                "name":x['name'],
                'genre':x['type']
            },
            "geometry":x['fea']['features'][0]['geometry']
        })
        a={'genre':x['type'],'features':x['fea'],'name':x['name']}
        arr.append(a)
    return geojson

if __name__ == '__main__':
    app.run(debug=True)