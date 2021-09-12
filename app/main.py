from flask_pymongo import PyMongo
import flask

app = flask.Flask(__name__)

mongodb_client = PyMongo(
    app,
    uri=
    "mongodb+srv://eugene_ivashkevich:1211@mongo-heroku-cluster.gi7cs.mongodb.net/myFirstDatabase?retryWrites=true&w=majority"
)
db = mongodb_client.db


@app.route("/add_one")
def add_one():
    db.todos.insert_one({'title': "todo title", 'body': "todo body"})
    return flask.jsonify(message="success")


@app.route("/")
def home_view():
    return "<h1>Welcome to Geeks for Geeks</h1>"
