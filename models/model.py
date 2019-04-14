from pymongo import MongoClient
from flask import session
from bson.objectid import ObjectId

client = MongoClient()
db = client['amazonRebuild']

# ---------------------------------------------------

def user_exists(username):
	query = {'username':username}
	result = db['users'].find(query)

	if result.count() > 0:
		return True
	return False

# ---------------------------------------------------	

def create_user(user_info):
	db['users'].insert_one(user_info)

# ---------------------------------------------------	

def login_user(username):
	query = {'username':username}
	result = db['users'].find_one(query)

	return result

# ---------------------------------------------------	

def product_exists(product_name):
	query = {'product_name':product_name}
	result = db['products'].find(query)

	if result.count() > 0:
		return True
	return False

# ---------------------------------------------------	

def create_product(product_info):
	db['products'].insert_one(product_info)

# ---------------------------------------------------	

def get_products():
	collection = db['products']
	cursor = collection.find({})
	return cursor

# ---------------------------------------------------	

def get_products_in_cart(username):
	cart = get_cart(username)
	cart_products = []

	for item in cart.keys():
		query = {'_id':ObjectId(item)}
		product = db['products'].find_one(query)
		cart_products.append(product)

	return cart_products

# ---------------------------------------------------	

def get_cart_total(cart_products, user_cart):
	cart_total = 0
	for product in cart_products:
		cart_total += (int(product['product_price']) * int(user_cart[str(product['_id'])]))

	return cart_total

# ---------------------------------------------------	

def add_product_to_cart(object_id, username):
	cart = get_cart(username)
	if object_id not in cart:
		cart.update({object_id: '1'})
	else:
		quantity = int(cart[object_id])
		cart.update({object_id: str(quantity + 1)})

	query = {'username':username}
	new_value = {"$set":{"cart": cart}}
	db.users.update(query, new_value)

# ---------------------------------------------------	

def remove_product_from_cart(object_id, username):
	cart = get_cart(username)
	quantity = int(cart[object_id])

	if quantity == 1:
		del cart[object_id]
	else:
		cart.update({object_id: str(quantity - 1)})

	query = {'username':username}
	new_value = {"$set":{"cart": cart}}
	db.users.update(query, new_value)

# ---------------------------------------------------

def clear_cart(username):
	cart = {}
	
	query = {'username':username}
	new_value = {"$set":{"cart": cart}}
	db.users.update(query, new_value)

# ---------------------------------------------------

def get_cart(username):
	query = {'username':username}
	user = db['users'].find_one(query)
	return user['cart']

# ---------------------------------------------------