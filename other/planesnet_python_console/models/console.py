# -*- coding: utf-8 -*-
import sys
from openerp import models, fields, api, _
import logging

_logger = logging.getLogger(__name__)





class Console(models.Model):
    _name = 'python.console.script'
    _description = 'Console of python'

    @api.model
    def _default_code(self):
        m = """
# Odoo api 8.0
# Vars: _logger

cr = self.env.cr
uid = self.env.uid


obj = self.pool.get('res.parter')
ids = obj.search(cr,uid,[])
for p in obj.browse(cr,uid,ids):
    _logger.debug(p.name)
"""
        return m


    # Execute the script.
    @api.one
    def execute(self):

        if not self.active:
            _logger.info("The script %s is disabled. You can not run at this time." % self.name)
            return

        _logger.info("Running the script %s" % self.name)

        exec self.code

        _logger.info("The script %s, has completed successfully" % self.name)

    # fields.
    name = fields.Char("Name", default="Search all products")
    active = fields.Boolean("Active",default=True)
    code = fields.Text('Code', default=_default_code)
