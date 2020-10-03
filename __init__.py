from flask import Flask, render_template, request, url_for, redirect, make_response, flash
import sqlite3
import datetime
import os
import hashlib   # used to hash passwords | SHA256

app = Flask(__name__)
app.secret_key = "abc"

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

## calculates room rent
## general : Rs. 2000
## single : Rs. 8000
## Semi : Rs. 4000
def getTotalRoomRent(room_type:str,days:int):
	if room_type == 'General':
		return 2000 * days
	elif room_type == 'Single':
		return 8000 * days
	return 4000 * days

	
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
				flash("Invalid Credentials! Please check your username or password")
				return redirect(url_for('login'))		
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
			flash("Patient Details updated successfully!")
			return redirect(url_for('update'))		

		if request.method == 'GET':
			if request.args.get('id'):
				patient_id = request.args.get('id')
				
				cur.execute("SELECT * FROM patients WHERE ws_pat_id=?;",(patient_id,))
				patient_details = cur.fetchone()
				cur.close()
				conn.close()
				if patient_details is None:
					flash("No such patient exists!")
					return redirect(url_for('update'))
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
				flash("Patient Details Deleted successfully!")
				return redirect(url_for('deletePatientRecord'))
			elif request.form['del_pr_confirm_btn'] == 'Close':
				return redirect(url_for('deletePatientRecord'))
			
		if request.method == 'GET':
			if request.args.get('del_patient_submit_btn'):
				p_id = request.args.get('p_id')
				cur.execute(f"SELECT * FROM patients WHERE ws_pat_id={p_id};")
				patient_details = cur.fetchone()
				if patient_details is None:
					flash("No such Patient exists!")
					return redirect(url_for('deletePatientRecord'))
				return render_template("deletePatientRecord.html",pageTitle="delete patient record",patient_details=patient_details,data_set=True)
		return render_template("deletePatientRecord.html",pageTitle="delete patient record")
	return redirect(url_for('login'))

		###############################################
################ searching for patient deatils using patiendID ####################
		###############################################

#for displaying details for the found patient
def individual(patient,key):
	return render_template("patients.html",function="search",key=key,patient_details=patient,pageTitle="Details of required patient:")

#for handling cases when no patient with the given Patiend ID is found
@app.route('/search_for_patient/ERROR/<value>/<quant>')
def error_in_search(value,quant):
	return render_template("searchError.html",value=value,quant=quant,pageTitle="No such patient found")


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
				flash("No such Patient found!")
				return redirect(url_for('searching'))
			else:
				test_search = sqlite3.connect("diagnostics.db")
				d_search=test_search.cursor()
				d_search.execute("Select Test_ID FROM track_diagnostics WHERE Patient_ID=? ", key)
						
				already_taken_tests_ID=[]
				for k in d_search.fetchall():
					already_taken_tests_ID.append(k)
							
				d_search.close()
				test_search.close()

				
				#####geting price detailsof testsconducted already

				# already_test_search = sqlite3.connect("diagnostics.db")
				# dp_search=already_test_search.cursor()

				# tests=[]
				# for each in already_taken_tests_ID:
				# 	dp_search.execute("Select * FROM Diagnostics_master WHERE Test_ID=? ", each)
				# 	for k in dp_search.fetchall():
				# 		tests.append(k)
							
				# dp_search.close()
				# already_test_search.close()


				return individual(patient,key)
		return render_template("search_patient.html",pageTitle="Search for a patient")
	return redirect(url_for('login'))

				     ##############################
#####################################  Search function ends here  #######################################
				     ##############################


