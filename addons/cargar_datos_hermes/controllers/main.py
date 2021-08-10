# -*- coding: utf-8 -*-

from openerp import tools
from openerp import models, fields, api
from openerp.osv import osv, expression

import logging
import json
_logger = logging.getLogger(__name__)

class LimpiezaHtml(models.Model):
    _name = 'limpieza.html'
    _description = 'Textos sin tags HTML'

    name = fields.Char(string='Identificador del valor')
    identificador_varios_1 = fields.Char(string='Identificador varios 1')
    identificador_varios_2 = fields.Char(string='Identificador varios 2')
    identificador_varios_3 = fields.Char(string='Identificador varios 3')
    modelo_origen = fields.Char(string='Modelo de datos origen')
    campo_origen = fields.Char(string='Campo del modelo de datos origen')
    texto_original = fields.Text(string='Texto original')
    texto_sin_html = fields.Text(string='Texto sin formato')

class TagsHtml(models.Model):
    _name = 'tags.html'
    _description = 'Listado de Tags HTML para filtrar'

    name = fields.Char(string='Tag HTML')
    cierre_tag = fields.Char(string='Cierre del tag')
    mantener_tag = fields.Boolean(string='¿Tag a mantener?')

class ProcesadorTextos(osv.osv):
    _name = 'process.texts.limpieza.html'
    _description = 'Procesador Textos Limpieza HTML'

    modelo = fields.Many2one('ir.model')
    campo = fields.Many2one('ir.model.fields', domain=[('model','=','product.product')])

    #Función que usaremos para obtener los valores de los textos indicados,
    #se pasarán como parámetros en la llamada el modelo y el campo, con ellos
    #recorreremos todos los valores "activos" que cumplan con su pertenencia
    #al modelo elegido y los crearemos en limpieza.html
    def procesar_textos(self, cr, uid, ids=False, context=None):
        LimpiezaHTML = self.pool.get('limpieza.html')

        if ids:
            obj_campo = self.pool.get('process.texts.limpieza.html').browse(cr, uid,ids)[0].campo

            if obj_campo:
                Modelo = self.pool.get('product.template')
                domain = [('website_published','=',True),('active','=',True)]
                modelos_ids = Modelo.search(cr, uid, domain, context=context)

                for modelos_ids in Modelo.browse(cr, uid, modelos_ids, context=context):
                    texto_origen = []
                    texto_final = []
                    tag = False
                    inicio_cortar = None
                    fin_cortar = None
                    if modelos_ids[obj_campo.name]:
                        texto_origen = modelos_ids[obj_campo.name]
                        texto_final = texto_origen
                        for i in range(0, len(texto_origen)):
                            if texto_origen[i] == '<':
                                tag = False
                                inicio_cortar = i
                            elif texto_origen[i] == '>':
                                tag = True
                                fin_cortar = i+1

                            if inicio_cortar != None and fin_cortar != None and tag:
                                domain = [('mantener_tag','=',True)]
                                htmltags_ids = self.pool.get('tags.html').search(cr, uid, domain, context=context)
                                for htmltags_ids in self.pool.get('tags.html').browse(cr, uid, htmltags_ids, context=context):
                                    if texto_origen[inicio_cortar:fin_cortar].find(htmltags_ids.name) == -1 and texto_origen[inicio_cortar:fin_cortar].find(htmltags_ids.cierre_tag) == -1:
                                        texto_final = texto_final.replace(texto_origen[inicio_cortar:fin_cortar], "")

                                inicio_cortar = None
                                fin_cortar = None

                    valor = {
                        'name':modelos_ids.name,
                        'identificador_varios_1':modelos_ids.brand_id.name,
                        'identificador_varios_2':modelos_ids.default_code,
                        'modelo_origen':'product.template',
                        'campo_origen':obj_campo.name,
                        'texto_original':texto_origen,
                        'texto_sin_html':texto_final
                    }
                    LimpiezaHTML.create(cr, uid, valor)

        return True
