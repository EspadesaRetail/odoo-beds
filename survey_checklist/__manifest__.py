# -*- encoding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.
{
    'name': 'Surveys Checklist',
    'version': '3.0',
    'category': 'Marketing',
    'description': """
Adds to Survey basic module
==============================================
Create beautiful surveys and visualize answers
==============================================

It depends on the answers or reviews of some questions by different users. A
survey may have multiple pages. Each page may contain multiple questions and
each question may have multiple answers. Different users may give different
answers of question and according to that survey is done. Partners are also
sent mails with personal token for the invitation of the survey.
    """,
    'summary': 'Addons to Create surveys and analyze answers',
    'website': 'https://www.odoo.com/page/survey',
    'depends': ['http_routing', 'mail', 'survey'],
    'data': [
        'security/inherited_survey_security.xml',
        'security/ir.model.access.csv',
        'views/inherited_survey_views.xml',
    ],
    'installable': True,
    'auto_install': False,
    'application': True,
    'sequence': 106,
}
