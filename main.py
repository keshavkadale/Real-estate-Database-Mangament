from os import name
import os
from flask import Flask,render_template,request,redirect,url_for,session,flash
from flask_sqlalchemy import SQLAlchemy
from flask_mysqldb import MySQL
from flask_mysqldb import MySQLdb
import MySQLdb.cursors
import re
from werkzeug.security import generate_password_hash,check_password_hash
from werkzeug.utils import secure_filename
import yaml




app = Flask(__name__)

# Set the secret key to some random bytes. Keep this really secret!
app.secret_key = b'_5#y2L"F4Q8z\n\xec]/'

#Configure db
db = yaml.safe_load(open('db.yaml'))
app.config['MYSQL_HOST']=db['mysql_host']
app.config['MYSQL_USER']=db['mysql_user']
app.config['MYSQL_PASSWORD']=db['mysql_password']
app.config['MYSQL_DB']=db['mysql_db']



mysql=MySQL(app)

@app.route("/")
def home():
        return render_template('index.html')
    
    

@app.route('/login', methods=['GET','POST'])
def login():
    if request.method=='POST':
        #Fetch form data
        userDetails=request.form
        email=userDetails['email']
        password=userDetails['password']
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute('SELECT * FROM account WHERE email = %s AND password = %s', (email, password))
        account = cursor.fetchone()
        # If account exists in accounts table in out database
        if account:
            # Create session data, we can access this data in other routes
            session['loggedin'] = True
            session['id'] = account['owner_id']
            session['username'] = account['name']
            # Redirect to home page
            print(session['id'])
            return render_template('index.html')
        else:
            # Account doesnt exist or username/password incorrect
            flash("invalid creditianls","danger")
    return render_template('login.html')


@app.route('/Adminlogin', methods=['GET','POST'])
def Adminlogin():
    if request.method=='POST':
        #Fetch form data
        userDetails=request.form
        email=userDetails['email']
        password=userDetails['password']
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute('SELECT * FROM adminaccount WHERE email = %s AND password = %s', (email, password))
        account = cursor.fetchone()
        # If account exists in accounts table in out database
        if account:
            # Create session data, we can access this data in other routes
            session['loggedin'] = True
            session['id'] = account['owner_id']
            session['username'] = account['name']
            # Redirect to home page
            print(session['id'])
            return render_template('index.html')
        else:
            # Account doesnt exist or username/password incorrect
            flash("invalid creditianls","danger")
    return render_template('adminlogin.html')




@app.route('/logout')
def logout():
    # Remove session data, this will log the user out
   session.pop('loggedin', None)
   session.pop('id', None)
   session.pop('username', None)
   # Redirect to login page
   flash("logout success","primary")
   return redirect(url_for('login'))

@app.route('/signup', methods=['GET','POST']) 
def  signup():
    if request.method=='POST':
        #Fetch form data
        userDetails=request.form
        name=userDetails['name']
        email=userDetails['email']
        password=userDetails['password']
        contact=userDetails['contact']
        address=userDetails['address']
        cur=mysql.connection.cursor()
        cur.execute("INSERT INTO account(name,email,password,contact,address) VALUES(%s,%s,%s,%s,%s)",(name,email,(password),contact,address))
        mysql.connection.commit()
        cur.close()
        return render_template('login.html')
    return render_template('signup.html')

@app.route('/users')
def users():
    cur=mysql.connection.cursor()
    resultValue=cur.execute("SELECT* FROM login")
    if resultValue>0:
        userDetails=cur.fetchall()
        return render_template('user.html',userDetails=userDetails)

@app.route('/buy')
def buy():
    # Check if user is loggedin
    if 'loggedin' in session:
        cur=mysql.connection.cursor()
        resultValue=cur.execute("SELECT* FROM property")
        if resultValue>0:
            propertyDetails=cur.fetchall()
        return render_template('buys.html', username=session['username'],propertyDetails=propertyDetails)
    # User is not loggedin redirect to login page
    return redirect(url_for('login'))


@app.route('/sell')
def sell():
    # Check if user is loggedin
    if 'loggedin' in session:
        # User is loggedin show them the home page
        return render_template('sell.html', username=session['username'])
    # User is not loggedin redirect to login page
    return redirect(url_for('login'))


@app.route('/listing', methods=['GET','POST']) 
def  listing():
    if request.method=='POST':
        #Fetch form datas
        userDetails=request.form
        userdetails=request.files
        owner_id=session['id']
        location=userDetails['location']
        city=userDetails['city']
        zipcode=userDetails['zipcode']
        description=userDetails['description']
        property_type=userDetails['property_type']
        price=userDetails['price']
        image=userdetails['image']
        image.save(os.path.join('static/images',secure_filename(image.filename)))
        images=image.filename
        
        cur=mysql.connection.cursor()
        cur.execute("INSERT INTO property(owner_id,location,city,zipcode,description,property_type,price,image) VALUES(%s,%s,%s,%s,%s,%s,%s,%s)",(owner_id,(location),city,zipcode,description,property_type,price,images))
        mysql.connection.commit()
        cur.close()
        return render_template('sell.html')
    return render_template('listing.html')


@app.route("/booking", methods=['GET','POST'])
def booking():
    if 'loggedin' in session:
        un=session['id']
        ad=1
        cur=mysql.connection.cursor()
        cur.execute("SELECT* FROM bookings WHERE buyer_id=(%s)",(un,) )
        bookingDetails=cur.fetchall()
        return render_template('bookings.html', username=session['username'],bookingDetails=bookingDetails)
    # User is not loggedin redirect to login page
    return redirect(url_for('login'))

@app.route("/adbooking", methods=['GET','POST'])
def adbooking():
    if 'loggedin' in session:
        un=session['username']
        cur=mysql.connection.cursor()
        resultValue=cur.execute("SELECT* FROM bookings")
        if resultValue>0:
            bookingDetails=cur.fetchall()
        return render_template('bookings.html', username=session['username'],bookingDetails=bookingDetails)
    # User is not loggedin redirect to login page
    return redirect(url_for('login'))







@app.route("/bookings", methods=['GET','POST'])
def bookings():
    if request.method=='POST':
        #Fetch form datas
        userDetails=request.form
        property_id=userDetails['property_id']
        seller_id=userDetails['owner_id']
        buyer_id=session['id']
        cur=mysql.connection.cursor()
        cur.execute("INSERT INTO bookings(property_id,seller_id,buyer_id) VALUES(%s,%s,%s)",(property_id,seller_id,buyer_id))
        mysql.connection.commit()
        cur.close()
        return render_template('index.html')
    return render_template('index.html')

@app.route("/payments")
def payments():
     if 'loggedin' in session:
        # User is loggedin show them the home page
        
        return render_template('payments.html', username=session['username'])
    # User is not loggedin redirect to login page
     return redirect(url_for('login'))

@app.route("/contact")
def contact():
    return render_template('contact.html')

   
if __name__ == '__main__':
    app.run(debug=True)