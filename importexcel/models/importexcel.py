# Copyright 2019 Alberto Calvo Bazco
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo.addons import decimal_precision as dp
from odoo.exceptions import UserError, ValidationError
from odoo import api, fields, models, _


class Importexcel(models.Model):

    _name = 'importexcel'
    _description = 'Import Excels'

    concatenar = fields.Char(string="Concatenar")
    companyia = fields.Char(string="Companyia")
    familia = fields.Char(string="Familia")
    marca = fields.Char(string="Marca")
    modelo = fields.Char(string="Modelo")
    presupuesto_ene = fields.Float(string="Ppto Ene")
    presupuesto_feb = fields.Float(string="Ppto Feb")
    presupuesto_mar = fields.Float(string="Ppto Mar")
    presupuesto_abr = fields.Float(string="Ppto Abr")
    presupuesto_may = fields.Float(string="Ppto May")
    presupuesto_jun = fields.Float(string="Ppto Jun")
    presupuesto_jul = fields.Float(string="Ppto Jul")
    presupuesto_ago = fields.Float(string="Ppto Ago")
    presupuesto_sep = fields.Float(string="Ppto Sep")
    presupuesto_oct = fields.Float(string="Ppto Oct")
    presupuesto_nov = fields.Float(string="Ppto Nov")
    presupuesto_dic = fields.Float(string="Ppto Dic")
    real_ene = fields.Float(string="Real Ene")
    real_feb = fields.Float(string="Real Feb")
    real_mar = fields.Float(string="Real Mar")
    real_abr = fields.Float(string="Real Abr")
    real_may = fields.Float(string="Real May")
    real_jun = fields.Float(string="Real Jun")
    real_jul = fields.Float(string="Real Jul")
    real_ago = fields.Float(string="Real Ago")
    real_sep = fields.Float(string="Real Sep")
    real_oct = fields.Float(string="Real Oct")
    real_nov = fields.Float(string="Real Nov")
    real_dic = fields.Float(string="Real Dic")

    # CREATE Functions
    @api.model
    def create(self, vals):
        for x in range(1, 12):
            mes = None
            objetivo = None
            real = None
            if x == 1:
                mes = '201801'
                objetivo = vals.get('presupuesto_ene')
                real = vals.get('real_ene')
            if x == 2:
                mes = '201802'
                objetivo = vals.get('presupuesto_feb')
                real = vals.get('real_feb')
            if x == 3:
                mes = '201803'
                objetivo = vals.get('presupuesto_mar')
                real = vals.get('real_mar')
            if x == 4:
                mes = '201804'
                objetivo = vals.get('presupuesto_abr')
                real = vals.get('real_abr')
            if x == 5:
                mes = '201805'
                objetivo = vals.get('presupuesto_may')
                real = vals.get('real_may')
            if x == 6:
                mes = '201806'
                objetivo = vals.get('presupuesto_jun')
                real = vals.get('real_jun')
            if x == 7:
                mes = '201807'
                objetivo = vals.get('presupuesto_jul')
                real = vals.get('real_jul')
            if x == 8:
                mes = '201808'
                objetivo = vals.get('presupuesto_ago')
                real = vals.get('real_ago')
            if x == 9:
                mes = '201809'
                objetivo = vals.get('presupuesto_sep')
                real = vals.get('real_sep')
            if x == 10:
                mes = '201810'
                objetivo = vals.get('presupuesto_oct')
                real = vals.get('real_oct')
            if x == 11:
                mes = '201811'
                objetivo = vals.get('presupuesto_nov')
                real = vals.get('real_nov')
            if x == 12:
                mes = '201812'
                objetivo = vals.get('presupuesto_dic')
                real = vals.get('real_dic')
            crear = {
                'mes': mes,
                'cia': vals.get("companyia"),
                'familia': vals.get("familia"),
                'marca': vals.get("marca"),
                'formato': vals.get("modelo"),
                'objetivo': objetivo,
                'real': real
            }
            self.env['exportexcel'].create(crear)
        return super(Importexcel, self).create(vals)


class Exportexcel(models.Model):

    _name = 'exportexcel'
    _description = 'Export Excels'

    mes = fields.Char(string="Mes")
    cia = fields.Char(string="Cia")
    familia = fields.Char(string="Familia")
    marca = fields.Char(string="Marca")
    formato = fields.Char(string="Formato")
    objetivo = fields.Float(string="Objetivo")
    real = fields.Float(string="Real")
