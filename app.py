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
    LogSystem.log_info("Database tables created")


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
            LogSystem.log_error(
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
            LogSystem.log_info(f"Product '{new_product['name']}' successfully created with ID: {new_product['id']}")
            stripe.Price.create(
                unit_amount=price_data['unit_amount'],
                currency=price_data['currency'],
                product=new_product['id'],
                recurring=price_data.get('recurring'),
                tax_behavior=price_data['tax_behavior']
            )
            LogSystem.log_info(
                f"Price created for product '{new_product['name']}': Amount={price_data['unit_amount']}, Currency='{price_data['currency']}'")
            return jsonify(new_product), 201
        except Exception as e:
            LogSystem.log_error(f"Error creating a product in POST /product: {str(e)}. Request data: {request.json}")
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
            LogSystem.log_info(f"Created user: {username} with hashed password: {hashed_password}")
            db.session.add(new_user)
            LogSystem.log_info(f"New user '{username}' successfully added to the database with ID: {user_id}")
            db.session.commit()

            return jsonify({'message': 'Account created successfully', 'user_id': user_id, 'secret': secret}), 201
        except Exception as e:
            LogSystem.log_error(f"Error creating account: {str(e)}. Request data: {request.json}")
            return jsonify({'error': str(e)}), 500

    elif request.method == 'GET':
        # Get user information, requiring either a secret or password
        try:
            user_id = request.args.get('user_id')
            secret = request.args.get('secret')
            password = request.args.get('password')

            if not user_id or (not secret and not password):
                return jsonify({'error': 'Access denied: Missing required credentials'}), 401

            # Fetch the user by ID
            user = User.query.get(user_id)

            if not user:
                return jsonify({'error': 'User not found'}), 404

            # If the secret is provided, verify it
            if secret and user.secret == secret:
                return jsonify({
                    'username': user.username,
                    'coins': user.coins,
                    'purchases': [
                        {
                            'product_name': ph.product_name,
                            'purchase_date': ph.purchase_date.isoformat()
                        } for ph in PurchaseHistory.query.filter_by(user_id=user_id).all()
                    ]
                }), 200

            # If the password is provided, verify it
            if password and check_password_hash(user.password, password):
                return jsonify({
                    'username': user.username,
                    'coins': user.coins,
                    'purchases': [
                        {
                            'product_name': ph.product_name,
                            'purchase_date': ph.purchase_date.isoformat()
                        } for ph in PurchaseHistory.query.filter_by(user_id=user_id).all()
                    ]
                }), 200

            # If neither secret nor password matches, deny access
            return jsonify({'error': 'Access denied: Invalid credentials'}), 401

        except Exception as e:
            LogSystem.log_error(f"Error fetching account info: {str(e)}")
            return jsonify({'error': str(e)}), 500

    elif request.method == 'PUT':
        # Update coins (add or deduct), requires secret
        try:
            data = request.json
            user_id = data['user_id']
            secret = data.get('secret')
            action = data['action']  # "add" or "deduct"
            amount = data['amount']

            user = User.query.get(user_id)
            if not user or user.secret != secret:
                return jsonify({'error': 'Unauthorized'}), 401

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
            LogSystem.log_info(
                f"User '{user.id}' coins updated: Action='{action}', Amount={amount}. Total={user.coins}")
            return jsonify({'message': 'Coins updated successfully', 'coins': user.coins}), 200
        except Exception as e:
            LogSystem.log_error(f"Error updating coins: {str(e)}.")
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
        LogSystem.log_error(f"Error during login: {str(e)}. Request data: {request.json}")
        return jsonify({'error': str(e)}), 500


@app.route('/data', methods=['GET', 'PUT'])
def data():
    ALLOWED_KEYS = {"level", "preferences", "score"}  # Erlaubte Schlüssel im Datenfeld

    if request.method == 'GET':
        try:
            user_id = request.args.get('user_id')
            user = User.query.get(user_id)
            if not user:
                return jsonify({'error': 'User not found'}), 404
            return jsonify({'data': user.data}), 200
        except Exception as e:
            LogSystem.log_error(
                f"Error fetching user data: {str(e)}. User ID: {request.args.get('user_id', 'Unknown')}")
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

            # Aktuelle Daten laden und mit gefilterten Daten mergen
            current_data = user.data or {}  # Falls keine Daten vorhanden sind, ein leeres Dict verwenden
            current_data.update(filtered_data)  # Nur die gegebenen Felder aktualisieren

            # Speichern der aktualisierten Daten
            user.data = current_data
            db.session.commit()

            LogSystem.log_info(f"User '{user.id}' updated data: {filtered_data}")
            return jsonify({'message': 'Data updated successfully', 'updated_data': current_data}), 200
        except Exception as e:
            LogSystem.log_error(f"Error updating user data: {str(e)}. Request data: {request.json}")
            return jsonify({'error': str(e)}), 500


if __name__ == '__main__':
    app.run()
