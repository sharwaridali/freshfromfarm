from flask import Flask, render_template, request, redirect, session,flash, g, url_for
from flask_mysqldb import MySQL
import yaml
from werkzeug.security import generate_password_hash,check_password_hash

app = Flask(__name__)
app.secret_key = "secretkey"

#DB Configuration
db = yaml.load(open('db_config.yaml'))
app.config['MYSQL_HOST']=db['mysql_host']
app.config['MYSQL_USER']=db['mysql_user']
app.config['MYSQL_PASSWORD']=db['mysql_password']
app.config['MYSQL_DB']=db['mysql_db']

mysql = MySQL(app)

@app.route('/', methods=['POST','GET'])
def index():
    return render_template('index.html')

@app.route('/login',methods=['POST','GET'])
def login():
    if request.method == 'POST':
        #Fetch Form Data
        details = request.form
        email = details['email']
        password = details['psw'].encode('utf-8')
        cur = mysql.connection.cursor()
        cur.execute("SELECT * FROM employee WHERE email = %s",[email])
        user = cur.fetchone()
        if user:
            db_email=user[1]
            db_psw=user[2]
            db_fname=user[3]
            db_lname=user[4]
            db_des=user[7]
            db_dept=user[6]
            print(db_dept)
            if check_password_hash(db_psw,password)== True:
                session['email']=email
                session['name']=db_fname+" "+db_lname+" "
                if db_des == 'Admin':
                    return redirect(url_for('admin_dashboard',email=email))
                elif db_des == 'manager' and db_dept=='shipping':
                    return redirect(url_for('shipping_manager_dashboard',email=email))
                elif db_des == 'delivery_emp' and db_dept=='shipping':
                    return redirect(url_for('delivery_emp_dashboard',email=email))
                elif db_des == 'manager' and db_dept =='import':
                    return redirect(url_for('from_farmer_mn_dashboard',email=email))
                elif db_des == 'delivery_emp' and db_dept=='import':
                    return redirect(url_for('fdelivery_emp_dashboard',email=email))
            else:
                return render_template('login.html',msg='Incorrect Password!!')
        else:
            return render_template('login.html',msg='No such a user!!')
    else:
        return render_template('login.html')

@app.route('/admin_dashboard')
def admin_dashboard():
    return render_template('admin_dashboard.html')

'''def checkPin(pincode):
    pincode = str(pincode)
    if pincode.isnumeric():
        if len(pincode) == 6:
            if pincode[0:3] == '416':
                return True
            else:
                return False
        else:
            return False
    else:
        return False
'''
def checkPhone(phone):
    phone = str(phone)
    if phone.isnumeric():
        if len(phone) == 10:
            if phone[0] == '9' or phone[0] == '8' or phone[0] == '7' :
                return True
            else:
                return False
        else:
            return False
    else:
        return False

@app.route('/emp_registration', methods=['POST','GET'])
def emp_registration():
    if request.method == 'POST':
        #Fetch Form Data
        empDetails = request.form
        email = empDetails['email']
        password = empDetails['psw']
        fname = empDetails['fname']
        lname = empDetails['lname']
        address = empDetails['address']
        phone = empDetails['phone']
        date= empDetails['date']
        department=empDetails['department']
        designation=empDetails['designation']
        manager=empDetails['manage']
        pass_repeat = empDetails['re_psw']

        #generate a password hash to securely store the password in database
        p_hash = generate_password_hash(password)
        ide = 0
        cur = mysql.connection.cursor()
        cur.execute("select email from employee where email = %s",[email])
        existing_email = cur.fetchone()
        if existing_email is None:
            if password == pass_repeat:
                if checkPhone(phone):
                    cur.execute("insert into employee (emp_id, email,psw,fname, lname, address, department, designation, manager, doj,phone)values(%s,%s,%s, %s, %s, %s,%s,%s,%s,%s,%s)",(ide,email,p_hash,fname,lname,address,department,designation,manager,date,phone))
                    mysql.connection.commit()
                    cur.close()
                    return render_template('admin_dashboard.html')
                else:
                    return render_template('emp_registration.html', msg ="Incorrect Phone Number!!!")
            else:
                return render_template('emp_registration.html', msg ="Password Don't Match!!!")
        else:
            return render_template('emp_registration.html', msg ="Email Already Exists!!!")
    return render_template('emp_registration.html', msg=" ") 

