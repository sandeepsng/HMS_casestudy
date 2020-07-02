from flask import Flask, render_template, request, url_for, redirect, make_response,session,sessions,jsonify
import sqlite3
import datetime
import os
import hashlib   # used to hash passwords | SHA256

app = Flask(__name__)
app.secret_key = "super secret key"

conn = sqlite3.connect('hospital.db')
cur = conn.cursor()

## the following function is used to create the database
## and tables inside it.
## tables created: 
##               -- patients 
##               -- users (For Registration,Pharmacist,Diagnostics)
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

## get_sha256_string(str) -> return str
## this function is used to encrypt the input password using SHA256
## returns the SHA256 encrypted string
def get_sha256_string(password:str):
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
	
## used for testing
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

## Main page 
## page on start up
@app.route('/')
@app.route('/index')
def indexPage():
	return render_template("index.html",pageTitle="Welcome to XYZ Hospital")

## Login route
## if the user is already logged-in (cookies are already set) -> redirect to userHomePage.html
## if the user is NOT logged-in -> return the login page
## if user submit login form -> check authentication -> [authorized] -> set cookies -> redirect to userHomePage.html
##                                                   -> [NOT authorized] -> return error message
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

			## set cookies
			res.set_cookie('loggedInUserId',row[0])
			res.set_cookie('loggedInUserName',row[1])
			res.set_cookie('loggedInUserType',row[3])
			return res

	return render_template("login.html",pageTitle="login")

## deletes the cookies and logs out
## redirect to login page
@app.route('/logout',methods=['POST'])
def logout():
	if request.method == 'POST':
		res = make_response(redirect(url_for('login')))
		# deleting cookies
		res.set_cookie('loggedInUserId','',expires=0)
		res.set_cookie('loggedInUserName','',expires=0)
		res.set_cookie('loggedInUserType','',expires=0)			
		return res

## used by Registrators,Pharmacist,Diagnostics people
## accessible only if the user is logged-in
## if user is logged-in -> redirect to userHomePage
## if user is not logged-in -> redirect to login page
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



## update patient details
## get the patient "id" from the update form and perform delete operation
@app.route('/updateDetails', methods=['POST','GET'])
def update():
	conn = sqlite3.connect("hospital.db")
	cur = conn.cursor()
	if 'loggedInUserId' in request.cookies:
		if request.method == 'POST':
			p_id = request.form['p_id']
			p_ssn = request.form['p_ssn']
			p_name = request.form['p_name']
			p_age = request.form['p_age']
			p_addr = request.form['p_addr']
			p_rtype = request.form['p_rtype']
			cur.execute(f"UPDATE patients SET ws_ssn={p_ssn}, ws_pat_name='{p_name}', ws_age={p_age}, ws_adrs='{p_addr}', ws_rtype='{p_rtype}' WHERE ws_pat_id={p_id};")
			conn.commit()
			cur.close()
			conn.close()
			return "updated!"			

		if request.method == 'GET':
			if request.args.get('id'):
				patient_id = request.args.get('id')
				
				cur.execute("SELECT * FROM patients WHERE ws_pat_id=?;",(patient_id,))
				patient_details = cur.fetchone()
				cur.close()
				conn.close()
				if patient_details is None:
					return "<h1> no such records found! </h1>"
				return render_template("updatePatientDetails.html",pageTitle="update patient details",id_editable=False,patient_details=patient_details,data_set=True)
		return render_template("updatePatientDetails.html",pageTitle="update patient details",data_set=False)
	return redirect(url_for('login'))

