{
    'name': 'Custom Shopping Packs',
    'description': 'Promociones que afectan a los packs',
    'summary': 'Promociones que afectan a los packs y modifican el funcionamiento estándar de los packs.',
    'category': 'sale',

    'version': '1.0.0',
    'author': 'Planes Soluciones Informáticas',
    'depends': ['sale', 'cs_model','cs_offer','cs_pack'],
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
