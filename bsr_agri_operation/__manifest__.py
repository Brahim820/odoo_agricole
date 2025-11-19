{
    'name': 'BSR Agri Operation',
    'version': '15.0.1.0.0',
    'category': 'Agriculture',
    'summary': 'Gestion des opérations agricoles',
    'description': '''
Module de gestion des opérations agricoles
=========================================

Fonctionnalités :
* Planification des opérations de culture
* Suivi des interventions en temps réel
* Gestion des ressources (personnel, équipements)
* Analyses et reporting
    ''',
    'author': 'BSR Agriculture',
    'website': 'https://www.bsr.com',
    'depends': [
        'bsr_agri_base',
        'mail',
        'hr',
        'maintenance', 
        'fleet',
        'stock',
    ],
    'data': [
        'security/security.xml',
        'security/ir.model.access.csv',
        'data/operation_types_data.xml',
        'views/culture_operation_views.xml',
        'views/menu_views.xml',
    ],
    'installable': True,
    'auto_install': False,
    'application': False,
    'license': 'LGPL-3',
}