## Delete patient Record, using patient id
## get patient id and perform delete record 
@app.route('/delete',methods = ['GET','POST'])
def deletePatientRecord():
	conn = sqlite3.connect("hospital.db")
	cur = conn.cursor()
	if 'loggedInUserId' in request.cookies:
		if request.method == 'POST':
			if request.form['del_pr_confirm_btn'] == 'Delete Record':
				cur.execute(f"DELETE FROM patients WHERE ws_pat_id={request.form['pat_id']};")
				conn.commit()
				return redirect(url_for('deletePatientRecord'))
			elif request.form['del_pr_confirm_btn'] == 'Close':
				return redirect(url_for('deletePatientRecord'))
			
		if request.method == 'GET':
			if request.args.get('del_patient_submit_btn'):
				p_id = request.args.get('p_id')
				cur.execute(f"SELECT * FROM patients WHERE ws_pat_id={p_id};")
				patient_details = cur.fetchone()
				if patient_details is None:
					return "<h1>No such Records Found!</h1>"
				return render_template("deletePatientRecord.html",pageTitle="delete patient record",patient_details=patient_details,data_set=True)
		return render_template("deletePatientRecord.html",pageTitle="delete patient record")
	return redirect(url_for('login'))

		###############################################
################ searching for patient deatils using patiendID ####################
		###############################################

#for handling cases when no patient with the given Patiend ID is found
@app.route('/search_for_patient/ERROR')
def error_in_search():
	return render_template("searchError.html",pageTitle="No such patient found")


#MAIN SEARCH FUNCTION
@app.route('/search_for_patient',methods=['GET','POST'])
def searching(): # takes only one input parameter i.e patientId
	if 'loggedInUserId' in request.cookies:
		if request.method=="POST":
			conn_search = sqlite3.connect("hospital.db")
			c_search=conn_search.cursor()
			key=(request.form['patientID'],)
			c_search.execute("Select * FROM patients WHERE ws_pat_id=? ", key)
			
			patient=[]
			for j in c_search.fetchall():
				patient.append(j)
			c_search.close()
			conn_search.close()
			if len(patient)==0:
				return redirect(url_for("error_in_search"))
			else:
				return render_template("patients.html",patient_details=patient,pageTitle="patients details")
		return render_template("search_patient.html",pageTitle="Search for a patient")
	return redirect(url_for('login'))


				     ##############################
#####################################  Search function ends here  #######################################
				     ##############################

		###############################################
################  GET patient histroy deatils using patiendID ####################
		###############################################
@app.route('/getPatientDetails',methods=['GET','POST'])
def getPatientDetails(): # takes only one input parameter i.e patientId
	if 'loggedInUserId' in request.cookies:
		if request.method=="POST":
			conn_details = sqlite3.connect("hospital.db")
			c_details=conn_details.cursor()
			key=(request.form['patientID'],)
			c_details.execute("Select b.ws_pat_id,b.ws_pat_name,b.ws_age,b.ws_adrs,b.ws_doj,a.ws_med_name,a.ws_qty,c.Rate,a.ws_qty*c.Rate FROM medicines a INNER JOIN patients b ON a.ws_pat_id=b.ws_pat_id INNER JOIN MasterMedicines c ON a.ws_med_name=c.ws_med_name  WHERE a.ws_pat_id=? ", key)
			
			patient=[]
			
			
			for j in c_details.fetchall():
				patient.append(j)
			c_details.close()
			conn_details.close()
			
			if len(patient)==0:
				return redirect(url_for("error_in_search"))
			else:
				pid=patient[0]
				session['my_var'] = pid
				#print(pid)
				return render_template("patientHistrtoy.html",patient_details=patient,pageTitle="patient Histroy details")
		return render_template("getPatientDetails.html",pageTitle="Get paients details")
	return redirect(url_for('login'))


		###############################################
################  GET  deatils  ENDS HERE ####################
		###############################################
@app.route('/issueMedicines',methods=['GET','POST'])
def issueMedicines():
	my_var = session.get('my_var', None)
	my_var2=my_var[0]	
	return render_template("issueMedicines.html",pageTitle="issueMedicines")

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

## 404 error handler
## for custom error pages
@app.errorhandler(404)
def pageNotFound(e):
	return render_template("pageNotFound.html")

@app.route('/pat/<id>')
def test(id):
	conn = sqlite3.connect("hospital.db")
	c = conn.cursor()
	c.execute("SELECT * FROM patients WHERE ws_pat_id=?;",(id,))
	d = c.fetchone()
	print(d)
	return (f"{d[2]}")



if __name__ == '__main__':
	createTable()
	#insertIntoTable()
	conn.close()
	#create_and_insert_users()
	app.run(debug=True)
