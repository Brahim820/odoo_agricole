# -*- coding: utf-8 -*-
{
    'name': 'BSR Agri Irrigation',
    'version': '15.0.1.0.0',
    'category': 'Agriculture',
    'summary': 'Système de gestion d\'irrigation intelligent pour l\'agriculture',
    'description': """
BSR Agri Irrigation - Gestion intelligente de l'irrigation
=========================================================

Ce module permet de gérer de manière intelligente l'irrigation des cultures avec :

**Fonctionnalités principales :**
* Gestion des systèmes d'irrigation (goutte-à-goutte, aspersion, micro-aspersion)
* Planification automatisée des programmes d'irrigation
* Division des parcelles en zones d'irrigation
* Suivi et enregistrement des sessions d'irrigation
* Saisie manuelle des données d'irrigation et conditions météo
* Système d'alerte pour pannes et problèmes d'équipement
* Optimisation basée sur les analyses du sol et historique
* Rapports complets de consommation et efficacité

**Integration avec les modules BSR :**
* Fermes et parcelles (bsr_agri_base)
* Analyses du sol (bsr_agri_soil_indicator) 
* Cultures et campagnes agricoles
* Gestion des équipements et maintenance
* Stocks et consommables d'irrigation

**Workflows automatisés :**
* Planification selon les conditions enregistrées
* Ajustement des programmes selon l'humidité du sol analysée
* Alertes pour la maintenance préventive
* Optimisation de la consommation d'eau basée sur l'historique

**Rapports et analyses :**
* Consommation d'eau par parcelle/culture
* Efficacité des systèmes d'irrigation
* Coûts et ROI des investissements irrigation
* Tendances et prévisions
    """,
    'author': 'BSR',
    'website': 'https://www.bsr.com',
    'depends': [
        'base', 
        'mail', 
        'web', 
        'maintenance', 
        'stock',
        'bsr_agri_base',
        'bsr_agri_soil_indicator'
    ],
    'data': [
        'security/security.xml',
        'security/ir.model.access.csv',
        'data/irrigation_sequences.xml',
        'data/irrigation_data.xml',
        'views/irrigation_system_views.xml',
        'views/irrigation_zone_views.xml',
        'views/irrigation_program_views.xml',
        'views/irrigation_session_views.xml',
        'views/irrigation_alert_views.xml',
        'views/menus.xml',
        'reports/reports.xml',
        'reports/irrigation_session_report.xml',
        'reports/irrigation_program_report.xml',
        'reports/irrigation_alert_report.xml',
        'reports/irrigation_system_zone_reports.xml',
        'reports/irrigation_performance_report.xml',
    ],
    'installable': True,
    'auto_install': False,
    'application': True,
    'license': 'LGPL-3',
    'sequence': 100,
}