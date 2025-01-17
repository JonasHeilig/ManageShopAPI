from flask import Flask, request, jsonify
import stripe
import key

game_name = 'Name of your Game'
api_version = '0.0.1'
stripe.api_key = key.privat_stripe_api_key

app = Flask(__name__)


@app.route('/')
def index():
    return {'name': f'ShopAPI - {game_name}',
            'version': api_version
            }


@app.route('/product', methods=['GET', 'POST'])
def product():
    if request.method == 'GET':
        try:
            products = stripe.Product.list()
            return jsonify({'products': products.data}), 200
        except Exception as e:
            return jsonify({'error': str(e)}), 500

    elif request.method == 'POST':
        try:
            data = request.json
            price_data = {
                "unit_amount": int(data['price'] * 100),
                "currency": "euro",
                "recurring": {"interval": data['recurrence']} if data.get('recurrence') else None,
                "tax_behavior": data.get("tax_behavior", "exclusive")
            }
            new_product = stripe.Product.create(
                name=data['name'],
                description=data.get('description', ''),
                metadata=data.get('metadata', {})
            )
            stripe.Price.create(
                unit_amount=price_data['unit_amount'],
                currency=price_data['currency'],
                product=new_product['id'],
                recurring=price_data['recurring'],
                tax_behavior=price_data['tax_behavior']
            )
            return jsonify(new_product), 201
        except Exception as e:
            return jsonify({'error': str(e)}), 500


if __name__ == '__main__':
    app.run()
