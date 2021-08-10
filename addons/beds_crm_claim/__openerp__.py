{
    'name': "bed's Gestión de reclamaciones",
    'description': "Gestión de reclamaciones",
    'summary': 'Gestión de reclamaciones',
    'category': 'crm',

    'version': '1.0.0',
    'author': 'Planes Soluciones Informáticas',
    'depends': ['website','website_sale','crm_claim','beds_model'],
    'data': [
        'views/views.xml',
        'views/templates.xml',

        'security/ir.model.access.csv',


    ],
    'application': False,


    'images':[
            'static/description/splash_screen.png',
    ],

}
