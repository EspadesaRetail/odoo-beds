# -*- coding: utf-8 -*-
from openerp import api, tools, SUPERUSER_ID
from openerp.osv import osv, fields, expression
from openerp.tools.translate import _

import logging
_logger = logging.getLogger(__name__)


class product_group(osv.osv):
    _inherit = 'product.template'

    @api.one
    def _product_group_parent_recalculate(self, cr, uid, context):

        if len(self.product_group_ids)==0:
            return

        ir_attachment_obj = self.pool['ir.attachment']
        product_template_obj = self.pool['product.template']
        product_product_obj = self.pool['product.product']
        attribute_obj = self.pool['product.attribute']
        pal_obj = self.pool['product.attribute.line']
        pav_obj = self.pool['product.attribute.value']
        pai_obj = self.pool['product.attribute.image']

        # Datos principales
        self.write({
            'brand_id' : self.product_group_ids[0].brand_id.id,
            'public_categ_ids' : [(6,0,[x.id for x in self.product_group_ids[0].public_categ_ids])],
        })


        # Borrar todas las imágenes
        images_ids = ir_attachment_obj.search(cr,uid,[('res_model','=','product.template'),('res_id','=',self.id)])
        ir_attachment_obj.unlink(cr,uid,images_ids)

        values = []
        # Obtener las imágenes adicionales de los componentes
        if self.product_group_images:
            image_ids = ir_attachment_obj.search(cr,uid,[('res_model','=','product.template'),('res_id','in',[x.id for x in self.product_group_ids])])
            images = ir_attachment_obj.browse(cr,uid,image_ids)
            for image in images:
                ir_attachment_obj.create(cr,uid,{
                    'res_id' : self.id,
                    'name' : image.name,
                    'datas_fname' : image.datas_fname,
                    'res_model' : image.res_model,
                    'type' : image.type,
                    'datas' : image.datas,
                })

            # Añadir la imagen principal del componente, como imagen específica por atributo.
            for componente_id in self.product_group_ids:
                pai_id = pai_obj.search(cr, uid, [('product_tmpl_id','=',self.id),('value_id','=',componente_id.product_group_attribute_value_id.id)])
                if pai_id:
                    pai_obj.write(cr,uid,pai_id,{
                        'image' : componente_id.image,
                    })
                else:
                    pai_obj.create(cr,uid,{
                        'product_tmpl_id' : self.id,
                        'value_id' : componente_id.product_group_attribute_value_id.id,
                        'image' : componente_id.image,
                    })

        # Añadir el atributo que diferencia los compoenentes del grupo. Ej. color
        pal_id = pal_obj.search(cr, uid, [('product_tmpl_id', '=', self.id),('attribute_id','=',self.product_group_attribute_id.id)])
        if not pal_id:
            pal_id = pal_obj.create(cr, uid, {
                'product_tmpl_id' : self.id,
                'attribute_id' : self.product_group_attribute_id.id,
            })

        pal_obj.write(cr,uid,pal_id,{'value_ids': [(6,0,[x.product_group_attribute_value_id.id for x in self.product_group_ids])]})

        # Añadir el atributo en comun de los componentes (ej. Medidas)
        ids = pal_obj.search(cr, uid, [('product_tmpl_id', 'in', [x.id for x in self.product_group_ids])])
        pal_ids = pal_obj.browse(cr, uid, ids)
        attribute_ids = list(set([x.attribute_id for x in pal_ids]))
        if len(attribute_ids) != 1:
            """
            Los productos que forman el pack, solo pueden tener un atributo.
            """
            raise osv.except_osv(_('Warning!'), _('Los atributos de los componentes no coinciden'))
        attribute_id = attribute_ids[0]
        pal_id = pal_obj.search(cr, uid, [('product_tmpl_id', '=', self.id),('attribute_id','=',attribute_id.id)])
        if not pal_id:
            pal_id = pal_obj.create(cr, uid, {
                'product_tmpl_id' : self.id,
                'attribute_id' : attribute_id.id,
            })

        # Obtener los valores de los atributos de todos los componentes
        pal_ids = pal_obj.search(cr, uid, [('product_tmpl_id', 'in', [x.id for x in self.product_group_ids]),('attribute_id','=',attribute_id.id)])
        pal_ids = pal_obj.browse(cr, uid, pal_ids)

        value_ids = []
        for pal in pal_ids:
            value_ids += [x.id for x in pal.value_ids]
        value_ids = list(set(value_ids))
        pal_obj.write(cr,uid,pal_id,{'value_ids': [(6,0,value_ids)]})


        # Obtener las variantes de los componentes y crear o actualizas las variantes en producto agrupado.
        for componente_id in self.product_group_ids:
            product_ids = product_product_obj.search(cr, uid, [('product_tmpl_id', '=', componente_id.id)])
            product_ids = product_product_obj.browse(cr, uid, product_ids)

            # Crear las variantes del producto agrupado, copiando los datos de las variantes del componente.
            for variante in product_ids:
                attribute_value_ids = [componente_id.product_group_attribute_value_id.id]
                attribute_value_ids += [x.id for x in variante.attribute_value_ids]

                values = {
                    'product_tmpl_id' : self.id,
                    'product_group_product_id' : variante.id,
                    'name': self.name,
                    'default_code': self.default_code,
                    'ean13':variante.ean13,
                    'list_price' : 0,
                    'attribute_value_ids' : [(6,0,attribute_value_ids)],
                }

                product_id  = product_product_obj.search(cr, uid, [('product_tmpl_id', '=', self.id), ('product_group_product_id', '=', variante.id)])
                if product_id:
                    product_product_obj.write(cr,uid,product_id,values)
                else:
                    product_product_obj.create(cr,uid, values)

        # Borrar las variantes sin código de barras. excepto si sólo hay una ya que se borra el producto.
        if product_product_obj.search_count(cr, uid, [('product_tmpl_id', '=', self.id)]) > 1:
            product_ids = product_product_obj.search(cr, uid, [('product_tmpl_id', '=', self.id), ('ean13', '=', False)])
            if product_ids:
                product_product_obj.unlink(cr, uid, product_ids)






        # Obtener la imagen principal de los componentes
        """
        for product_id in self.product_group_ids:
            values.append({
                'res_id' : self.id,
                'name' : "%s-0" % product_id.default_code,
                'res_model' : 'product.template',
                'datas' : product_id.image,
            })

        """




    def product_group_recalculate(self, cr, uid, ids, context):
        for product in self.browse(cr, uid, ids, context=context):
            if product.product_group_id:
                product.product_group_id._product_group_parent_recalculate(cr,uid,context)

            if product.product_group_type == 1:
                product._product_group_parent_recalculate(cr,uid,context)
