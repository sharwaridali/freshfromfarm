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

name_array=[]
qua_array=[]
rows=0
cols=1
arr=[]


'''def calculate_total(name_array,qua_array):
    prices=[]
    total_amt=0
    cur = mysql.connection.cursor()
    for name in name_array:
        print(name)
    for name in name_array:
        resultval=cur.execute("select price from product where prod_id = %s",[int(name)])
        #print(resultval)
        if resultval > 0:
            prices.append(resultval)
            #print(prices)
    mysql.connection.commit()
    cur.close()
    #for price,qua in zip(prices,quantities):
        #total_amt+=int(price)*int(qua)
    return total_amt'''


@app.route('/')
def index():
    return render_template('index.html')

@app.route('/products')
def products():
    cur = mysql.connection.cursor()
    resultValue = cur.execute("SELECT * FROM product")
    if resultValue > 0:
        productDetails = cur.fetchall()
        cur.close()
        return render_template('products.html',productDetails=productDetails)
    return render_template('products.html')

@app.route('/login_option')
def login_option():
    return render_template('login_option.html')

@app.route('/registration_option')
def registration_option():
    return render_template('registration_option.html')

@app.route('/customer_login', methods=['POST','GET'])
def customer_login():
    if request.method == 'POST':
        #Fetch Form Data
        details = request.form
        email = details['email']
        password = details['psw'].encode('utf-8')
        cur = mysql.connection.cursor()
        cur.execute("SELECT * FROM customer WHERE email = %s",[email])
        user = cur.fetchone()
        if user:
            db_email=user[1]
            db_psw=user[2]
            db_fname=user[3]
            db_lname=user[4]
            if check_password_hash(db_psw,password)== True:
                session['email']=email
                session['name']=db_fname+" "+db_lname+" "
                return redirect(url_for('dashboard',email=email))
            else:
                return render_template('customer_login.html',msg='Incorrect password')
        else:
                return render_template('customer_login.html',msg='Username Does not exists!!! Please Register First')
    else:
        return render_template('customer_login.html')

@app.route('/farmer_login', methods=['POST','GET'])
def farmer_login():
    if request.method == 'POST':
        #Fetch Form Data
        details = request.form
        email = details['email']
        password = details['psw'].encode('utf-8')
        cur = mysql.connection.cursor()
        cur.execute("SELECT * FROM farmer WHERE email = %s",[email])
        user = cur.fetchone()
        if user:
            db_email=user[1]
            db_psw=user[2]
            db_fname=user[3]
            db_lname=user[4]
            if check_password_hash(db_psw,password)== True:
                session['email']=email
                session['name']=db_fname+" "+db_lname+" "
                return redirect(url_for('farmer_dashboard',email=email))
            else:
                return render_template('farmer_login.html',msg='Incorrect password')
        else:
                return render_template('farmer_login.html',msg='Username Does not exists!!! Please Register First')
    else:
        return render_template('farmer_login.html')

def checkPin(pincode):
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


@app.route('/customer_registration', methods=['POST','GET'])
def customer_registration():
    if request.method == 'POST':
        #Fetch Form Data
        customerDetails = request.form
        email = customerDetails['email']
        password = customerDetails['psw']
        fname = customerDetails['fname']
        lname = customerDetails['lname']
        address = customerDetails['address']
        apartment = customerDetails['apartment']
        pincode = customerDetails['pincode']
        phone = customerDetails['phone']
        pass_repeat = customerDetails['re_psw']
        psw = customerDetails['psw']
        #generate a password hash to securely store the password in database
        p_hash = generate_password_hash(password)
        ide = 0
        cur = mysql.connection.cursor()
        cur.execute("select email from customer where email = %s",[email])
        existing_email = cur.fetchone()
        if existing_email is None:
            if psw == pass_repeat:
                if checkPin(pincode):
                    if checkPhone(phone):
                        cur.execute("INSERT INTO customer(cust_id,email,psw,fname,lname,address,apartment,pincode,phone) VALUES(%s,%s,%s,%s,%s,%s,%s,%s,%s)", (ide,email,p_hash,fname,lname,address,apartment,pincode,phone))
                        mysql.connection.commit()
                        cur.close()
                        return redirect('/customer_login')
                    else:
                        return render_template('customer_registration.html', msg ="Incorrect Phone Number!!!")
                else:
                    return render_template('customer_registration.html', msg ="Incorrect Pincode!!!")
            else:
                return render_template('customer_registration.html', msg ="Password Don't Match!!!")
        else:
            #flash("Email Already exists!!!")
            return render_template('customer_registration.html', msg ="Email Already Exists!!!")
    return render_template('customer_registration.html', msg=" ")

