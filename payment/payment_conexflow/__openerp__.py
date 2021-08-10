# -*- coding: utf-8 -*-

{
    'name': 'Conexflow Payment Acquirer',
    'category': 'Hidden',
    'summary': 'Payment Acquirer: Conexflow Implementation. Informática El Corte Ingles',
    'version': '8.0.1.0.2',
    'author': "Planes Soluciones Informáticas, www.planesnet.com",
    'depends': ['payment'],
    "external_dependencies": {
        "python": [
            "Crypto.Cipher.DES",
        ],
        "bin": [],
    },
    'data': [
        'views/cf.xml',
        'views/payment_acquirer.xml'
    ],
    'license': 'AGPL-3',
    'installable': True,
}
