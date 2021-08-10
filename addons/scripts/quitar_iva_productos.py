from myconfig import *
import odoorpc

# Prepare the connection to the server
odoo = odoorpc.ODOO(server, port=port)

# Login
odoo.login(db, username, password)

# Current user
user = odoo.env.user
print(user.name)            # name of the user connected
print(user.company_id.name) # the name of its company

# Simple 'raw' query
#user_data = odoo.execute('res.users', 'read', [user.id])
#print(user_data)

# Use all methods of a model
obj = odoo.env['product.template']
ids = obj.search([])

for product in obj.browse(ids):
    print(product.name)
    
    product.taxes_id = None
    product.supplier_taxes_id = None
