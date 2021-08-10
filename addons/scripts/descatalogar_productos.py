from myconfig import *
import odoorpc
import sys





if len(sys.argv)!=2:
    print ""
    print "Hay que indicar la lista de productos a descatalogoar separados por comas."
    print "Ejemplo:"
    print "->descatalogar_productos 11111,22222,333333"
    

# Prepare the connection to the server
print "Conectando a " + server +":" + str(port)
odoo = odoorpc.ODOO(host)

# Login
odoo.login(db, username, password)

references = str(sys.argv[1]).split(',')
    




# Use all methods of a model
obj = odoo.env['product.template']
ids = obj.search([('default_code','in',references)])

for product in obj.browse(ids):
    print product.name
    product.active = False
    