## if GET request -> returns to the add-new-patient form/html page
## if POST request -> user has filled the "add new patient form" -> INSERT the patient details in the "patients" TABLE -> redirect to view all patients details
@app.route('/addnewpatient',methods=['GET','POST'])
def addNewPatient():
	if 'loggedInUserId' in request.cookies:
		if request.method == 'POST':
			conn = sqlite3.connect("hospital.db")
			c = conn.cursor()
			address = request.form['p_addr'] + ", " + request.form['p_state']
			try:
				c.execute("INSERT INTO patients (ws_ssn, ws_pat_name, ws_adrs, ws_age, ws_doj, ws_rtype, ws_status) VALUES (?,?,?,?,?,?,?);", (request.form['p_ssn'],request.form['p_name'],address,request.form['p_age'],getCurrentDate(),request.form['p_rtype'],1))
				conn.commit()
				c.close()
				conn.close()
				flash("Patient Record uploaded successfully!")
				return redirect(url_for('addNewPatient'))
			except:
				flash("An error occured!")
				return redirect(url_for('addNewPatient'))
			#return redirect(url_for('viewPatientDetails'))	
		return render_template("addnewpatients.html",pageTitle="add new patient")
	return redirect(url_for('login'))





########################################### DIAGNOSTIC SECTION  ###################################
										#		STARTS  		#
#########################################  DIAGNOSTIC SECTION  ############################################

@app.route('/update_test/<patientID>/<test_ID>',methods=['GET','POST'])
def update_test(patientID,test_ID):
	conn_pat=sqlite3.connect("diagnostics.db")
	c_pat=conn_pat.cursor()

	# "track_diagnostics" is the table for tracking which patient has taken which tests
	c_pat.execute("INSERT INTO track_diagnostics (Patient_ID,test_ID) VALUES (?,?);", (patientID,test_ID))
	conn_pat.commit()
	c_pat.close()
	conn_pat.close()
	
	return render_template("base.html",function="update")


#main diagnostics screen for searching diagnosis test by name
@app.route('/searchTest/<key>',methods=['GET','POST'])
def search_test(key):
	if request.method=="POST":
		conn_pat=sqlite3.connect("hospital.db")
		c_pat=conn_pat.cursor()
		a=[str(s) for s in key.split(",")]
		b=a[0]
		actual_int=int(b[3:12])
		actual_key=(str(actual_int),)
		c_pat.execute("Select * FROM patients WHERE ws_pat_id=? ", actual_key)

		patient=[]
		for i in c_pat.fetchall():
			patient.append(i)
		c_pat.close()
		conn_pat.close()

		if len(patient)==0:
			return redirect(url_for("error_in_search"))

		###########################for displaying alredy taken tests ################
		test_search = sqlite3.connect("diagnostics.db")
		d_search=test_search.cursor()
		d_search.execute("Select Test_ID FROM track_diagnostics WHERE Patient_ID=? ", actual_key)
				
		already_taken_tests_ID=[]
		for k in d_search.fetchall():
			already_taken_tests_ID.append(k)
					
		d_search.close()
		test_search.close()

		
		#####geting price detailsof testsconducted already

		already_test_search = sqlite3.connect("diagnostics.db")
		dp_search=already_test_search.cursor()

		already_taken_tests_details=[]
		for each in already_taken_tests_ID:
			dp_search.execute("Select * FROM Diagnostics_master WHERE Test_ID=? ", each)
			for k in dp_search.fetchall():
				already_taken_tests_details.append(k)
					
		dp_search.close()
		already_test_search.close()





		#############################################################################

		conn_search = sqlite3.connect("diagnostics.db")
		c_search=conn_search.cursor()
		name=(request.form['Tests'],)

		#  "Diagnostics_master" is the table which store testID, names and charges of test to be conducted
		c_search.execute("Select * FROM Diagnostics_master WHERE Test_Name=? ", name)
		
		test_details=[]
		for j in c_search.fetchall():
			test_details.append(j)
		c_search.close()
		conn_search.close()
		if len(test_details)==0:
			return redirect(url_for("error_in_search"))
		else:
			return render_template("add_test.html", test_details=test_details,already=already_taken_tests_details, patient_detail=patient, pageTitle="test details")
	
	return render_template("search_test.html",key=key)



										   #############################
###########################################  DIAGNOSTIC SECTION ENDS HERE #####################
										   ##############################

