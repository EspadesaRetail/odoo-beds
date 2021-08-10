{
    'name': 'Custom Shopping Sin IVA',
    'description': 'Promociones regalo',
    'summary': 'Promoviones Regalo',
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
