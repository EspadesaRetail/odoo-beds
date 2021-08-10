{
    'name': "Custom Shopping Cross Selling",
    'description': "Venta de productos relacionados",
    'summary': 'Muestra los productos relacionados con el actual.',
    'category': 'sale',

    'version': '1.0.0',
    'author': 'Planes Soluciones Informáticas',
    'depends': ['website','website_sale','cs_model','cs_theme'],
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
