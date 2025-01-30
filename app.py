from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
import stripe
import uuid
import key
from logsystem import LogSystem

game_name = 'Name of your Game'
api_version = '0.0.1'
stripe.api_key = key.privat_stripe_api_key
uuid_salt = 'your_salt_value'  # Replace 'your_salt_value' with a secure, hard-to-guess value

app = Flask(__name__)
LogSystem = LogSystem()

# Configure the database
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///game_shop.db'  # SQLite as the database
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)


# Database model for Users
class User(db.Model):
    id = db.Column(db.String(36), primary_key=True)  # Unique user ID
    username = db.Column(db.String(50), unique=True, nullable=False)
    password = db.Column(db.String(200), nullable=False)  # Encrypted password
    secret = db.Column(db.String(36), unique=True, nullable=False)  # Unique secure token
    data = db.Column(db.JSON, default={})  # Flexible JSON data field
    coins = db.Column(db.Integer, default=0)  # Coins field with default value


# Database model for Purchase history
class PurchaseHistory(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.String(36), db.ForeignKey('user.id'), nullable=False)  # Linked to User
    product_name = db.Column(db.String(100), nullable=False)
    purchase_date = db.Column(db.DateTime, nullable=False)  # Date of purchase


# Create tables if not exist
with app.app_context():
    db.create_all()
    LogSystem.info("Database tables created")


@app.route('/')
def index():
    return {'name': f'ShopAPI - {game_name}',
            'version': api_version
            }


@app.route('/product', methods=['GET', 'POST'])
def product():
    if request.method == 'GET':
        # Fetch products from Stripe
        try:
            products = stripe.Product.list()
            return jsonify({'products': products.data}), 200
        except Exception as e:
            LogSystem.error(
                f"Error fetching products in GET /product: {str(e)}. Associated user: {request.args.get('user_id', 'Unknown')}")
            return jsonify({'error': str(e)}), 500

    elif request.method == 'POST':
        # Create a new product in Stripe
        try:
            data = request.json

            # Convert price and set required fields
            price_data = {
                "unit_amount": int(data['price'] * 100),
                "currency": "eur",
                "recurring": {"interval": data['recurrence']} if data.get('recurrence') else None,
                "tax_behavior": data.get("tax_behavior", "exclusive")
            }

            # Create product in Stripe
            new_product = stripe.Product.create(
                name=data['name'],
                description=data.get('description', ''),
                metadata=data.get('metadata', {})
            )
            # Create Price for the product
            LogSystem.info(f"Product '{new_product['name']}' successfully created with ID: {new_product['id']}")
            # Create Price for the product
            stripe.Price.create(
                unit_amount=price_data['unit_amount'],
                currency=price_data['currency'],
                product=new_product['id'],
                recurring=price_data['recurring'],
                tax_behavior=price_data['tax_behavior']
            )
            LogSystem.info(
                f"Price created for product '{new_product['name']}': Amount={price_data['unit_amount']}, Currency='{price_data['currency']}'")
            return jsonify(new_product), 201
        except Exception as e:
            LogSystem.error(f"Error creating a product in POST /product: {str(e)}. Request data: {request.json}")
            return jsonify({'error': str(e)}), 500


