# -*- coding: utf-8 -*-
from openerp import api, tools
from openerp.osv import osv, fields, expression
import base64
import sys
import os
from openerp.tools.translate import _


import logging
import json
_logger = logging.getLogger(__name__)

import openerp.addons.decimal_precision as dp

# Importar productos.
class external_products_import(osv.Model):
    _name = "external.product.import"
    _description = "External product"



    # Calcular el valor para las medidas.
    def get_attribute_values(self, p):
        medidas = False

        if p.ancho or p.largo:
            if p.ancho:
                medidas = p.ancho

            if p.largo:
                if medidas:
                    medidas +=  " x " + p.largo
                else:
                    medidas += p.largo

        else:
            if p.medidas:
                    medidas = p.medidas


        color = p.color
        piel = p.piel
        talla = p.talla



        return {
            'medidas': medidas,
            'color': color,
            'piel': piel,
        }

    # Actualizar niveles
    # product.public.category
    def product_public_category(self, cr, uid, context, external_product):
        # Nivel 1
        obj = self.pool.get('product.public.category')

        cond = []
        cond.append(('niveles','ilike',external_product.niveles))

        # Localizar la categoría púbblica.
        id = obj.search(cr,uid, cond)
        if id:
            return id[0]

        return False




    # Marca. product.brand
    def import_product_brand(self, cr, uid, context, external_product):
        obj = self.pool.get('product.brand')
        ids = obj.search(cr,uid,[('name','=',external_product.marca)])
        if ids:
            id = ids[0]
        else:
            id = obj.create(cr,uid,{'name':external_product.marca})
        return id

    def check_attribute(self, cr, uid, context, external_product, attribute_id, attribute_value, product_template_id, product_product_id):
        pro_obj = self.pool.get('product.product')
        pal_obj = self.pool.get('product.attribute.line')
        pal_vals = {
            'product_tmpl_id': product_template_id,
            'attribute_id': attribute_id,
        }

        pal_id = pal_obj.search(cr,uid,[('product_tmpl_id','=',product_template_id),
                            ('attribute_id','=',attribute_id)])

        if not pal_id:
            pal_id = pal_obj.create(cr,uid,pal_vals)


        pav_obj = self.pool.get('product.attribute.value')
        ids = pav_obj.search(cr,uid,[('attribute_id',"=",attribute_id),('name',"=",attribute_value)])
        if not ids:
            pav_id = pav_obj.create(cr,uid,{"attribute_id":attribute_id, "name":attribute_value})
        else:
            pav_id = ids[0]

        # Actualizar la relación de productos por medida.
        if pav_id and product_product_id:
            #pav_obj.write(cr,uid,pav_id, {'product_ids': [(4,product_product_id)]})
            pal_obj.write(cr,uid,pal_id,{'value_ids': [(4,pav_id)]})

        # Update attribute in product.product.
        pro_vals={}
        pro_vals['attribute_value_ids'] = [(4,pav_id)]

        # Update attribute in product.product.
        pro_obj.write(cr,uid,product_product_id, pro_vals)


        # Actualizar el precio.
        """
        if price_extra <> 0:
            pap_obj = self.pool.get('product.attribute.price')
            pap_ids = pap_obj.search(cr,uid, [('product_tmpl_id','=',product_template_id),('value_id','=',pav_id)])
            pap_vals = {'price_extra':price_extra}
            if pap_ids:
                pap_obj.write(cr,uid,pap_ids,pap_vals)
            else:
                pap_vals['product_tmpl_id'] = product_template_id
                pap_vals['value_id'] = pav_id
                pap_obj.create(cr,uid,pap_vals)
        """

        return {
            'pal_id':pal_id
        }



    def check_pricelist(self, cr, uid, context, external_product, product_product_id, version_xml_id):

            if external_product.precio1 > 0:
                base_id = self.pool['ir.model.data'].xmlid_to_res_id(cr, uid, 'product.list_price', raise_if_not_found=True)
                version_id = self.pool['ir.model.data'].xmlid_to_res_id(cr, uid, version_xml_id, raise_if_not_found=True)

                ppi_obj = self.pool.get('product.pricelist.item')
                ppi_vals = {
                    'price_version_id' : version_id,
                    'base' : base_id,
                    'product_id': product_product_id,
                    'product_price': external_product.precio1,
                    'product_discount': external_product.dto1,
                }

                ppi_ids = ppi_obj.search(cr,uid,[('price_version_id','=',version_id ),('product_id','=',product_product_id)])
                if ppi_ids:
                    ppi_obj.write(cr,uid,ppi_ids,ppi_vals)
                else:
                    ppi_obj.create(cr,uid,ppi_vals)


    # Importar un producto concreto y sus medidas.
    # Importar todos los productos externos.
    def import_data(self, cr, uid, ids, context=None):

        # Obtener el atributos
        obj = self.pool['ir.model.data']
        medidas_id = obj.xmlid_to_res_id(cr, uid, 'cs_model.product_attribute_measures', raise_if_not_found=True)
        color_id = obj.xmlid_to_res_id(cr, uid, 'cs_model.product_attribute_color', raise_if_not_found=True)
        skin_id = obj.xmlid_to_res_id(cr, uid, 'cs_model.product_attribute_skin', raise_if_not_found=True)

        obj = self.pool.get('external.product')
        ids = obj.search(cr,uid,[])
        external_products = obj.browse(cr,uid,ids,context=context)

        product_template_id = False
        referencia = False
        for external_product in external_products:

            try:
                product_public_category_id = self.product_public_category(cr,uid,context,external_product)

                # Sólo se procesan si la categoría es correcta.
                if not product_public_category_id:
                    _logger.warning("El producto no se puede importar, porque no tiene categoría publica establecida.")
                    continue

                # Si cambia la referencia hay que identificar de nuevo el product_template.
                if referencia <> external_product.referencia:
                    referencia = external_product.referencia
                    product_template_id = False

                # Verificar si ya existe el producto, a partir de la referencia.
                if not product_template_id:
                    product_template_obj = self.pool.get('product.template')
                    product_template_ids = product_template_obj.search(cr,uid, [('default_code','=',referencia)])

                    if len(product_template_ids)>1:
                        raise osv.except_osv(_('Warning!'), _('Existe más de un producto con la referencia: %s' % referencia))

                    if product_template_ids:
                        product_template_id = product_template_ids[0]

                # Actualizar el product.product.
                product_vals = {}
                product_product_id = None
                product_product_obj = self.pool.get('product.product')
                product_product_ids = product_product_obj.search(cr,uid, [('ean13','=',external_product.codigo_barras)])

                _logger.info("Importando la referencia %s / %s" % (referencia, external_product.codigo_barras))
                # Si no existe, creo la variante.
                if not product_product_ids:
                    product_product_vals = {
                        'name': external_product.nombre,
                        'default_code': external_product.referencia,
                        'ean13':external_product.codigo_barras,
                        'list_price' : 0,
                    }

                    # Si ya tiene product_template. lo asigno.
                    if product_template_id:
                        product_product_vals['product_tmpl_id'] = product_template_id

                    # crear el product.product
                    product_product_id = product_product_obj.create(cr,uid, product_product_vals)
                    _logger.debug("Creando la variante %s / %s" % (referencia, external_product.codigo_barras))


                else:
                    product_product_id = product_product_ids[0]

                # Si es necesario actualizo el product.template.
                if not product_template_id:
                    product_template_obj = self.pool.get('product.template')

                    # guardar el product_template_id
                    r = product_product_obj.read(cr,uid, product_product_id,['product_tmpl_id'])
                    product_template_id = r['product_tmpl_id'][0]

                    # Obtener el id de la marca.
                    product_brand_id = self.import_product_brand(cr,uid,context,external_product)

                    # Categorías (niveles) product.category
                    #product_category_id = self.import_product_category_nivel1(cr,uid,context,external_product)



                    # Actualizar product.template
                    product_template_vals = {
                        'name': external_product.nombre,
                        'default_code': external_product.referencia,
                        'brand_id' : product_brand_id,
                        'list_price' : 0,
    #                        'categ_id' : product_category_id,
                        'public_categ_ids' : [(4,product_public_category_id,)],


                        #'website_published' : True,  #TODO Quitar.



                    }

                    product_template_obj.write(cr,uid,product_template_id, product_template_vals)


                    # end update product.template



                gav = self.get_attribute_values(external_product)

                medidas = gav['medidas']
                color = gav['color']


                # Medidas
                if medidas:
                    self.check_attribute(cr,uid,context,external_product, medidas_id, medidas,product_template_id, product_product_id)

                # Color
                if color:
                    self.check_attribute(cr,uid,context,external_product, color_id, color,product_template_id, product_product_id)


                #self.check_pricelist(cr, uid, context, external_product, product_product_id, 'product.ver0')

                #external_product.write({'for_delete',1})
                external_product.unlink()

            except Exception:
                _logger.debug("Error en la importación del registro: " + str(external_product))
                continue


        # next external.product.
        return {'type': 'ir.actions.act_window_close'}

    def import_data_cancel(self, cr, uid, ids, context=None):
        return {'type': 'ir.actions.act_window_close'}




    """ Obsoleto. """

        # product.category
    def import_product_category_nivel1(self, cr, uid, context, external_product):
        # Nivel 1
        obj = self.pool.get('product.category')
        id = obj.search(cr,uid, [('name','=',external_product.nivel1)])
        if id:
            return id[0]
        else:
            pid = self.import_product_category_nivel2(cr, uid, context, external_product)
            id = obj.create(cr,uid,{'name':external_product.nivel1, 'parent_id':pid})

        return id

    def import_product_category_nivel2(self, cr, uid, context, external_product):
        # Nivel 2
        obj = self.pool.get('product.category')
        id = obj.search(cr,uid, [('name','=',external_product.nivel2)])
        if id:
            return id[0]
        else:
            pid = self.import_product_category_nivel3(cr, uid, context, external_product)
            id = obj.create(cr,uid,{'name':external_product.nivel2, 'parent_id':pid})

        return id

    def import_product_category_nivel3(self, cr, uid, context, external_product):
        # Nivel 3
        obj = self.pool.get('product.category')

        ids = obj.search(cr,uid, [('name','=',external_product.nivel3)])
        if ids:
            return ids[0]
        else:
            internal_category_id = self.pool['ir.model.data'].xmlid_to_res_id(cr, uid, 'cs_model.product_internal_category', raise_if_not_found=True)
            id = obj.create(cr,uid,{'name':external_product.nivel3, 'parent_id':internal_category_id})

        return id




