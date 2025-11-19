# -*- coding: utf-8 -*-
{
    'name': "BSR Agriculture - Indicateurs Sol et Culture",
    'summary': """
        Gestion des analyses du sol et des cultures : physiques, chimiques et biologiques
    """,
    'description': """
        Module de gestion des indicateurs et analyses agricoles
        
        Ce module permet de gérer :
        * Analyses du sol (physiques, chimiques, biologiques)
        * Analyses des cultures et récoltes
        * Suivi des indicateurs de qualité
        * Recommandations et alertes
        * Intégration avec les parcelles et cultures
        
        Fonctionnalités principales :
        - Types d'analyses configurables
        - Paramètres d'analyse personnalisables
        - Résultats détaillés avec unités
        - Comparaison historique
        - Alertes automatiques
        - Rapports et tableaux de bord
        - Intégration complète avec bsr_agri_base
    """,
    'author': "BSR Agriculture",
    'website': "https://www.bsr-agriculture.com",
    'category': 'Agriculture/Management',
    'version': '15.0.1.0.0',
    'depends': [
        'base',
        'mail',
        'bsr_agri_base',
        'web',
    ],
    'data': [
        # Security
        'security/security.xml',
        'security/ir.model.access.csv',
        
        # Data
        'data/sequences.xml',
        
        # Views
        'views/analysis_type_views.xml',
        'views/analysis_parameter_views.xml',
        'views/soil_analysis_views.xml',
        'views/culture_analysis_views.xml',
        'views/analysis_alert_views.xml',
        'views/menus.xml',
    ],
    'installable': True,
    'application': False,
    'auto_install': False,
    'license': 'LGPL-3',
}