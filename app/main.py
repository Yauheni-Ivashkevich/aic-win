from flask import Flask, jsonify, render_template, request, url_for, redirect, session, flash
from .forms import ContactForm
from flask_mail import Mail, Message
import pymongo
from pymongo.errors import BulkWriteError
import bcrypt
#set app as a Flask instance
app = Flask(__name__)

# configurations flask_mail 
app.config['MAIL_SERVER'] = 'smtp.gmail.com'
app.config['MAIL_PORT'] = 465
app.config['MAIL_USE_SSL'] = True
app.config['MAIL_USERNAME'] = 'gogenjack@gmail.com' 
app.config['MAIL_PASSWORD'] = '********' # your app specific password

mail = Mail(app)

#encryption relies on secret keys so they could be run
app.secret_key = "testing"
#connect to your Mongo DB database
# app.config["MONGO_URI"] = "mongodb+srv://eugene_ivashkevich:wpLV8ZJcC1spQoc6@aic-win.ku48g.mongodb.net/aic-win?retryWrites=true&w=majority"
client = pymongo.MongoClient(host="localhost", port=27017)
dbaic = client.dbaic
users = dbaic.users  
customers = users.customers  
clients = customers.clients


# @app.route("/registration", methods=['POST'])
# def registration():
#     record = request.get_json()
#     email = record['email']
#     password = record['password']
#     name = record['name']
#     registration_type = 'email'
#     user = User.objects(email=email, registration_type=registration_type).first()
#     if user:
#         return jsonify({"msg": "User is alredy"}), 409
#     else:
#         if password:
#             user = save_user(name, email, registration_type, password)
#             return user

#     users.accountants.insert_one({'title_': "todo title", 'body': "todo body"})
#     return Flask.jsonify(message="success")


@app.route("/add_one")
def add_one():
    dbaic.customers.insert_one({'title': "todo title", 'body': "todo body"})
    return Flask.jsonify(message="success")


@app.route("/add_many")
def add_many():
    try:
        todo_many = dbaic.todos.insert_many([
            {'_id': 1, 'title': "todo title one ", 'body': "todo body one "},
            {'_id': 8, 'title': "todo title two", 'body': "todo body two"},
            {'_id': 2, 'title': "todo title three", 'body': "todo body three"},
            {'_id': 9, 'title': "todo title four", 'body': "todo body four"},
            {'_id': 10, 'title': "todo title five", 'body': "todo body five"},
            {'_id': 5, 'title': "todo title six", 'body': "todo body six"},
        ], ordered=False) # вставит только действительные и уникальные записи 
    except BulkWriteError as e:
        return Flask.jsonify(message="duplicates encountered and ignored",
                             details=e.details,
                             inserted=e.details['nInserted'],
                             duplicates=[x['op'] for x in e.details['writeErrors']])

    return Flask.jsonify(message="success", insertedIds=todo_many.inserted_ids)


@app.route("/")
def home():
    todos = dbaic.todos.find()
    return Flask.jsonify([todo for todo in todos])


@app.route("/get_todo/<int:todoId>")
def insert_one(todoId):
    todo = dbaic.todos.find_one({"_id": todoId})
    return todo


@app.route("/replace_todo/<int:todoId>")
def replace_one(todoId):
    todo = dbaic.todos.find_one_and_replace({'_id': todoId}, {'title': "modified title"})
    return todo

@app.route("/update_todo/<int:todoId>")
def update_one(todoId):
    result = dbaic.todos.find_one_and_update({'_id': todoId}, {"$set": {'title': "updated title"}})
    return result


@app.route('/update_many')
def update_many():
    todo = dbaic.todos.update_many({'title' : 'todo title two'}, {"$set": {'body' : 'updated body'}})
    return todo.raw_result 


@app.route("/delete_todo/<int:todoId>", methods=['DELETE'])
def delete_todo(todoId):
    todo = dbaic.todos.find_one_and_delete({'_id': todoId})
    if todo is not None:
        return todo.raw_result
    return "ID does not exist"


@app.route('/delete_many', methods=['DELETE'])
def delete_many():
    todo = dbaic.todos.delete_many({'title': 'todo title two'})
    return todo.raw_result


@app.route("/save_file", methods=['POST', 'GET'])
def save_file():
    upload_form = """<h1>Save file</h1>
                     <form method="POST" enctype="multipart/form-data">
                     <input type="file" name="file" id="file">
                     <br><br>
                     <input type="submit">
                     </form>"""
                     
    if request.method=='POST':
        if 'file' in request.files:
            file = request.files['file']
            client.save_file(file.filename, file)
            return {"file name": file.filename}
    return upload_form


@app.route("/get_file/<filename>")
def get_file(filename):
    return client.send_file(filename) 


# forms for flask_mail
@app.route('/success')
def success():
	return render_template('success.html', title='Success Index', success=True)


@app.route('/contact', methods=['GET', 'POST'])
def contactForm():
    form = ContactForm()

    if request.method == 'GET':
	    return render_template('contact.html', form=form)
    elif request.method == 'POST':
	    if form.validate() == False:
		    flash('All fields are required !')
		    return render_template('contact.html', form=form)
	    else:
		    msg = Message(form.topic.data, sender='gogenjack@gmail.com', recipients=['gogenjack@gmail.com']) # your reciepients gmail id
		    msg.body = """
			from: %s; 
            email: %s; 
            message: %s
			"""% (form.name.data, form.email.data, form.message.data)
		    mail.send(msg)
		    return redirect(url_for('success')) 
