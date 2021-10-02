from flask import Flask, render_template, request, url_for, redirect, session, flash
from .forms import ContactForm
from flask_mail import Mail, Message
import pymongo
import certifi
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
#connoct to your Mongo DB database
client = pymongo.MongoClient(
    "mongodb+srv://eugene_ivashkevich:wpLV8ZJcC1spQoc6@aic-win.ku48g.mongodb.net/aic-win?retryWrites=true&w=majority", tlsCAFile=certifi.where())

#get the database name
db = client.get_database('total_records')
#get the particular collection that contains the data
records = db.register


#assign URLs to have a particular route
@app.route("/", methods=['post', 'get'])
def index():
    message = ''
    #if method post in index
    if "email" in session:
        return redirect(url_for("logged_in"))
    if request.method == "POST":
        user = request.form.get("fullname")
        email = request.form.get("email")
        password1 = request.form.get("password1")
        password2 = request.form.get("password2")
        #if found in database showcase that it's found
        user_found = records.find_one({"name": user})
        email_found = records.find_one({"email": email})
        if user_found:
            message = 'There already is a user by that name'
            return render_template('index.html', message=message)
        if email_found:
            message = 'This email already exists in database'
            return render_template('index.html', message=message)
        if password1 != password2:
            message = 'Passwords should match!'
            return render_template('index.html', message=message)
        else:
            #hash the password and encode it
            hashed = bcrypt.hashpw(password2.encode('utf-8'), bcrypt.gensalt())
            #assing them in a dictionary in key value pairs
            user_input = {'name': user, 'email': email, 'password': hashed}
            #insert it in the record collection
            records.insert_one(user_input)

            #find the new created account and its email
            user_data = records.find_one({"email": email})
            new_email = user_data['email']
            #if registered redirect to logged in as the registered user
            return render_template('logged_in.html', email=new_email)
    return render_template('index.html')


@app.route("/login", methods=["POST", "GET"])
def login():
    message = 'Please login to your account'
    if "email" in session:
        return redirect(url_for("logged_in"))

    if request.method == "POST":
        email = request.form.get("email")
        password = request.form.get("password")

        #check if email exists in database
        email_found = records.find_one({"email": email})
        if email_found:
            email_val = email_found['email']
            passwordcheck = email_found['password']
            #encode the password and check if it matches
            if bcrypt.checkpw(password.encode('utf-8'), passwordcheck):
                session["email"] = email_val
                return redirect(url_for('logged_in'))
            else:
                if "email" in session:
                    return redirect(url_for("logged_in"))
                message = 'Wrong password'
                return render_template('login.html', message=message)
        else:
            message = 'Email not found'
            return render_template('login.html', message=message)
    return render_template('login.html', message=message)


@app.route('/logged_in')
def logged_in():
    if "email" in session:
        email = session["email"]
        return render_template('logged_in.html', email=email)
    else:
        return redirect(url_for("login"))


@app.route("/logout", methods=["POST", "GET"])
def logout():
    if "email" in session:
        session.pop("email", None)
        return render_template("signout.html")
    else:
        return render_template('index.html')


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
