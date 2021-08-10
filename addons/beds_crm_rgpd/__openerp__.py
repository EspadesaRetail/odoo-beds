{
    'name': "bed's Gestión de RGPD",
    'description': "Gestión de datos personales",
    'summary': 'Gestión de datos personales',
    'category': 'crm',

    'version': '1.0.0',
    'author': 'Planes Soluciones Informáticas',
    'depends': ['website','website_sale','mass_mailing'],
    'data': [
        'data/data.xml',
        'views/views.xml',
        'views/templates.xml',

        'security/ir.model.access.csv',


    ],
    'application': False,


    'images':[
            'static/description/splash_screen.png',
    ],

}
