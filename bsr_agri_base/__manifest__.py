# -*- coding: utf-8 -*-
{
    'name': 'BSR Agri Base',
    'version': '15.0.1.0.0',
    'category': 'Agriculture',
    'summary': 'Application de gestion des fermes, parcelles et cultures',
    'description': """
Application BSR Agriculture de Base
===================================

Cette application permet de gérer :
* Les fermes
* Les parcelles 
* Les cultures (maraîchage, pépinière, arboriculture, etc.)

Règles de gestion :
* Une ferme peut contenir plusieurs parcelles
* Une parcelle peut contenir une seule culture
    """,
    'author': 'BSR',
    'website': 'https://www.bsr.com',
    'depends': ['base', 'mail', 'maintenance', 'fleet', 'stock'],
    'data': [
        'security/security.xml',
        'security/ir.model.access.csv',
        'data/culture_type_data.xml',
        'data/farm_sequence_data.xml',
        'data/cron_data.xml',
        'views/farm_views.xml',
        'views/parcel_views.xml',
        'views/culture_views.xml',
        'views/culture_campaign_views.xml',
        'views/culture_type_views.xml',
        'views/irrigation_consumable_views.xml',
        'views/menu_views.xml',
    ],
    'installable': True,
    'auto_install': False,
    'application': True,
    'license': 'LGPL-3',
}