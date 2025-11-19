{
    'name': 'BSR Agri RH',
    'version': '15.0.1.0.0',
    'category': 'Agriculture/Human Resources',
    'summary': 'Gestion des équipes agricoles et affectations',
    'description': '''
Module de gestion RH agricole
=============================

Fonctionnalités :
* Gestion des équipes agricoles
* Compétences et spécialisations
* Affectation aux opérations
* Suivi des performances d'équipe
    ''',
    'author': 'BSR Agriculture',
    'website': 'https://www.bsr.com',
    'depends': [
        'bsr_agri_base',
        'bsr_agri_operation',
        'hr',
        'hr_skills',
        'mail',
    ],
    'data': [
        'security/ir.model.access.csv',
        'data/bsr_agri_rh_data.xml',
        'views/agri_skill_views.xml',
        'views/agri_team_views.xml',
        'views/team_assignment_views.xml',
        'views/menus.xml',
    ],
    'installable': True,
    'auto_install': False,
    'application': False,
    'license': 'LGPL-3',
}