@app.route('/farmer_registration', methods=['POST','GET'])
def farmer_registration():
    if request.method == 'POST':
        #Fetch Form Data
        farmerDetails = request.form
        email = farmerDetails['email']
        password = farmerDetails['psw']
        fname = farmerDetails['fname']
        lname = farmerDetails['lname']
        address = farmerDetails['address']
        taluka = farmerDetails['taluka']
        pincode = farmerDetails['pincode']
        phone = farmerDetails['phone']
        bank_acc_no=farmerDetails['bank_acc_no']
        ifsc=farmerDetails['ifsc']
        pass_repeat = farmerDetails['re_psw']
        psw = farmerDetails['psw']
        #generate a password hash to securely store the password in database
        p_hash = generate_password_hash(password)
        ide = 0
        cur = mysql.connection.cursor()
        cur.execute("select email from farmer where email = %s",[email])
        existing_email = cur.fetchone()
        if existing_email is None:
            if psw == pass_repeat:
                if checkPin(pincode):
                    if checkPhone(phone):
                        cur.execute("INSERT INTO farmer(farmer_id,email,psw,fname,lname,address,taluka,pincode,phone,bank_acc_no,ifsc_code) VALUES(%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)", (ide,email,p_hash,fname,lname,address,taluka,pincode,phone,bank_acc_no,ifsc))
                        mysql.connection.commit()
                        cur.close()
                        return redirect('/farmer_login')
                    else:
                        return render_template('farmer_registration.html', msg ="Incorrect Phone Number!!!")
                else:
                    return render_template('farmer_registration.html', msg ="Incorrect Pincode!!!")
            else:
                return render_template('farmer_registration.html', msg ="Password Don't Match!!!")
        else:
            return render_template('farmer_registration.html', msg ="Email Already Exists!!!")
    return render_template('farmer_registration.html', msg=" ") 

@app.route('/profile')
def profile():
    if 'email' in session:
        email = session['email']
    cur = mysql.connection.cursor()
    resultValue = cur.execute("SELECT * FROM customer where email=%s",[email])
    if resultValue > 0:
        customerDetails = cur.fetchone()
        mysql.connection.commit()
        cur.close()
        return render_template('profile.html',customerDetails=customerDetails)
    return render_template('profile.html')

@app.route('/dashboard')
def dashboard():
    cur = mysql.connection.cursor()
    resultValue = cur.execute("SELECT * FROM product")
    if resultValue > 0:
        productDetails = cur.fetchall()
        cur.close()
        return render_template('dashboard.html',productDetails=productDetails)
        
'''@app.route('/cart', methods=['POST','GET'])
def cart():
    for item in name_array:
        cur = mysql.connection.cursor()
        resultValue = cur.execute("SELECT * FROM product where prod_id=%s",[item])
        if resultValue > 0:
            productDetails = cur.fetchall()
            cur.close()
    return render_template('cart.html',productDetails=productDetails)'''