'''
@app.route('/shipping_manager_login',methods=['POST','GET'])
def shipping_manager_login():
    if request.method == 'POST':
        #Fetch Form Data
        details = request.form
        email = details['email']
        password = details['psw'].encode('utf-8')
        cur = mysql.connection.cursor()
        cur.execute("SELECT * FROM employee WHERE email = %s and designation='manager'",[email])
        user = cur.fetchone()
        if user:
            db_email=user[1]
            db_psw=user[2]
            db_fname=user[3]
            db_lname=user[4]
            if check_password_hash(db_psw,password)== True:
                session['email']=email
                session['name']=db_fname+" "+db_lname+" "
                return redirect(url_for('shipping_manager_dashboard',email=email))
            else:
                return render_template('shipping_manager_login.html')
    else:
        return render_template('shipping_manager_login.html')
'''
@app.route('/shipping_manager_dashboard')
def shipping_manager_dashboard():
    if 'email' in session:
        email = session['email']
    cur = mysql.connection.cursor()
    result = cur.execute("SELECT fname,lname FROM employee where email=%s",[email])
    if result > 0:
        managerDetails=cur.fetchone()
    name = managerDetails[0]+" "+managerDetails[1]
    resultValue = cur.execute("SELECT emp_id,fname,lname,phone FROM employee where manager=%s",[name])
    if resultValue > 0:
            empDetails = cur.fetchall()
    resultValue = cur.execute("SELECT order_id FROM orders where order_status='F'")
    if resultValue > 0:
            orderDetails = cur.fetchall()
    else:
        orderDetails=[0]
    r = cur.execute("SELECT order_id FROM orders where order_status='P'")
    if r > 0:
        placedorderDetails = cur.fetchall()
        mysql.connection.commit()
        cur.close()
    elif r == 0:
        placedorderDetails=[0]

    return render_template('shipping_manager_dashboard.html',empDetails=empDetails,orderDetails=orderDetails,placedorderDetails=placedorderDetails)
 
@app.route('/from_farmer_mn_dashboard')
def from_farmer_mn_dashboard():
    if 'email' in session:
        email = session['email']
    cur = mysql.connection.cursor()
    result = cur.execute("SELECT fname,lname FROM employee where email=%s",[email])
    if result > 0:
        managerDetails=cur.fetchone()
    name = managerDetails[0]+" "+managerDetails[1]
    resultValue = cur.execute("SELECT emp_id,fname,lname,phone FROM employee where manager=%s",[name])
    if resultValue > 0:
            empDetails = cur.fetchall()
    resultValue = cur.execute("SELECT sell_id FROM sells where sell_status='F'")
    if resultValue > 0:
            orderDetails = cur.fetchall()
    else:
        orderDetails=[0]
    r = cur.execute("SELECT sell_id FROM sells where sell_status='P'")
    if r > 0:
        placedorderDetails = cur.fetchall()
        mysql.connection.commit()
        cur.close()
    elif r == 0:
        placedorderDetails=[0]

    return render_template('from_farmer_mn_dashboard.html',empDetails=empDetails,orderDetails=orderDetails,placedorderDetails=placedorderDetails)
 

'''
@app.route('/delivery_emp_login',methods=['GET','POST'])
def delivery_emp_login():
    if request.method == 'POST':
        #Fetch Form Data
        details = request.form
        email = details['email']
        password = details['psw'].encode('utf-8')
        cur = mysql.connection.cursor()
        cur.execute("SELECT * FROM employee WHERE email = %s and designation='delivery_emp'",[email])
        user = cur.fetchone()
        if user:
            db_email=user[1]
            db_psw=user[2]
            db_fname=user[3]
            db_lname=user[4]
            if check_password_hash(db_psw,password)== True:
                session['email']=email
                session['name']=db_fname+" "+db_lname+" "
                return redirect(url_for('delivery_emp_dashboard',email=email))
            else:
                return render_template('delivery_emp_login.html')
    else:
        return render_template('delivery_emp_login.html')
'''
@app.route('/delivery_emp_dashboard')
def delivery_emp_dashboard():
    if 'email' in session:
        email = session['email']
    cur = mysql.connection.cursor()
    result = cur.execute("SELECT emp_id FROM employee where email=%s",[email])
    if result > 0:
        empDetails=cur.fetchone()
    emp_id=empDetails[0]
    resultVal = cur.execute("SELECT order_id,customer.fname,customer.lname, orders.address, orders.apartment, orders.pincode, total_amt, mode_of_payment FROM orders join customer on orders.cust_id=customer.cust_id where order_id in(select order_id from delivery_to_customer where emp_id=%s)and order_status='P'",[emp_id])
    if resultVal > 0:
        orDetails=cur.fetchall()
    else:
        orDetails=[0]
    r=cur.execute("select orders.order_id from orders join delivery_to_customer on orders.order_id = delivery_to_customer.order_id where emp_id = %s and order_status='T'",[emp_id])
    if r > 0:
        oDetails=cur.fetchall()
    else:
        oDetails=[0]
    return render_template('delivery_emp_dashboard.html',orDetails=orDetails,oDetails=oDetails)

