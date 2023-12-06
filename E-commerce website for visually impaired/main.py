from flask import Flask, render_template, request, redirect, url_for, session
from flask_mysqldb import MySQL
from flask import jsonify
import secrets
import mysql.connector
from gtts import gTTS
import os






app = Flask(__name__)


app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD'] = 'HibaRashi.17'
app.config['MYSQL_DB'] = 'shopping'

UPLOAD_FOLDER = 'static/uploads'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

mysql = MySQL(app)

app.secret_key = secrets.token_hex(16)

# Allow only certain file types
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS





@app.route('/')
def home():
    return render_template('home.html')





#ADMIN


#admin login page
@app.route('/adminlogin')
def adminlogin():
    return render_template('adminlogin.html')

#checking credentials of admin
@app.route('/checkadmin', methods=['POST'])
def checkadmin():
    if request.method == 'POST':
        try:
            username = request.form['username']
            password = request.form['password']
            if username == 'admin' and password == 'admin123':
                return redirect(url_for('adminindex'))
            else:
                return render_template('adminlogin.html', message="Incorrect username or password")
        except Exception as e:
            return render_template('wentwrong.html')







@app.route('/adminindex')
def adminindex():
    cur = mysql.connection.cursor()
    cur.execute("SELECT * FROM products")
    data = cur.fetchall()
    cur.close()
    return render_template('AdminIndex.html', productdata=data)



@app.route('/viewcustomer')
def viewcustomer():
    cur = mysql.connection.cursor()
    cur.execute("SELECT * FROM users")
    data = cur.fetchall()
    cur.close()
    return render_template('ViewCustomer.html', registerlist=data)

@app.route('/vieworders')
def vieworders():
    cur = mysql.connection.cursor()
    cur.execute("SELECT * FROM orders")
    data = cur.fetchall()
    cur.close()
    return render_template('ViewOrders.html', orderlist=data)





@app.route('/proddetailsedit', methods=['POST'])
def proddetailsedit():
    result = request.form['result']
    print(result)
    cur = mysql.connection.cursor()
    cur.execute("SELECT  pid, pname, category, price, pdescription FROM products where pid = '%s'" % (result))
    data = cur.fetchone()
    pid, pname, category, price, pdescription = data
    return render_template('editProduct.html', pid=pid, pname=pname, category=category, price=price, pdescription=pdescription)


@app.route('/proddelete', methods=['POST'])
def proddelete():
    result = request.form['result']
    print(result)
    cur = mysql.connection.cursor()
    cur.execute("Delete from products where pid = '%s'" % (result))
    mysql.connection.commit()
    cur.close()
    return redirect(url_for('adminindex'))


@app.route('/addnewprod', methods=['POST'])
def addnewprod():
    if request.method == "POST":
        try:
            pname = request.form['pname']
            price = request.form['price']
            category = request.form['category']
            pdescription = request.form['pdescription']

            # Check if the 'image' file is present in the request
            if 'image' not in request.files:
                return render_template('wentwrong.html', message="No file part")

            f = request.files['image']

            # Check if the file name is empty
            if f.filename == '':
                return render_template('wentwrong.html', message="No selected file")

            # Check if the file type is allowed
            if not allowed_file(f.filename):
                return render_template('wentwrong.html', message="Invalid file type")

            # Save the file to the configured upload folder
            upload_path = os.path.join(app.config['UPLOAD_FOLDER'], f.filename)
            f.save(upload_path)

            # Update the product details in the database
            cur = mysql.connection.cursor()
            cur.execute("INSERT INTO products (pname, price, category, pdescription, pimage) VALUES (%s, %s, %s, %s, %s)", (pname, price, category, pdescription, f.filename))

            mysql.connection.commit()
            cur.close()

            return redirect(url_for('adminindex'))
        except Exception as e:
            return render_template('wentwrong.html', message=str(e))



@app.route('/updateprod', methods=['POST'])
def updateprod():
    if request.method == "POST":
        try:
            pid = request.form['pid']
            pname = request.form['pname']
            price = request.form['price']
            category = request.form['category']
            pdescription = request.form['description']

            # Update the product details in the database
            cur = mysql.connection.cursor()
            cur.execute("UPDATE products SET pname=%s, price=%s, category=%s, pdescription=%s WHERE pid=%s",
                        (pname, price, category, pdescription, pid))

            mysql.connection.commit()
            cur.close()

            return redirect(url_for('adminindex'))
        except Exception as e:
            return render_template('wentwrong.html', message=str(e))





@app.route('/addproduct')
def addproduct():
    return render_template('addproduct.html')


@app.route('/logout')
def logout():
    return render_template('home.html')



@app.route('/cancel')
def cancel():
    return render_template('AdminIndex.html')









#USER


@app.route('/gotologin')
def gotologin():
    return render_template('login.html')



@app.route('/login', methods=['POST'])
def login():
    # Get the recognized username and password from the form
    recognized_username = request.form.get('recognized_username')
    recognized_password = request.form.get('recognized_password')

    # Validate the credentials using MySQL query
    is_valid_credentials = check_credentials(recognized_username, recognized_password)

    session['username'] = recognized_username

    if is_valid_credentials:
        # Redirect to the products page if credentials are correct
        return redirect(url_for('products'))
    else:
        # Redirect to the signup page if credentials are incorrect
        return redirect(url_for('signup'))


