# -*- coding: utf-8 -*-

from odoo import models, fields, api, _

class HrSkill(models.Model):
    _inherit = 'hr.skill'

    # Catégorisation agricole
    skill_category = fields.Selection([
        ('general', 'Compétences Générales'),
        ('machinery', 'Machinisme Agricole'),
        ('crop_management', 'Gestion des Cultures'),
        ('livestock', 'Élevage'),
        ('irrigation', 'Irrigation'),
        ('pest_control', 'Lutte Phytosanitaire'),
        ('soil_management', 'Gestion des Sols'),
        ('harvest', 'Récolte'),
        ('safety', 'Sécurité Agricole'),
        ('quality_control', 'Contrôle Qualité'),
        ('technology', 'Technologies Agricoles'),
        ('management', 'Gestion et Leadership'),
    ], string='Catégorie Agricole')

    # Spécificité agricole
    is_agricultural_skill = fields.Boolean('Compétence Agricole', default=False)
    
    # Certifications requises
    requires_certification = fields.Boolean('Nécessite une certification')
    certification_validity_months = fields.Integer('Validité certification (mois)', default=12)
    
    # Opérations liées
    operation_type_ids = fields.Many2many(
        'bsr.culture.operation',
        string='Types d\'opérations',
        compute='_compute_related_operations',
        help='Opérations pour lesquelles cette compétence est utile'
    )
    
    # Niveau de risque
    risk_level = fields.Selection([
        ('low', 'Faible'),
        ('medium', 'Moyen'),
        ('high', 'Élevé'),
        ('critical', 'Critique'),
    ], string='Niveau de risque', default='low')

    # Compléments d'information
    prerequisites = fields.Text('Prérequis')
    training_duration_hours = fields.Integer('Durée formation (heures)')
    renewal_required = fields.Boolean('Renouvellement requis')

    @api.depends('name', 'skill_category')
    def _compute_related_operations(self):
        for skill in self:
            # Logic pour lier automatiquement aux opérations pertinentes
            # basé sur le nom et la catégorie de la compétence
            skill.operation_type_ids = False  # Sera implémenté plus tard


class HrSkillType(models.Model):
    _inherit = 'hr.skill.type'

    # Ajout de types spécifiques à l'agriculture
    is_agricultural = fields.Boolean('Type Agricole', default=False)
    color = fields.Integer('Couleur', help='Couleur pour l\'affichage dans les vues')


class HrEmployee(models.Model):
    _inherit = 'hr.employee'

    # Compétences agricoles spécifiques
    agricultural_skill_ids = fields.One2many(
        'hr.employee.skill',
        'employee_id',
        string='Compétences Agricoles',
        domain=[('skill_id.is_agricultural_skill', '=', True)]
    )
    
    # Certifications agricoles
    agricultural_certifications_count = fields.Integer(
        'Certifications Agricoles',
        compute='_compute_agricultural_certifications'
    )
    
    # Expérience agricole
    agricultural_experience_years = fields.Float('Années d\'expérience agricole')
    specialization_area = fields.Selection([
        ('crops', 'Cultures'),
        ('livestock', 'Élevage'),
        ('machinery', 'Machinisme'),
        ('irrigation', 'Irrigation'),
        ('management', 'Gestion'),
        ('quality', 'Qualité'),
        ('mixed', 'Polyvalent'),
    ], string='Domaine de spécialisation')

    # Équipes
    team_ids = fields.Many2many(
        'bsr.agri.team',
        'bsr_agri_team_member_rel',
        'employee_id',
        'team_id',
        string='Équipes'
    )
    led_team_ids = fields.One2many(
        'bsr.agri.team',
        'leader_id',
        string='Équipes dirigées'
    )

    # Disponibilité
    is_available_for_operations = fields.Boolean('Disponible pour opérations', default=True)
    max_concurrent_assignments = fields.Integer('Max affectations simultanées', default=1)

    @api.depends('employee_skill_ids.skill_id.is_agricultural_skill', 'employee_skill_ids.skill_id.requires_certification')
    def _compute_agricultural_certifications(self):
        for employee in self:
            certified_skills = employee.employee_skill_ids.filtered(
                lambda s: s.skill_id.is_agricultural_skill and s.skill_id.requires_certification
            )
            employee.agricultural_certifications_count = len(certified_skills)

    def action_view_agricultural_skills(self):
        """Action pour voir les compétences agricoles de l'employé"""
        self.ensure_one()
        return {
            'name': f'Compétences Agricoles - {self.name}',
            'type': 'ir.actions.act_window',
            'res_model': 'hr.employee.skill',
            'view_mode': 'tree,form',
            'domain': [
                ('employee_id', '=', self.id),
                ('skill_id.is_agricultural_skill', '=', True)
            ],
            'context': {
                'default_employee_id': self.id,
                'default_skill_id': False,
            },
        }

    def get_skill_level(self, skill_id):
        """Obtenir le niveau de compétence pour un skill donné"""
        skill_line = self.employee_skill_ids.filtered(lambda s: s.skill_id.id == skill_id)
        return skill_line.skill_level_id.name if skill_line else False


class HrEmployeeSkill(models.Model):
    _inherit = 'hr.employee.skill'

    # Informations spécifiques aux compétences agricoles
    certification_date = fields.Date('Date de certification')
    certification_expiry = fields.Date('Date d\'expiration', compute='_compute_expiry_date', store=True)
    certification_number = fields.Char('Numéro de certification')
    certified_by = fields.Char('Certifié par')
    
    # Statut de certification
    certification_status = fields.Selection([
        ('valid', 'Valide'),
        ('expiring_soon', 'Expire bientôt'),
        ('expired', 'Expirée'),
        ('not_required', 'Non requise'),
    ], string='Statut certification', compute='_compute_certification_status', store=True)

    # Notes et évaluations
    practical_notes = fields.Text('Notes pratiques')
    last_evaluation_date = fields.Date('Dernière évaluation')
    next_training_date = fields.Date('Prochaine formation')

    @api.depends('certification_date', 'skill_id.certification_validity_months')
    def _compute_expiry_date(self):
        for skill in self:
            if skill.certification_date and skill.skill_id.certification_validity_months:
                months = skill.skill_id.certification_validity_months
                # Ajouter les mois à la date de certification
                from dateutil.relativedelta import relativedelta
                skill.certification_expiry = skill.certification_date + relativedelta(months=months)
            else:
                skill.certification_expiry = False

    @api.depends('certification_expiry', 'skill_id.requires_certification')
    def _compute_certification_status(self):
        today = fields.Date.today()
        for skill in self:
            if not skill.skill_id.requires_certification:
                skill.certification_status = 'not_required'
            elif not skill.certification_expiry:
                skill.certification_status = 'expired'
            elif skill.certification_expiry < today:
                skill.certification_status = 'expired'
            elif (skill.certification_expiry - today).days <= 30:
                skill.certification_status = 'expiring_soon'
            else:
                skill.certification_status = 'valid'