# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
{
    "name": "Product Pricelist",
    "summary":
        "Module to relate products to different pricelist.",
    "description": """
                      Allow to assing different prices to same products, relate
                      this prices and his tax to products and pricelist.
    """,
    "version": "12.0.1.0.0",
    "category": "Sales",
    "author": "Alberto Calvo Bazco <alberto.calvo@beds.es>",
    "license": "AGPL-3",
    "application": False,
    "installable": True,
    "depends": [
        "website_sale",
        "product",
        'account',
    ],
    'data': [
        "security/website_sale_product_pricelist_security.xml",
        "security/ir.model.access.csv",
        "views/inherited_product_pricelist_views.xml",
        "views/inherited_product_product_views.xml",
        "views/inherited_product_template_views.xml",
        "views/website_sale_product_pricelist_views.xml",
    ],
}