@app.route('/account', methods=['POST', 'GET', 'PUT'])
def account():
    if request.method == 'POST':
        # Create a new account
        try:
            data = request.json
            username = data['username']
            password = data['password']

            # Check if the username already exists
            if User.query.filter_by(username=username).first():
                return jsonify({'error': 'Username already exists'}), 400

            # Hash the password and create the user
            hashed_password = generate_password_hash(password, method='pbkdf2:sha256')
            secret = str(uuid.uuid5(uuid.NAMESPACE_DNS, uuid_salt + str(uuid.uuid4())))

            user_id = str(uuid.uuid5(uuid.NAMESPACE_DNS, uuid_salt + str(uuid.uuid4())))  # Generate a unique user ID
            new_user = User(id=user_id, username=username, password=hashed_password, secret=secret)
            LogSystem.info(f"Created user: {username} with hashed password: {hashed_password}")
            db.session.add(new_user)
            LogSystem.info(f"New user '{username}' successfully added to the database with ID: {user_id}")
            db.session.commit()

            return jsonify({'message': 'Account created successfully', 'user_id': user_id, 'secret': secret}), 201
        except Exception as e:
            LogSystem.error(f"Error creating account: {str(e)}. Request data: {request.json}")
            return jsonify({'error': str(e)}), 500

    elif request.method == 'GET':
        # Get purchase history
        try:
            user_id = request.args.get('user_id')
            user = User.query.get(user_id)

            if not user:
                return jsonify({'error': 'User not found'}), 404

            # Fetch user purchases
            purchases = PurchaseHistory.query.filter_by(user_id=user_id).all()
            purchase_list = [
                {'product_name': p.product_name, 'purchase_date': p.purchase_date.isoformat()} for p in purchases
            ]

            return jsonify({'username': user.username, 'purchases': purchase_list}), 200
        except Exception as e:
            LogSystem.error(
                f"Error fetching purchase history: {str(e)}. User ID: {request.args.get('user_id', 'Unknown')}")
            return jsonify({'error': str(e)}), 500

    elif request.method == 'PUT':
        # Update coins (add or deduct)
        try:
            data = request.json
            user_id = data['user_id']
            action = data['action']  # "add" or "deduct"
            amount = data['amount']

            user = User.query.get(user_id)
            if not user:
                return jsonify({'error': 'User not found'}), 404

            # Perform the action (add or deduct coins)
            if action == 'add':
                user.coins += amount
            elif action == 'deduct':
                if user.coins < amount:
                    return jsonify({'error': 'Not enough coins'}), 400
                user.coins -= amount
            else:
                return jsonify({'error': 'Invalid action'}), 400

            db.session.commit()
            LogSystem.info(
                f"User '{user.id}' coins successfully updated: Action='{action}', Amount={amount}, TotalCoins={user.coins}")
            return jsonify({'message': 'Coins updated successfully', 'coins': user.coins}), 200
        except Exception as e:
            LogSystem.error(f"Error updating coins: {str(e)}. Request data: {request.json}")
            return jsonify({'error': str(e)}), 500


@app.route('/login', methods=['POST'])
def login():
    # Authenticate user
    try:
        data = request.json
        username = data['username']
        password = data['password']

        user = User.query.filter_by(username=username).first()
        if not user:
            return jsonify({'error': 'User not found'}), 404
        if not check_password_hash(user.password, password):
            app.logger.info(f"Login attempt failed. Invalid password for user: {username}")
            return jsonify({'error': 'Invalid username or password'}), 401

        return jsonify(
            {'message': 'Login successful', 'username': username, 'user_id': user.id, 'secret': user.secret}), 200
    except Exception as e:
        LogSystem.error(f"Error during login: {str(e)}. Request data: {request.json}")
        return jsonify({'error': str(e)}), 500


@app.route('/data', methods=['GET', 'PUT'])
def data():
    ALLOWED_KEYS = {"level", "preferences", "score"}  # Allowed keys in the data field

    if request.method == 'GET':
        try:
            user_id = request.args.get('user_id')
            user = User.query.get(user_id)
            if not user:
                return jsonify({'error': 'User not found'}), 404
            return jsonify({'data': user.data}), 200
        except Exception as e:
            LogSystem.error(f"Error fetching user data: {str(e)}. User ID: {request.args.get('user_id', 'Unknown')}")
            return jsonify({'error': str(e)}), 500

    elif request.method == 'PUT':
        try:
            data = request.json
            user_id = data['user_id']
            secret = data.get('secret')
            if not user_id or not secret:
                return jsonify({'error': 'Missing user_id or secret'}), 400
            user_data = data['data']

            user = User.query.get(user_id)
            if not user or user.secret != secret:
                return jsonify({'error': 'Unauthorized'}), 401

            # Validierung der Daten
            filtered_data = {key: value for key, value in user_data.items() if key in ALLOWED_KEYS}
            if len(filtered_data) != len(user_data):
                invalid_keys = [key for key in user_data if key not in ALLOWED_KEYS]
                return jsonify({'error': 'Invalid keys in data', 'invalid_keys': invalid_keys}), 400
            if len(filtered_data) != len(user_data):
                invalid_keys = [key for key in user_data if key not in ALLOWED_KEYS]
                return jsonify({'error': 'Invalid keys in data', 'invalid_keys': invalid_keys}), 400

            user.data = filtered_data
            user.data = filtered_data
            LogSystem.info(f"User '{user.id}' had their Stored data updated: UpdatedKeys={list(filtered_data.keys())}")
            return jsonify({'message': 'Data updated successfully'}), 200
        except Exception as e:
            LogSystem.error(f"Error updating user data: {str(e)}. Request data: {request.json}")
            return jsonify({'error': str(e)}), 500


if __name__ == '__main__':
    app.run()
