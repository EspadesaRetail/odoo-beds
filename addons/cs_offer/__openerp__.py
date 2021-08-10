{
    'name': 'Custom Shopping Promociones y Ofertas',
    'description': 'Promociones y oferas.',
    'summary': 'Promoviones Regalo',
    'category': 'sale',

    'version': '1.0.0',
    'author': 'Planes Soluciones Informáticas',
    'depends': ['sale','website_sale', 'cs_model','cs_theme'],
    'data': [
        'views/offer_views.xml',
        'views/offer_templates.xml',
        'views/offer_black_friday.xml',

        'security/ir.model.access.csv',


    ],
    'application': True,


    'images':[
            'static/description/splash_screen.png',
    ],

}
