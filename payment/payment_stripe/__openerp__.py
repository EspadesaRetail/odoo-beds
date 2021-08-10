# -*- coding: utf-8 -*-

{
    'name': 'Stripe Payment Acquirer',
    'category': 'Hidden',
    'summary': 'Payment Acquirer: Stripe',
    'version': '8.0.1.0.2',
    'author': "Alberto Calvo Bazco",
    'depends': ['payment'],
    "external_dependencies": {
        "python": [
            "Crypto.Cipher.DES",
        ],
        "bin": [],
    },
    'data': [
        'views/stripe.xml',
        'views/payment_acquirer.xml'
    ],
    'license': 'AGPL-3',
    'installable': True,
}
