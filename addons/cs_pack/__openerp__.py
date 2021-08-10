{
    'name': "Custom Shopping Pack's",
    'description': "Pack's de productos",
    'summary': 'Muestra los packs en la web',
    'category': 'sale',

    'version': '1.0.0',
    'author': 'Planes Soluciones Informáticas',
    'depends': ['website','cs_model','cs_theme'],
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