def check_credentials(username, password):
    # Connect to the database
    cur = mysql.connection.cursor()

    # Execute a query to check credentials
    cur.execute("SELECT * FROM users WHERE username=%s AND upassword=%s", (username, password))

    # Fetch one row from the result set
    user = cur.fetchone()



    # Close the database connection
    cur.close()

    # Check if a user with the given credentials exists
    return user is not None

@app.route('/signup')
def signup():
    return render_template('signup.html')


@app.route('/signuserup', methods=['POST'])
def signuserup():
    recognized_name = request.form.get('recognized_name')
    recognized_username = request.form.get('recognized_username')
    recognized_password = request.form.get('recognized_password')
    recognized_mobile = request.form.get('recognized_mobile')
    recognized_address = request.form.get('recognized_address')

    cur = mysql.connection.cursor()

    cur.execute("select MAX(uid) from users")
    data = cur.fetchone()
    uid = data[0]
    uid = uid + 1

    insert_query = "insert into users(uid, uname, username, upassword, mobile_number, address) values (%s, %s, %s, %s, %s, %s)"
    data = (uid, recognized_name, recognized_username, recognized_password, recognized_mobile, recognized_address)

    cur.execute(insert_query, data)

    mysql.connection.commit()
    cur.close()

    return render_template('login.html')


@app.route('/usercart')
def usercart():
    username = session.get('username')
    cur = mysql.connection.cursor()
    cur.execute("SELECT cid, cpid, cpname, cpprice FROM cart where cusername = %s", (username,))
    data = cur.fetchall()
    cur.close()
    return render_template('usercart.html', cartlist=data)



@app.route('/userorders')
def userorders():
    username = session.get('username')
    cur = mysql.connection.cursor()
    cur.execute("SELECT opid, opname, opprice FROM orders WHERE ousername = %s", (username,))
    data = cur.fetchall()
    cur.close()
    return render_template('userorders.html', orderlist=data)


@app.route('/products')
def products():
    # Connect to the database
    cur = mysql.connection.cursor()

    # Execute a query to fetch product details from the 'products' table
    cur.execute("SELECT pid, pname, pdescription, price, pimage FROM products")



    # Fetch all rows from the result set
    products_data = cur.fetchall()

    # Close the database connection
    cur.close()

    # Render the HTML template with product details
    return render_template('products.html', products=products_data)




@app.route('/search_products', methods=['POST'])
def search_products():
    # Connect to the database
    cur = mysql.connection.cursor()

    # Get the search input from the form data
    recognized_search = request.form.get('recognized_search')

    # Execute a query to fetch filtered product details from the 'products' table
    cur.execute("SELECT pid, pname, pdescription, price FROM products WHERE pdescription COLLATE utf8mb4_unicode_ci LIKE %s", ('%' + recognized_search + '%',))

    # Fetch all rows from the result set
    products_data = cur.fetchall()

    # Close the database connection
    cur.close()

    # Return the filtered products as JSON
    return render_template('products.html', products=products_data)



@app.route('/add_product_to_cart', methods=['POST'])
def add_product_to_cart():

    pid = request.args.get('pid')
    # Connect to the database
    cur = mysql.connection.cursor()
    cusername = session.get('username')
    cur.execute("SELECT pdescription, pname, price from products where pid=%s", (pid, ))

    data = cur.fetchone()

    cpdescription= data[0]
    cpname= data[1]
    cpprice= data[2]



    cur.execute("select MAX(cid) from cart")
    cartdata = cur.fetchone()
    cid = cartdata[0]
    cid = cid + 1



    # Execute a query to add the product to the cart
    cur.execute("INSERT INTO cart (cid, cpdescription, cpid, cpname, cpprice, cusername) VALUES (%s, %s, %s, %s, %s, %s)", (cid, cpdescription, pid, cpname, cpprice, cusername))

    # Commit the transaction
    mysql.connection.commit()

    # Close the database connection
    cur.close()

    return redirect(url_for('usercart'))




@app.route('/buy_all_products', methods=['POST'])
def buy_all_products():
    # Connect to the database
    cur = mysql.connection.cursor()
    cusername = session.get('username')

    # Fetch all products in the cart for the current user
    cur.execute("SELECT cid, cpid, cpname, cpprice FROM cart WHERE cusername = %s", (cusername,))
    cart_data = cur.fetchall()

    # Loop through each product in the cart and add it to orders
    for product in cart_data:
        cid, cpid, cpname, cpprice = product

        # Fetch the maximum order ID
        cur.execute("SELECT MAX(oid) FROM orders")
        order_data = cur.fetchone()
        oid = order_data[0]
        if oid is None:
            oid = 1
        else:
            oid += 1

        # Fetch user address
        cur.execute("SELECT address FROM users WHERE username = %s", (cusername,))
        user_data = cur.fetchone()
        oaddress = user_data[0]

        # Insert the product into orders
        cur.execute("INSERT INTO orders (oid, opid, opname, opprice, ousername, oaddress) VALUES (%s, %s, %s, %s, %s, %s)",
                    (int(oid), int(cpid), cpname, cpprice, cusername, oaddress))

    # Delete all products from the cart for the current user
    cur.execute("DELETE FROM cart WHERE cusername = %s", (cusername,))

    # Commit the transaction
    mysql.connection.commit()

    # Close the database connection
    cur.close()

    return redirect(url_for('userorders'))






if __name__ == '__main__':
    app.run(debug=True)