@app.route('/add_to_cart',methods=['POST','GET'])
def add_to_cart():
    itemDetails=request.form
    name = itemDetails["product"]
    qua = itemDetails["quantity"]
    temp=[]
    arr2=[]
    price=[]
    global rows
    global cols
    t_amt=0
    rows=rows+1
    if int(qua) == 0 or int(qua) < 0:
        return redirect('/dashboard')
    else:
        cur = mysql.connection.cursor()
        resultValue = cur.execute("SELECT * FROM product where prod_id=%s",[name])
        if resultValue > 0:
            productDetails = cur.fetchone()
            if int(qua) > productDetails[4]:
                return redirect('/dashboard')
            mysql.connection.commit()
            cur.close()
        if name not in name_array:
            name_array.append(name)
            qua_array.append(qua)
        #else:
        #    return render_template('dashboard.html',msg='item already added')
        #print(name_array)
        for name,qua in zip(name_array,qua_array):
            cur = mysql.connection.cursor()
            resultValue = cur.execute("SELECT * FROM product where prod_id=%s",[name])
            if resultValue > 0:
                productDetails = cur.fetchone()
                mysql.connection.commit()
                cur.close()
                temp.append(productDetails[1])
                temp.append(productDetails[2])
                temp.append(productDetails[3])
                temp.append(qua)
                price.append(productDetails[3])
                temp.append(productDetails[5])
                for i in range(rows):
                    col=[]
                    for j in range(cols):
                        if col not in col:
                            col.append(temp)
                            temp=[]
                            print(col)
                    if col not in arr:
                        arr.append(col)
        print(price)
        for p,q in zip(price,qua_array):
            t_amt += int(p)*int(q)
            print(p,q)
            print(t_amt)
        return render_template('cart.html',arr=arr,amount=t_amt)
    return redirect('/dashboard')

@app.route('/logout')
def logout():
    if 'email' in session:
        session.pop('email', None)
        name_array.clear()
        qua_array.clear()
        arr.clear()
        print(name_array)
        return redirect(url_for('customer_login'))
    else:
        return 'Log in first'

@app.route('/purchase',methods=['POST','GET'])
def purchase():
    global rows
    if request.method == 'POST':
        email=''
        if 'email' in session:
            email = session['email']
            cur = mysql.connection.cursor()
            result=cur.execute("SELECT cust_id FROM customer where email=%s",[email])
            if result > 0:
                cust_id = cur.fetchone()
            #print(cust_id)
            ide=0
            deliveryAdd=request.form
            address = deliveryAdd['address']
            apartment = deliveryAdd['apartment']
            pincode = deliveryAdd['pincode']
            offline=request.form.get("offline")
            online=request.form.get("online")
            mode_of_payment=""
            if offline == "on":
                mode_of_payment="offline"
            else:
                mode_of_payment="online"
            de_date=0
            status='F'
            print(qua_array)
            print(name_array)
            prices=[]
            quant=[]
            qu=0
            newqua=[]
            total_amt=0
            for name in name_array:
                cur.execute("select price,quantity from product where prod_id = %s",[int(name)])
                pr=cur.fetchone()
                prices.append(pr[0])
                quant.append(pr[1])
            print(prices)
            for price,qua in zip(prices,qua_array):
                total_amt += price * int(qua) 

            for i,j in zip(quant,qua_array):
                newqua.append(i-int(j))

                
            print(newqua)
            print(total_amt)
            temp1=','.join(name_array)
            temp2=','.join(qua_array)
            print(temp1)
            cur.execute("INSERT INTO orders(order_id, cust_id, address, apartment, pincode, order_date, delivery_date, order_status, products, Quantity, total_amt,mode_of_payment) VALUES(%s,%s,%s,%s,%s,curdate(),%s,%s,%s,%s,%s,%s)", (ide,cust_id,address,apartment,pincode,de_date,status,temp1,temp2,total_amt,mode_of_payment))
            for q,i in zip(newqua, name_array):
                cur.execute("update product set quantity=%s where prod_id=%s",(q,int(i)))
            mysql.connection.commit()
            cur.close()      
            arr.clear()
            rows=0
            if mode_of_payment=='online':
                return render_template("online_payment.html")
    return render_template('dashboard.html',total_amt=total_amt)

@app.route('/cart')
def cart():
    return render_template('cart.html')