########################################### PHARMACY SECTION  ###################################
										#		STARTS  		#
#########################################  PHARMACY SECTION  ############################################


@app.route('/update_test/<patientID>/<medicine_ID>/<issuedquant>/<new_quantity>')
def update_medicine(patientID,medicine_ID,issuedquant,new_quantity):
	

	conn_pat=sqlite3.connect("pharmacy.db")
	c_pat=conn_pat.cursor()


	# "track_diagnostics" is the table for tracking which patient has taken which tests
	c_pat.execute("INSERT INTO track_medicine (Patient_ID, Medicine_ID, quantity_issued) VALUES (?,?,?);", (patientID,medicine_ID,issuedquant))
	conn_pat.commit()
	c_pat.close()
	conn_pat.close()

	############## Updating availble quantity in medicine_master table  #########
	# new_quantity=int(new_quantity)
	co_pat=sqlite3.connect("pharmacy.db")
	cat=co_pat.cursor()

	# "track_medicine" is the table for tracking which patient has taken which medicine

	cat.execute(f"UPDATE medicine_master SET Quantity_available={new_quantity} WHERE Medicine_ID={medicine_ID};")
	co_pat.commit()
	cat.close()
	co_pat.close()
	
	
	return render_template("base.html",function="update")


def create_issued_med(already_taken_medicine_details,quantities):
	new_arr=[]

	count=0
	for every in already_taken_medicine_details:
		small=[]
		for i in range(len(every)):
			if i==2:
				small.append(quantities[count])
			else:
				small.append(every[i])
				
		count+=1
		new_arr.append(small)
	return new_arr	



@app.route('/searchMedicine/<key>',methods=['GET','POST'])
def search_medicine(key):
	if request.method=="POST":
		conn_pat=sqlite3.connect("hospital.db")
		c_pat=conn_pat.cursor()
		a=[str(s) for s in key.split(",")]
		b=a[0]
		actual_int=int(b[3:12])
		actual_key=(str(actual_int),)
		c_pat.execute("Select * FROM patients WHERE ws_pat_id=? ", actual_key)

		patient=[]
		for i in c_pat.fetchall():
			patient.append(i)
		c_pat.close()
		conn_pat.close()

		if len(patient)==0:
			return redirect(url_for("error_in_search"))

		###########################for displaying alredy taken medicine ################
		test_search = sqlite3.connect("pharmacy.db")
		d_search=test_search.cursor()
		d_search.execute("Select Medicine_ID, quantity_issued FROM track_medicine WHERE Patient_ID=? ", actual_key)
		
		
		quantities=[]
		already_medicine_taken_ID=[]
		for k in d_search.fetchall():
			already_medicine_taken_ID.append((k[0],))
			quantities.append(k[1])


					
		d_search.close()
		test_search.close()

		
		#####geting price details of medicine prescribed to this patient already

		already_test_search = sqlite3.connect("pharmacy.db")
		dp_search=already_test_search.cursor()

		already_taken_medicine_details=[]
		for each in already_medicine_taken_ID:
			dp_search.execute("Select * FROM medicine_master WHERE Medicine_ID=? ", each)
			for k in dp_search.fetchall():
				already_taken_medicine_details.append(k)


		new_table=create_issued_med(already_taken_medicine_details,quantities)

					
		dp_search.close()
		already_test_search.close()

#############################################################################
############  CHECKING AVAILABILITY    #################

		
		
		
		quantity_required=int(request.form['quantity_issued'])
		
		
		
		
		comsearch = sqlite3.connect("pharmacy.db")
		c_search=comsearch.cursor()
		name=(request.form['Medicine'],)

	
		#  " medicine_master" is the table which store medicine_ID, names and price of medicine to be issued
		c_search.execute("Select * FROM medicine_master WHERE Medicine_name=? ", name)
		
		medicine_details=[]
		for j in c_search.fetchall():
			medicine_details.append(j)
			quantity_available=int(j[2])

		list_req=[list(medicine_details[0])]
		list_req[0][2]=quantity_required
		c_search.close()
		comsearch.close()
		if quantity_available<quantity_required:
			return redirect(url_for("error_in_search",value="quantity",quant=quantity_available))
		else:
			new_quantity=quantity_available-quantity_required
			
			return render_template("add_medicine.html", medicine_details=list_req,already=new_table, patient_detail=patient,issuedquant=quantity_required,new_quantity=new_quantity, pageTitle="Medicine details")
	
	return render_template("search_medicine.html",key=key)









