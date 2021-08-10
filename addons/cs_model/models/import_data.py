# -*- coding: utf-8 -*-


from openerp import api, tools
from openerp.osv import osv, fields, expression

import logging
import json
_logger = logging.getLogger(__name__)

import openerp.addons.decimal_precision as dp


# Tabla con los productos externos.
class external_products(osv.Model):
    _name = "external.product"
    _description = "External product"
    _order = "referencia"


    def _niveles(self, cursor, user, ids, name, arg, context=None):
        res = {}
        for rec in self.browse(cursor, user, ids, context=context):
            res[rec.id] = rec.nivel1 and rec.nivel2 and rec.nivel3 and rec.nivel3+'+'+rec.nivel2+'+'+rec.nivel1 or ''
        return res


    _columns = {
        # referencia
        'referencia': fields.char('Referencia', required=True, translate=True, select=True),
        'nombre': fields.text('Nombre',translate=True),
        'ancho': fields.text('Ancho'),
        'largo': fields.text('Largo'),
        'color': fields.text('Color'),
        'piel': fields.text('Tipo de piel'),
        'talla': fields.text('Talla'),
        'medidas': fields.text('Medidas textil'),
        'codigo_barras': fields.text('Cod barras'),
        'marca': fields.text('Marca'),
        'precio1': fields.float('Precio venta',digits_compute= dp.get_precision('Product Price')),
        'precio2': fields.float('Precio venta 2',digits_compute= dp.get_precision('Product Price')),
        'proveedor': fields.text('Proveedor'),
        'familia': fields.text('Familia'),
        'dto1': fields.integer('Dto ven 1'),
        'dto2': fields.integer('Dto ven 2'),
        'nivel1': fields.text('Nivel 1'),
        'nivel2': fields.text('Nivel 2'),
        'nivel3': fields.text('Nivel 3'),
        'niveles': fields.function(_niveles,string='Niveles',type='text'),
        'for_delete': fields.boolean('Para borrar'),
    }

    _defaults = {
        'for_delete' : False,
    }
