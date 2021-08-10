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

# Limpiar los datos.
obj = odoo.env['sale.order']
ids = obj.search([])
orders = obj.browse(ids)
for order in orders:
    #print order.name
    order.beds_pedido = ''
    order.beds_estado = 0
    order.beds_fecha_entrega = ''
    order.beds_situacion = ''



# Inicializar los datos
obj = odoo.env['sale.order']
ids = obj.search([('name','in',['SO070','SO075','SO078'])])
orders = obj.browse(ids)

orders[0].beds_pedido = '441915'
orders[1].beds_pedido = '441911'
orders[2].beds_pedido = '441890'
    




