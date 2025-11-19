# -*- coding: utf-8 -*-
{
    'name': 'BSR Agriculture Production',
    'version': '15.0.1.0.0',
    'category': 'Agriculture',
    'summary': 'Gestion complète de la production agricole - Écosystème BSR',
    'description': """
BSR Agriculture Production
==========================

Module complet de gestion de la production agricole intégré dans l'écosystème BSR.

Fonctionnalités principales :
* Planification des campagnes agricoles
* Gestion des cycles de production
* Suivi des activités culturales
* Enregistrement des récoltes
* Analyses de performance et rendements

Intégration BSR :
* Fermes, parcelles et cultures (bsr_agri_base)
* Analyses de sol et recommandations (bsr_agri_soil_indicator)
* Sessions d'irrigation et programmes (bsr_agri_irrigation)
    """,
    'author': 'BSR Agriculture',
    'website': 'https://bsr-agriculture.com',
    'license': 'LGPL-3',
    'depends': [
        'base',
        'mail', 
        'web',
        'bsr_agri_base',
        'bsr_agri_soil_indicator',
        'bsr_agri_irrigation',
    ],
    'data': [
        # Security
        'security/production_security.xml',
        'security/ir.model.access.csv',
        
        # Data
        'data/production_sequence.xml',
        'data/production_states.xml',
        
        # Views
        'views/production_campaign_views.xml',
        'views/production_cycle_views.xml',
        'views/production_menus.xml',
    ],
    'demo': [],
    'installable': True,
    'application': True,
    'auto_install': False,
    'external_dependencies': {
        'python': [],
        'bin': [],
    },
}