# -*- coding: utf-8 -*-
{
    'name': 'BSR Gestion Pépinière Agricole',
    'version': '15.0.1.0.0',
    'category': 'Agriculture',
    'summary': 'Gestion complète de pépinière agricole',
    'description': """
        Gestion de Pépinière Agricole
        ==============================
        
        Fonctionnalités principales :
        * Gestion des cultures et plants (espèces, variétés, lots)
        * Suivi du cycle de vie des plants
        * Gestion des stocks (semences, substrats, intrants)
        * Traçabilité et contrôle qualité
        * Gestion commerciale (devis, commandes, facturation)
        * Gestion des ressources humaines et planning
        * Suivi financier et analyse des coûts
    """,
    'author': 'BSR',
    'website': 'https://www.bsr.ma',
    'depends': [
        'base',
        'stock',
        'sale_management',
        'purchase',
        'account',
        'hr',
        'product',
    ],
    'data': [
        'security/security.xml',
        'security/ir.model.access.csv',
        'data/sequence_data.xml',
        'views/espece_views.xml',
        'views/variete_views.xml',
        'views/intervention_views.xml',
        'views/stock_intrant_views.xml',
        'views/sale_order_views.xml',
        'views/lot_plant_views.xml',
        'views/menu_views.xml',
        'report/report_templates.xml',
        'report/report_views.xml',
    ],
    'installable': True,
    'application': True,
    'auto_install': False,
    'license': 'LGPL-3',
}