@app.route('/online_payment')
def online_payment():
    return render_template('online_payment.html')

@app.route('/leafVeg')
def leafVeg():
    cur = mysql.connection.cursor()
    resultValue = cur.execute("SELECT * FROM product where category='LeafVegetable'")
    if resultValue > 0:
        productDetails = cur.fetchall()
        mysql.connection.commit()
        cur.close()
        return render_template('dashboard.html',productDetails=productDetails)
    return render_template('dashboard.html')

@app.route('/fruitVeg')
def fruitVeg():
    cur = mysql.connection.cursor()
    resultValue = cur.execute("SELECT * FROM product where category='FruitVegetable'")
    if resultValue > 0:
        productDetails = cur.fetchall()
        mysql.connection.commit()
        cur.close()
        return render_template('dashboard.html',productDetails=productDetails)
    return render_template('dashboard.html')

@app.route('/rootVeg')
def rootVeg():
    cur = mysql.connection.cursor()
    resultValue = cur.execute("SELECT * FROM product where category='rootVegetable'")
    if resultValue > 0:
        productDetails = cur.fetchall()
        mysql.connection.commit()
        cur.close()
        return render_template('dashboard.html',productDetails=productDetails)
    return redirect('dashboard.html')

@app.route('/fleafVeg')
def fleafVeg():
    cur = mysql.connection.cursor()
    resultValue = cur.execute("SELECT * FROM product where category='LeafVegetable'")
    if resultValue > 0:
        productDetails = cur.fetchall()
        mysql.connection.commit()
        cur.close()
        return render_template('farmer_dashboard.html',productDetails=productDetails)
    return render_template('farmer_dashboard.html')

@app.route('/ffruitVeg')
def ffruitVeg():
    cur = mysql.connection.cursor()
    resultValue = cur.execute("SELECT * FROM product where category='FruitVegetable'")
    if resultValue > 0:
        productDetails = cur.fetchall()
        mysql.connection.commit()
        cur.close()
        return render_template('farmer_dashboard.html',productDetails=productDetails)
    return render_template('farmer_dashboard.html')

@app.route('/rootVeg')
def frootVeg():
    cur = mysql.connection.cursor()
    resultValue = cur.execute("SELECT * FROM product where category='rootVegetable'")
    if resultValue > 0:
        productDetails = cur.fetchall()
        mysql.connection.commit()
        cur.close()
        return render_template('farmer_dashboard.html',productDetails=productDetails)
    return redirect('farmer_dashboard.html')

@app.route('/order_history')
def order_history():
    a=[]
    arr1=[]
    t1=[]
    t2=[]
    tempid=""
    tempqua=""
    i=0
    dates=[]
    if 'email' in session:
        email=session['email']
    cur = mysql.connection.cursor()
    cur.execute("SELECT cust_id FROM customer where email=%s",[email])
    cust_id=cur.fetchone()
    resultValue=cur.execute("SELECT * FROM orders where cust_id=%s group by order_date",[cust_id])
    if resultValue > 0:
        orderDetails = cur.fetchall()
        for order in orderDetails:
            a.append(order)
            i+=1
        l2=[]
        for order in a:
            l=[]
            l.append(order[5])
            l.append(order[6])
            l.append(order[10])
            if order[7] == 'T':
                l.append('Delivered')
            else:
                l.append('Order Placed')
            tempid+=(order[8])
            tempid+=","
            tempqua+=(order[9])
            tempqua+=","
            t1=tempid.split(",")
            t2=tempqua.split(",")
            #print(tempid)
            for ide,q in zip(t1,t2):
                if ide != '':
                    x=[]
                    cur.execute("SELECT prod_name,prod_description,price,unit FROM product where prod_id=%s",[int(ide)])
                    re=cur.fetchone()
                    x.append(re[0])
                    x.append(re[1])
                    x.append(re[2])
                    x.append(re[3])
                    x.append(q)
                    l.append(x)
                    #print(re)
            tempid=" "
            tempqua=" "
            t1=[]
            t2=[]
            l2.append(l)
            '''dates.append(orderDetails[i][5])
            tempid+=(orderDetails[i][8])
            tempid+=","
            tempqua+=(orderDetails[i][9])
            tempqua+=","
            i+=1
            #arr1.append(str(orderDetails[i][5]))
        t1=tempid.split(",")
        t2=tempqua.split(",")
        print(tempid)
        for ide in t1:
            if ide != '':
                cur.execute("SELECT prod_name,prod_description,price,unit FROM product where prod_id=%s",[int(ide)])
                re=cur.fetchone()
                col=[]
                for j in range(cols):
                    if col not in col:
                        col.append(re)
                        col.append(t2.pop(0))
                if col not in arr:
                    arr1.append(col)
        print(arr1)
        print(dates)'''
        print(l2)
        mysql.connection.commit()
        cur.close()
        return render_template('order_history.html',arr1=l2,i=0)
    return render_template('order_history.html')