@app.route('/fdelivery_emp_dashboard')
def fdelivery_emp_dashboard():
    if 'email' in session:
        email = session['email']
    cur = mysql.connection.cursor()
    result = cur.execute("SELECT emp_id FROM employee where email=%s",[email])
    if result > 0:
        empDetails=cur.fetchone()
    emp_id=empDetails[0]
    resultVal = cur.execute("SELECT sell_id,farmer.fname,farmer.lname, sells.location, total_amt FROM sells join farmer on sells.farmer_id=farmer.farmer_id where sell_id in(select sell_id from delivery_from_farmer where emp_id=%s)and sell_status='P'",[emp_id])
    if resultVal > 0:
        orDetails=cur.fetchall()
    else:
        orDetails=[0]
    r=cur.execute("select sells.sell_id from sells join delivery_from_farmer on sells.sell_id = delivery_from_farmer.sell_id where emp_id = %s and sell_status='T'",[emp_id])
    if r > 0:
        oDetails=cur.fetchall()
    else:
        oDetails=[0]
    return render_template('fdelivery_emp_dashboard.html',orDetails=orDetails,oDetails=oDetails)

@app.route('/place_order',methods=['POST','GET'])
def place_order():
    if request.method == 'POST':
        ide = 0
        deliveryDetails = request.form
        order_id = deliveryDetails['order_id']
        emp_id = deliveryDetails['emp_id']
        cur = mysql.connection.cursor()
        cur.execute("insert into delivery_to_customer (delivery_id,order_id,emp_id)values(%s,%s,%s)",(ide,order_id,emp_id))
        cur.execute("update orders set order_status = 'P' where order_id = %s",[order_id])
        mysql.connection.commit()
        cur.close()
    return redirect(url_for('shipping_manager_dashboard'))

@app.route('/fplace_order',methods=['POST','GET'])
def fplace_order():
    if request.method == 'POST':
        ide = 0
        deliveryDetails = request.form
        order_id = deliveryDetails['order_id']
        emp_id = deliveryDetails['emp_id']
        cur = mysql.connection.cursor()
        cur.execute("insert into delivery_from_farmer (delivery_id,sell_id,emp_id)values(%s,%s,%s)",(ide,order_id,emp_id))
        cur.execute("update sells set sell_status = 'P' where sell_id = %s",[order_id])
        mysql.connection.commit()
        cur.close()
    return redirect(url_for('from_farmer_mn_dashboard'))

@app.route('/order_delivered',methods=['POST','GET'])
def order_delivered():
    if request.method == 'POST':
        deliveryDetails = request.form
        order_id = deliveryDetails['order_id']
        ddate=deliveryDetails['delivery_date']
        cur = mysql.connection.cursor()
        cur.execute("update orders set order_status = 'T' where order_id = %s",[order_id])
        cur.execute("update orders set delivery_date = %s where order_id = %s",(ddate,order_id))
        mysql.connection.commit()
        cur.close()
    return redirect(url_for('delivery_emp_dashboard'))

@app.route('/forder_delivered',methods=['POST','GET'])
def forder_delivered():
    if request.method == 'POST':
        deliveryDetails = request.form
        order_id = deliveryDetails['order_id']
        ddate=deliveryDetails['delivery_date']
        cur = mysql.connection.cursor()
        cur.execute("update sells set sell_status = 'T' where sell_id = %s",[order_id])
        cur.execute("update sells set delivery_date = %s where sell_id = %s",(ddate,order_id))
        mysql.connection.commit()
        cur.close()
    return redirect(url_for('fdelivery_emp_dashboard'))

@app.route('/logout')
def logout():
    if 'email' in session:
        session.pop('email', None)
        return redirect(url_for('index'))
    else:
        return 'Log in first'

if __name__ == '__main__':
    app.run(debug = True)