#Importa las imágenes desde el directorio /mnt/beds al fichero de productos.
class external_image_product_import(osv.Model):
    _name = "external.product.image.import"
    def import_data(self, cr, uid, ids, context=None):


        def search_product(default_code):
            obj = self.pool.get('product.template')
            return obj.search(cr,uid,[('default_code', '=', default_code)])


        def search_image(name):
            obj = self.pool.get('ir.attachment')
            return obj.search(cr,uid,[('name', '=', name)])

        def write_img_optimize(model, ids, datos):
            obj = self.pool.get(model)
            for i in range(len(ids)):
                obj.write_img_optimize(cr,uid,ids[i],datos[i])
            return

        def create_img_optimize(model, datos):
            obj = self.pool.get(model)
            for dato in datos:
                obj.create_img_optimize(cr,uid,dato)
            return


        def process(file):

                file_path = '/mnt/beds/img/' + file;

                try:

                    msg = "not imported."
                    image_string = ""
                    name = file[:len(file)-4]

                    with open(file_path, "rb") as image:
                        image_string = base64.b64encode(image.read())

                    args1 = {
                        'image' : image_string,
                    }


                    # Split file name:




                    if "-" in name:
                        default_code,n = name.split("-")

                    else:
                        default_code, n  = name, 0

                    n = int(n)

                    # Search id for default_code.
                    ids = search_product(default_code)


                    if(len(ids)>0):
                        ok = False
                        if n == 0:
                            datos = [args1]
                            write_img_optimize('product.template',ids,datos)
                            ok = True
                            msg = "import main file."

                        else:


                            img_ids = search_image(name)

                            args1 = {
                                'name' : name,
                                'res_model' : 'product.template',
                                'res_id' : ids[0],
                                'datas' : image_string,
                                'type' : 'binary',
                                'file_type' : 'image/jpeg',
                                'datas_fname' : file,

                            }
                            datos = [args1]

                            if len(img_ids)>0:
                                write_img_optimize('ir.attachment',img_ids,datos)
                                #write('ir.attachment',img_ids,datos)
                                msg = "update image file: " + str(n)
                                ok = True
                            else:
                                create_img_optimize('ir.attachment',datos)
                                msg = "impor another file: " + str(n)
                                ok = True

                        # logging.
                        _logger.info(file + " " + msg)


                        # Move the img file to
                        if ok:
                            os.rename(file_path, '/mnt/beds/up/' + file)




                except Exception, e:
                        _logger.error("Error al importar %s %s" % (file_path,str(e)))


        files = os.listdir('/mnt/beds/img')

        for file in files:
            process(file)

        # next external.product.
        return {'type': 'ir.actions.act_window_close'}

    def import_data_cancel(self, cr, uid, ids, context=None):
        return {'type': 'ir.actions.act_window_close'}
