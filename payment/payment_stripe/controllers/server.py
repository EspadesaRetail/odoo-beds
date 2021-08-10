#! /usr/bin/env python3.6

"""
server.py
Stripe Server.
Python 3.6 or newer required.
"""
import os
from flask import Flask, jsonify, request

import stripe
# This is a sample test API key. Sign in to see examples pre-filled with your key.
stripe.api_key = 'sk_test_4eC39HqLyjWDarjtT1zdp7dc'

app = Flask(__name__,
            static_url_path='',
            static_folder='.')

YOUR_DOMAIN = 'http://localhost:8069'

@app.route('/create-checkout-session', methods=['POST'])
def create_checkout_session():
    try:
        checkout_session = stripe.checkout.Session.create(
            payment_method_types=['card'],
            line_items=[
                {
                    'price_data': {
                        'currency': 'eur',
                        'unit_amount': 3000,
                        'product_data': {
                            'name': 'Pedido SOweb',
                            'images': ['https://www.beds.es/beds_theme/static/src/img/website_logo_es_ES.png'],
                        },
                    },
                    'quantity': 1,
                },
            ],
            mode='payment',
            success_url=YOUR_DOMAIN# + '/success.html',
            cancel_url=YOUR_DOMAIN# + '/cancel.html',
        )
        return jsonify({'id': checkout_session.id})
    except Exception as e:
        return jsonify(error=str(e)), 403

if __name__ == '__main__':
    app.run(port=4242)
