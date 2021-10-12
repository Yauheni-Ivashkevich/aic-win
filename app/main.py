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
customers = users.customers  
clients = customers.clients


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
    # # return email        
    # elif password != password_two:
    #     return jsonify(messanger = "Пароли не совпадают")
    # else:
    #     return jsonify(messanger = "Давайте познакомимся")


@app.route("/add_customer", methods=['POST', 'GET', 'PUT'])
def customer():
    user_id = request.json['_id']
    customer_data = {
        # "_id": request.json["_id_customer"],
        "type_customer": request.json["type"],
        "name_customer": request.json["name"],
        "number_customer": request.json["number"],
            }
    dbaic.users.customers.update_one(
        {"_id": ObjectId(user_id)},
        {"$addToSet": {"customer_data": customer_data}}
    )
    return jsonify(messanger = "Заказчик добавлен")


@app.route("/add_clients", methods=['POST', 'GET', 'PUT'])
def clients():
    customer_id = request.json['_id']
    client_data = {
        "_id": request.json["_id_client"],
        "type_client": request.json["type"],
        "name_client": request.json["name"],
        "number_client": request.json["number"],
            }
    dbaic.clients.update_one(
        {"_id": ObjectId(customer_id)},
        {"$addToSet": {"client_data": client_data}}
    )
    return jsonify(messanger = "Контрагент добавлен")


@app.route("/", methods=['POST', 'GET', 'PUT'])
def home():
    users = dbaic.users.find()
    return Flask.jsonify([user for user in users])


@app.route("/add_many_customers", methods=['POST'])
def add_many():
    try:
        todo_many = dbaic.customers.insert_many([
            {"_id": 1, "type_customer": "type", "name_customer": "name", "number_customer": "number"},
            {"_id": 2, "type_customer": "type", "name_customer": "name", "number_customer": "number"},
            {"_id": 3, "type_customer": "type", "name_customer": "name", "number_customer": "number"}
        ], ordered=False)
    except BulkWriteError as e:
        return Flask.jsonify(message="duplicates encountered and ignored",
                             details=e.details,
                             inserted=e.details['nInserted'],
                             duplicates=[x['op'] for x in e.details['writeErrors']])

    return Flask.jsonify(message="success", insertedIds=todo_many.inserted_ids)


@app.route("/get_customer/<int:customerId>", methods=['GET'])
def insert_one(customerId):
    customer = dbaic.customers.find_one({"_id": customerId})
    return customer


@app.route("/replace_customer/<int:customerId>", methods=['PUT'])
def replace_one(customerId):
    customer = dbaic.customers.find_one_and_replace({"_id": customerId}, {"type_customer": "type"})
    return customer

@app.route("/update_customer/<int:customerId>", methods=['PUT'])
def update_one(customerId):
    result = dbaic.customers.find_one_and_update({'_id': customerId}, {"$set": {"type_customer": "updated type"}})
    return result


@app.route('/update_many', methods=['PUT'])
def update_many():
    customer = dbaic.customers.update_many({"type_customer": "type"}, {"$set": {"type_customer": "updated type"}})
    return customer.raw_result 


@app.route("/delete_customer/<int:customerId>", methods=['DELETE'])
def delete_todo(customerId):
    customer = dbaic.customers.find_one_and_delete({'_id': customerId}) 
    if customer is not None:
        return customer.raw_result
    return "ID does not exist"


@app.route('/delete_many', methods=['DELETE'])
def delete_many():
    customer = dbaic.customers.delete_many({"type_customer": "type"})
    return customer.raw_result


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