@app.route('/billing',methods=['GET','POST'])
def billing():
	GRAND_TOTAL = 0
	if 'loggedInUserId' in request.cookies:
		if request.method == 'POST':
			if request.form['bill_btn'] == 'Close':
				return redirect(url_for('billing'))
			if request.form['bill_btn'] == 'Confirm':
				return render_template("thankYouPage.html",pageTitle="Thank You")
		if request.method == 'GET':
			if request.args.get('bill_btn_submit') == "GET Details":
				patient_id = request.args.get("p_id")
				conn = sqlite3.connect("hospital.db")
				c = conn.cursor()

				conn2 = sqlite3.connect("pharmacy.db")
				c2 = conn2.cursor()
				c.execute(f"SELECT * FROM patients WHERE ws_pat_id={patient_id}")
				patient_details = c.fetchone()
				if patient_details is None:
					flash("No such Patient Exists!")
					return redirect(url_for('billing'))
				
				c2.execute(f'''
						SELECT track_medicine.Medicine_ID, medicine_master.Medicine_name , medicine_master.Price_per_unit, track_medicine.quantity_issued, medicine_master.Price_per_unit * track_medicine.quantity_issued as Amount
						FROM track_medicine INNER JOIN medicine_master
						ON track_medicine.Medicine_ID = medicine_master.Medicine_ID
						WHERE track_medicine.Patient_ID={patient_id}''')
				pharmacy_details = c2.fetchall()
				pharmacy_set = True if len(pharmacy_details) !=0 else False
				print(pharmacy_set)
				pharmacy_total = 0
				if pharmacy_set:
					for pharma in pharmacy_details:
						pharmacy_total += pharma[4]
				
				conn3 = sqlite3.connect("diagnostics.db")
				c3 = conn3.cursor()
				c3.execute(f'''
						SELECT Diagnostics_master.Test_ID, Diagnostics_master.Test_Name, Diagnostics_master.charges 
						FROM Diagnostics_master INNER JOIN track_diagnostics 
						ON Diagnostics_master.Test_ID = track_diagnostics.test_ID
						WHERE track_diagnostics.Patient_ID = {patient_id}''')
				diag_details = c3.fetchall()
				diag_set = True if len(diag_details) !=0 else False
				diag_total = 0
				if diag_set:
					for d in diag_details:
						diag_total += d[2]
				
				date_format = "%Y-%m-%d"
				today_date = getCurrentDate()
				doj = datetime.datetime.strptime(patient_details[5],date_format)
				toc = datetime.datetime.strptime(today_date,date_format)
				delta = toc - doj
				room_rent_days_count = delta.days
				room_cost = getTotalRoomRent(patient_details[6],room_rent_days_count)
				GRAND_TOTAL = room_cost + pharmacy_total + diag_total

				return render_template("bill.html",pageTitle="billing", data_set=True, patient_details=patient_details,pharmacy_set=pharmacy_set,pharmacy_details=pharmacy_details,pharmacy_total=pharmacy_total,diag_set=diag_set,diag_details=diag_details,diag_total=diag_total,today_date=today_date,room_rent_days_count=room_rent_days_count,room_cost=room_cost,grand_total=GRAND_TOTAL)
		return render_template("bill.html",pageTitle="billing")
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
					    
def getApp():
    return app


if __name__ == '__main__':
	createTable()
	#insertIntoTable()
	conn.close()
	#create_and_insert_users()
	app.run(debug=True)