@app.route('/farmer_dashboard')
def farmer_dashboard():
    cur = mysql.connection.cursor()
    resultValue = cur.execute("SELECT * FROM product")
    if resultValue > 0:
        productDetails = cur.fetchall()
        cur.close()
        return render_template('farmer_dashboard.html',productDetails=productDetails)

@app.route('/flogout')
def flogout():
    if 'email' in session:
        session.pop('email', None)
        name_array.clear()
        qua_array.clear()
        arr.clear()
        #print(name_array)
        return redirect(url_for('farmer_login'))
    else:
        return 'Log in first'

@app.route('/fprofile')
def fprofile():
    if 'email' in session:
        email = session['email']
    cur = mysql.connection.cursor()
    resultValue = cur.execute("SELECT * FROM farmer where email=%s",[email])
    if resultValue > 0:
        customerDetails = cur.fetchone()
        mysql.connection.commit()
        cur.close()
        return render_template('fprofile.html',customerDetails=customerDetails)
    return render_template('fprofile.html')

@app.route('/sell_history')
def sell_history():
    a=[]
    arr1=[]
    t1=[]
    t2=[]
    tempid=""
    tempqua=""
    i=0
    dates=[]
    if 'email' in session:
        email=session['email']
    cur = mysql.connection.cursor()
    cur.execute("SELECT farmer_id FROM farmer where email=%s",[email])
    cust_id=cur.fetchone()
    resultValue=cur.execute("SELECT * FROM sells where farmer_id=%s ",[cust_id])
    if resultValue > 0:
        orderDetails = cur.fetchall()
        for order in orderDetails:
            a.append(order)
            i+=1
        l2=[]
        for order in a:
            l=[]
            l.append(order[3])
            l.append(order[4])
            l.append(order[8])
            if order[5] == 'T':
                l.append('Delivered')
            else:
                l.append('Order Placed')
            tempid+=(order[6])
            tempid+=","
            tempqua+=(order[7])
            tempqua+=","
            t1=tempid.split(",")
            t2=tempqua.split(",")
            #print(tempid)
            for ide,q in zip(t1,t2):
                if ide != '':
                    x=[]
                    cur.execute("SELECT prod_name,prod_description,price,unit FROM product where prod_id=%s",[int(ide)])
                    re=cur.fetchone()
                    x.append(re[0])
                    x.append(re[1])
                    x.append(re[2])
                    x.append(re[3])
                    x.append(q)
                    l.append(x)
                    #print(re)
            tempid=" "
            tempqua=" "
            t1=[]
            t2=[]
            l2.append(l)
            '''dates.append(orderDetails[i][5])
            tempid+=(orderDetails[i][8])
            tempid+=","
            tempqua+=(orderDetails[i][9])
            tempqua+=","
            i+=1
            #arr1.append(str(orderDetails[i][5]))
        t1=tempid.split(",")
        t2=tempqua.split(",")
        print(tempid)
        for ide in t1:
            if ide != '':
                cur.execute("SELECT prod_name,prod_description,price,unit FROM product where prod_id=%s",[int(ide)])
                re=cur.fetchone()
                col=[]
                for j in range(cols):
                    if col not in col:
                        col.append(re)
                        col.append(t2.pop(0))
                if col not in arr:
                    arr1.append(col)
        print(arr1)
        print(dates)'''
        print(l2)
        mysql.connection.commit()
        cur.close()
        return render_template('sell_history.html',arr1=l2,i=0)
    return render_template('sell_history.html')

