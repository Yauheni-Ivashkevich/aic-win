from flask_pymongo import PyMongo
from flask import Flask, request, jsonify

app = Flask(__name__)

mongodb_client = PyMongo(
    app,
    uri=
    "mongodb+srv://eugene_ivashkevich:wpLV8ZJcC1spQoc6@aic-win.ku48g.mongodb.net/aic-win?retryWrites=true&w=majority"
)
db = mongodb_client.db


@app.route("/add_one")
def add_one():
    db.todos.insert_one({'title': "todo title", 'body': "todo body"})
    return jsonify(message="success")


@app.route("/test", methods=['GET', 'POST'])
def test():
    if request.method == "GET":
        return jsonify({"response": "Get Request Called"})
    elif request.method == "POST":
        req_Json = request.json
        name = req_Json['name']
        return jsonify({"response": "Hi " + name})


@app.route("/")
def home_view():
    return "<h1>Welcome to Geeks for Geeks</h1>"
