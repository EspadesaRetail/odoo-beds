# -*- coding: utf-8 -*-


from openerp import api, tools
from openerp.osv import osv, fields, expression

import logging
import json
_logger = logging.getLogger(__name__)


class update_data_country_state(osv.osv):
    _name = 'update.data.country.state'
    _description = 'Update Country State'

    # Permite marcar provincias que tengan tiendas cerradas como country_state_beds = False
    # a su vez, permite marcar provicias con tiendas abiertas como country_state_beds = True
    def set_country_state_beds(self, cr, uid, ids=False, context=None):
        # Primero recorremos las tiendas que están están publicadas y no están marcadas
        # como cerradas, con eso, guardamos un array de partner_ids que recorreremos para
        # usar como referencia de las provincias que tenemos que tener marcadas como visibles
        Partner = self.pool.get('res.partner')
        domain = [('beds_shop', '=', True),('beds_shop_closed','=',False),('website_published','=',True)]
        partner_ids = Partner.search(cr, uid, domain, context=context)
        partner_ids = Partner.browse(cr, uid, partner_ids, context=context)

        # Creamos una lista de provincias que tengan state_id relleno y actualizamos
        State = self.pool.get('res.country.state')
        provincias = [x.state_id.id for x in partner_ids]
        provincias = list(set(provincias))
        provincias = State.search(cr, uid, [('id','in',provincias)], context=context)

        if provincias:
            # Se establece el valor a introducir y se escribe
            valor = {
                'country_state_beds':True
            }
            provincias = State.write(cr, uid, provincias, valor)

        # Ahora recorremos todas las provincias que están marcadas como visibles
        # y empezamos a comprobar que tienen tiendas abiertas, publicadas y no
        # marcadas como cerradas, si cumplen no hacemos nada, si no, marcamos la
        # provincia como no visible
        domain = [('country_state_beds', '=', True)]
        provincias = State.search(cr, uid, domain, context=context)

        for provincia in State.browse(cr, uid, provincias, context=context):
            domain = [('state_id','=',provincia.id),('beds_shop', '=', True),('beds_shop_closed','=',False),('website_published','=',True)]
            partner_state = Partner.search(cr, uid, domain, context=context)
            partner_state = Partner.browse(cr, uid, partner_state, context=context)
            if not partner_state:
                # Se establece el valor a introducir y se escribe
                valor = {
                    'country_state_beds':False
                }
                State.write(cr, uid, provincia.id, valor)
