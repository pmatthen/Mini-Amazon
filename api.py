from flask import Flask, render_template, request, redirect, url_for, session
from flask_bootstrap import Bootstrap
from flask_mail import Mail, Message
from models.model import *
import os

app = Flask(__name__)
Bootstrap(app)
app.config['SECRET_KEY'] = 'SECRET_KEY'

# ---------------------------------------------------

# email server
app.config.update(dict(
    DEBUG = True,
    MAIL_SERVER = 'smtp.gmail.com',
    MAIL_PORT = 465,
    MAIL_USE_TLS = False,
    MAIL_USE_SSL = True,
    MAIL_USERNAME = os.environ.get('MAIL_USERNAME'),
    MAIL_PASSWORD = os.environ.get('MAIL_PASSWORD')
))

# administrator list
ADMINS = ['poulosem@gmail.com']
mail = Mail(app)

# ---------------------------------------------------

@app.route('/send_email')
def send_email():
	msg = Message('Order Details', sender=ADMINS[0], recipients=ADMINS)
	msg.body = create_message()
	with app.app_context():
		mail.send(msg)

# ---------------------------------------------------

@app.route('/create_message')
def create_message():
	msg_body = ''
	cart = get_cart(session['username'])
	cart_products = get_products_in_cart(session['username'])
	cart_total = get_cart_total(cart_products, cart)

	for item in cart.keys():
		query = {'_id':ObjectId(item)}
		product = db['products'].find_one(query)
		msg_body = msg_body + 'Item Name: ' + product['product_name'] + '\n' + 'Product Price: ' + product['product_price'] + '\n' + 'Qty: ' + cart[item] + '\n\n'

	msg_body = msg_body + 'Cart Total: ' + str(cart_total) + '\n'
	msg_body = msg_body + 'Your items are on their way!'

	return msg_body

# ---------------------------------------------------

@app.route('/')
def home():
	return render_template('home.html', title="Home")

# ---------------------------------------------------	

@app.route('/contact')
def contact():
	return render_template('contact.html', title="Contact")

# ---------------------------------------------------		

@app.route('/login', methods=['POST'])
def login():
	username = request.form['name']
	password = request.form['password']

	user = login_user(username)

	if user is None:
		return "User not found"

	if user['password'] == password:
		session['username'] = user['username']
		session['c_type'] = user['c_type']
		return redirect(url_for('home'))
	return "Password incorrect"	

# ---------------------------------------------------		

@app.route('/signup', methods=['POST'])
def signup():
	user_info = {}
	user_info['username'] = request.form['name']
	user_info['email'] = request.form['email']
	user_info['password'] = request.form['password']
	user_info['c_type'] = request.form['c_type']
	rpassword = request.form['rpassword']

	if user_exists(user_info['username']) is False:
		if rpassword == user_info['password']:
			if user_info['c_type'] == "buyer":
				user_info['cart'] = {}
			create_user(user_info)
			session['username'] = user_info['username']
			session['c_type'] = user_info['c_type']
			return redirect(url_for('home'))
		return "The password you re-entered does not match, please try again"	
	return "Username already exists, please choose another"

# ---------------------------------------------------		

@app.route('/add_products', methods=['POST'])
def add_products():
	product_info = {}
	product_info['product_name'] = request.form['product_name']
	product_info['product_price'] = request.form['product_price']
	product_info['product_description'] = request.form['product_description']
	product_info['seller_name'] = session['username']

	if product_exists(product_info['product_name']) is False:
		create_product(product_info)
		return redirect(url_for('home'))
	return "Please add a unique product"

# ---------------------------------------------------		

@app.route('/seller_products')
def seller_products():
	products = get_products()
	return render_template('seller_products.html', products=products)

# ---------------------------------------------------		

@app.route('/all_products')
def all_products():
	products = get_products()
	return render_template('all_products.html', products=products)

# ---------------------------------------------------	

@app.route('/cart')
def cart():
	cart_products = get_products_in_cart(session['username'])
	user_cart = get_cart(session['username'])
	cart_total = get_cart_total(cart_products, user_cart)

	return render_template('cart.html', 
			user_cart = user_cart, 
			cart_products=cart_products, 
			cart_total=cart_total, 
			title="Your Cart")

# ---------------------------------------------------		

@app.route('/add_to_cart', methods=['POST'])
def add_to_cart():
	object_id = request.form['object_id']
	add_product_to_cart(object_id, session['username'])
	return redirect(url_for('cart'))

# ---------------------------------------------------		

@app.route('/remove_from_cart', methods=['POST'])
def remove_from_cart():
	object_id = request.form['object_id']
	remove_product_from_cart(object_id, session['username'])
	return redirect(url_for('cart'))	

# ---------------------------------------------------

@app.route('/buy_items_in_cart', methods=['POST'])
def buy_items_in_cart():
	send_email()
	clear_cart(session['username'])
	return redirect(url_for('cart'))	

# ---------------------------------------------------	

@app.route('/logout')
def logout():
	session.clear()
	return redirect(url_for('home'))

# ---------------------------------------------------		

if __name__ == '__main__':
	app.run(host='0.0.0.0', port=8000, debug=True)
