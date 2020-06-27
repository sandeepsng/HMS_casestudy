from flask import Flask, render_template, request, url_for, redirect, make_response
import sqlite3
import datetime
import os
import hashlib   # used to hash passwords | SHA256

app = Flask(__name__)

conn = sqlite3.connect('hospital.db')
cur = conn.cursor()

## the following function is used to create the database
## and tables inside it.
## tables created: 
##               -- patients 
def createTable():	
	cur.execute('''CREATE TABLE IF NOT EXISTS patients (
		ws_ssn INTEGER UNIQUE,
		ws_pat_id INTEGER PRIMARY KEY AUTOINCREMENT,
		ws_pat_name TEXT NOT NULL,
		ws_adrs TEXT NOT NULL,
		ws_age INTEGER NOT NULL,
		ws_doj TEXT NOT NULL,
		ws_rtype TEXT,
		ws_status INTEGER DEFAULT 1
	) ''')
	conn.commit()

## return the current date in string type
## required format in case-study YYYY-MM-DD
def getCurrentDate():
	p = datetime.datetime.now()
	current_date = p.strftime("%Y-%m-%d")
	print(f"date_today: {current_date}")
	return current_date

## Inserting values and data into the tables
## inserting just for reference
## NOTE: Call this function only once at the time of running the app for the first time.
def insertIntoTable():
	date_today = getCurrentDate()	
	
	p_records = [
		(987412365,100000000,'natsu', 'f-street-01, fiore', 19,date_today,'General',1),
		(987412354,100000001,'gray', 'f-street-16, fiore', 19,date_today,'General',1)	
	]
	cur.executemany("INSERT INTO patients VALUES (?,?,?,?,?,?,?,?)" , p_records)
	print(f"INSERTED {cur.rowcount} rows")
	conn.commit()

def get_sha256_string(password):
	return hashlib.sha256(password.encode()).hexdigest()

def create_and_insert_users():
	conn = sqlite3.connect("hospital.db")
	c = conn.cursor()
	try:
		c.execute('''CREATE TABLE IF NOT EXISTS users (
			id TEXT PRIMARY KEY,
			name TEXT NOT NULL,
			password TEXT NOT NULL,
			type TEXT NOT NULL
		)
		''')
		conn.commit()
	except:
		print("error in creating USERS table")
	
	u_records = [
		('RE0001','reuser1',get_sha256_string('tcs_user1'),'Registration'),
		('RE0002','reuser2',get_sha256_string('tcs_user2'),'Registration'),
		('PH0001','phuser1',get_sha256_string('tcs_phuser1'),'Pharmacist'),
		('DE0001','deuser1',get_sha256_string('tcs_deuser1'),'Diagnostics')
	]

	c.executemany("INSERT INTO users VALUES (?,?,?,?);", u_records)
	conn.commit()
	print(f"--> inserted {c.rowcount} rows")
	c.close()
	conn.close()
	

def viewUsers():
	conn = sqlite3.connect('hospital.db')
	c = conn.cursor()
	c.execute("SELECT * FROM users")
	for i in c.fetchall():
		print(i)
	c.close()
	cur.close()


## ========================================================================
## =========== FLASK ROUTES and LOGIC BELOW ===============================
## ========================================================================

@app.route('/')
@app.route('/index')
def indexPage():
	return render_template("index.html",pageTitle="Welcome to XYZ Hospital")

@app.route('/login',methods=['GET','POST'])
def login():
	if 'loggedInUserId' in request.cookies:
		return redirect(url_for('userHomepage'))

	if request.method == 'POST':
		if request.form['userLogin_submit_btn']:
			print("--> here")
			user_name = request.form['user_name']
			hashed_user_password = get_sha256_string(request.form['user_password'])

			conn = sqlite3.connect("hospital.db")
			c = conn.cursor()
			c.execute("SELECT * from users WHERE name = ? and password = ? ;", (user_name,hashed_user_password))
			row = c.fetchone()
			if row is None:
				return "<h2>No such user exists</h2>"
			res = make_response(redirect(url_for('userHomepage')))
			res.set_cookie('loggedInUserId',row[0])
			res.set_cookie('loggedInUserName',row[1])
			res.set_cookie('loggedInUserType',row[3])
			return res

	return render_template("login.html",pageTitle="login")

@app.route('/logout',methods=['POST'])
def logout():
	if request.method == 'POST':
		res = make_response(redirect(url_for('login')))
		res.set_cookie('loggedInUserId','',expires=0)
		res.set_cookie('loggedInUserName','',expires=0)
		res.set_cookie('loggedInUserType','',expires=0)			
		return res


@app.route('/user')
def userHomepage():
	if 'loggedInUserId' in request.cookies:
		return render_template("userHomepage.html",pageTitle="User Home Page",cookie_data=request.cookies)
	return redirect(url_for('login'))


## view details of all the patients present in the "patients" table
@app.route('/patients')
def viewPatientDetails():
	if 'loggedInUserId' in request.cookies:
		patient_details = []
		conn2 = sqlite3.connect("hospital.db")
		c = conn2.cursor()
		c.execute("SELECT * from patients")
		for i in c.fetchall():
			patient_details.append(i)
		c.close()
		conn2.close()
		return render_template("patients.html",patient_details=patient_details,pageTitle="patients details")
	return redirect(url_for('login'))


## if GET request -> returns to the add-new-patient form/html page
## if POST request -> user has filled the "add new patient form" -> INSERT the patient details in the "patients" TABLE -> redirect to view all patients details
@app.route('/addnewpatient',methods=['GET','POST'])
def addNewPatient():
	if 'loggedInUserId' in request.cookies:
		if request.method == 'POST':
			conn = sqlite3.connect("hospital.db")
			c = conn.cursor()
			c.execute("INSERT INTO patients (ws_ssn, ws_pat_name, ws_adrs, ws_age, ws_doj, ws_rtype, ws_status) VALUES (?,?,?,?,?,?,?);", (request.form['p_ssn'],request.form['p_name'],request.form['p_addr'],request.form['p_age'],getCurrentDate(),request.form['p_rtype'],1))
			conn.commit()
			c.close()
			conn.close()
			return redirect(url_for('viewPatientDetails'))	
		return render_template("addnewpatients.html",pageTitle="add new patient")
	return redirect(url_for('login'))


@app.errorhandler(404)
def pageNotFound(e):
	return render_template("pageNotFound.html")

if __name__ == '__main__':
	createTable()
	#insertIntoTable()
	conn.close()
	#create_and_insert_users()
	app.run(debug=True)