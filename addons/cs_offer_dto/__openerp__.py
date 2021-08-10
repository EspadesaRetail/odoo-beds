{
    'name': 'Custom Shopping Descuento adicional',
    'description': 'Promoción Descuento adicional',
    'summary': 'Permite hacer un descuento adicional a un producto',
    'category': 'sale',

    'version': '1.0.0',
    'author': 'Planes Soluciones Informáticas',
    'depends': ['sale', 'cs_model','cs_offer'],
    'data': [
        'views/offers_view.xml',
        'views/sale_view.xml',

        'security/ir.model.access.csv',


    ],
    'application': True,


    'images':[
            'static/description/splash_screen.png',
    ],

}
