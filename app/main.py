from bson.objectid import ObjectId
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
# customers = users.customers  
# clients = customers.clients


@app.route("/registration", methods=['POST'])
def registration():
    email = request.json['email']
    password = request.json['password']
    # password_two = request.json['password_two']
    check = users.find_one({"email": email})
    if check:
        return jsonify(messanger = "Пользователь с данным email уже зарегистрирован")
    else:
        user_info = dict(email=email)
        users.insert_one(user_info)
        return jsonify(messanger = "Пользователь успешно добавлен") 

    # return email        
    # elif password != password_two:
    #     return jsonify(messanger = "Пароли не совпадают")
    # else:
    #     return jsonify(messanger = "Давайте познакомимся")


@app.route("/customer", methods=['POST', 'GET', 'PUT'])
def customer():
    user_id = request.json['_id']
    customer_data = {
        "_id": "123", # Вопрос реализации ч/з id и вложенность 
        "type_customer": request.json["type_customer"],
        "name_customer": request.json["name_customer"],
        "number_customer": request.json["number_customer"],
            }
    dbaic.users.update(
        {"_id": ObjectId(user_id)},
        {"$set": {"customer_data": customer_data}}
    )
    return jsonify(messanger = "Заказчик добавлен")


@app.route("/clients", methods=['POST', 'GET', 'PUT'])
def clients():
    customer_id = request.json['_id']
    client_data = {
        "type_client": request.json["type_client"],
        "name_client": request.json["name_client"],
        "number_client": request.json["number_client"],
            }
    dbaic.users.update(
        {"_id": ObjectId(customer_id)},
        {"$set": {"client_data": client_data}}
    )
    return jsonify(messanger = "Контрагент добавлен")


@app.route("/")
def home():
    users = dbaic.users.find()
    return Flask.jsonify([user for user in users])


@app.route("/user_todo/<int:userId>")
def insert_one(userId):
    user = dbaic.users.find_one({"_id": userId})
    return user


@app.route("/replace_todo/<int:userId>")
def replace_one(userId):
    user = dbaic.users.find_one_and_replace({'_id': userId}, {'title': "modified title"})
    return user

@app.route("/update_user/<int:userId>")
def update_one(userId):
    result = dbaic.users.find_one_and_update({'_id': userId}, {"$set": {'title': "updated title"}})
    return result


@app.route('/update_many')
def update_many():
    user = dbaic.users.update_many({'title' : 'todo title two'}, {"$set": {'body' : 'updated body'}})
    return user.raw_result 


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