@app.route('/add_to_sell',methods=['POST','GET'])
def add_to_sell():
    itemDetails=request.form
    name = itemDetails["product"]
    qua = itemDetails["quantity"]
    temp=[]
    global rows
    global cols
    price=[]
    t_amt=0
    rows=rows+1
    if int(qua) == 0 or int(qua) < 0: 
        return redirect('/farmer_dashboard')
    else:
        if name not in name_array:
            name_array.append(name)
            qua_array.append(qua)
        for name,qua in zip(name_array,qua_array):
            print (name)
            print(name_array)
            cur = mysql.connection.cursor()
            resultValue = cur.execute("SELECT * FROM product where prod_id=%s",[name])
            if resultValue > 0:
                productDetails = cur.fetchone()
                print(productDetails)
                mysql.connection.commit()
                cur.close()
                temp.append(productDetails[1])
                temp.append(productDetails[2])
                temp.append(productDetails[8])
                temp.append(qua)
                temp.append(productDetails[5])
                price.append(productDetails[8])
                print(temp)
                for i in range(rows):
                    col=[]
                    for j in range(cols):
                        if col not in col:
                            col.append(temp)
                            temp=[]
                            print(col)
                    if col not in arr:
                        arr.append(col)
        for p,q in zip(price,qua_array):
            t_amt += int(p)*int(q)
        return render_template('fcart.html',arr=arr,amount=t_amt)
    return redirect('/farmer_dashboard')


@app.route('/sell',methods=['POST','GET'])
def sell():
    global rows
    if request.method == 'POST':
        address = request.form['address']
        email=''
        if 'email' in session:
            email = session['email']
            cur = mysql.connection.cursor()
            result=cur.execute("SELECT farmer_id FROM farmer where email=%s",[email])
            if result > 0:
                cust_id = cur.fetchone()
            #print(cust_id)
            ide=0
            de_date=0
            status='F'
            print(qua_array)
            print(name_array)
            prices=[]
            quant=[]
            qu=0
            newqua=[]
            total_amt=0
            for name in name_array:
                cur.execute("select purchase_price,quantity from product where prod_id = %s",[int(name)])
                pr=cur.fetchone()
                prices.append(pr[0])
                quant.append(pr[1])
            print(prices)
            for price,qua in zip(prices,qua_array):
                total_amt += price * int(qua) 

            for i,j in zip(quant,qua_array):
                newqua.append(i+int(j))
            print(newqua)
            print(total_amt)
            temp1=','.join(name_array)
            temp2=','.join(qua_array)
            print(temp1)
            cur.execute("INSERT INTO sells(sell_id, farmer_id, location,sell_date, delivery_date, sell_status, products, Quantity, total_amt) VALUES(%s,%s,%s,curdate(),%s,%s,%s,%s,%s)", (ide,cust_id,address,de_date,status,temp1,temp2,total_amt))
            for q,i in zip(newqua, name_array):
                cur.execute("update product set quantity=%s where prod_id=%s",(q,int(i)))
            mysql.connection.commit()
            cur.close()      
            arr.clear()
            rows=0
    return render_template('farmer_dashboard.html',total_amt=total_amt)

@app.route('/fcart')
def fcart():
    return render_template('fcart.html')

@app.route('/remove',methods=['POST','GET'])
def remove():
    ide= request.form['product']
    if ide in name_array:
        ind = index(ide)
    name_array.remove(ide)
    qua_array.pop(ind)
    return redirect('/dashboard')

if __name__ == '__main__':
    app.run(debug = True)