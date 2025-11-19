# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from odoo.exceptions import ValidationError
import logging

_logger = logging.getLogger(__name__)

class AgriTeam(models.Model):
    _name = 'bsr.agri.team'
    _description = 'Équipe Agricole'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _order = 'name'

    # Identification
    name = fields.Char('Nom de l\'équipe', required=True, tracking=True)
    code = fields.Char('Code de l\'équipe')
    description = fields.Text('Description')
    image_128 = fields.Image('Image', max_width=128, max_height=128)

    # Type et spécialisation
    team_type = fields.Selection([
        ('general', 'Équipe Générale'),
        ('seeding', 'Équipe Semis'),
        ('harvest', 'Équipe Récolte'),
        ('treatment', 'Équipe Traitement'),
        ('irrigation', 'Équipe Irrigation'),
        ('maintenance', 'Équipe Maintenance'),
        ('livestock', 'Équipe Élevage'),
        ('specialized', 'Équipe Spécialisée'),
    ], string='Type d\'équipe', required=True, default='general', tracking=True)

    # Hiérarchie
    leader_id = fields.Many2one(
        'hr.employee', 
        string='Chef d\'équipe',
        tracking=True,
        domain=[('active', '=', True)]
    )
    member_ids = fields.Many2many(
        'hr.employee',
        'bsr_agri_team_member_rel',
        'team_id',
        'employee_id',
        string='Membres de l\'équipe',
        domain=[('active', '=', True)]
    )
    member_count = fields.Integer('Nombre de membres', compute='_compute_member_count', store=True)

    # Compétences de l'équipe (basé sur hr_skills)
    required_skill_ids = fields.Many2many(
        'hr.skill',
        'bsr_team_required_skill_rel',
        'team_id',
        'skill_id',
        string='Compétences requises'
    )
    team_skill_ids = fields.Many2many(
        'hr.skill',
        string='Compétences de l\'équipe',
        compute='_compute_team_skills',
        store=False
    )

    # Période d'activité
    active_period = fields.Selection([
        ('year_round', 'Toute l\'année'),
        ('seasonal', 'Saisonnière'),
        ('project', 'Projet spécifique'),
        ('on_demand', 'À la demande'),
    ], string='Période d\'activité', default='year_round')

    start_date = fields.Date('Date de début')
    end_date = fields.Date('Date de fin')

    # Affectation géographique
    farm_ids = fields.Many2many(
        'bsr.farm',
        'bsr_team_farm_rel',
        'team_id',
        'farm_id',
        string='Fermes assignées'
    )

    # État et statut
    state = fields.Selection([
        ('draft', 'Brouillon'),
        ('active', 'Active'),
        ('inactive', 'Inactive'),
        ('seasonal', 'Saisonnière'),
        ('archived', 'Archivée'),
    ], string='État', default='draft', required=True, tracking=True)

    # Planification et charges
    max_concurrent_operations = fields.Integer('Max opérations simultanées', default=1)
    work_schedule = fields.Selection([
        ('morning', 'Matin (6h-14h)'),
        ('afternoon', 'Après-midi (14h-22h)'),
        ('full_day', 'Journée complète (6h-18h)'),
        ('night', 'Nuit (22h-6h)'),
        ('flexible', 'Flexible'),
    ], string='Horaire de travail', default='full_day')

    # Métriques et performance
    current_operations_count = fields.Integer(
        'Opérations en cours', 
        compute='_compute_current_operations'
    )
    total_operations_count = fields.Integer(
        'Total opérations', 
        compute='_compute_total_operations'
    )
    assignment_count = fields.Integer(
        'Nombre d\'affectations',
        compute='_compute_total_operations',
        store=False
    )
    avg_performance_rating = fields.Float(
        'Note moyenne de performance',
        compute='_compute_avg_performance',
        digits=(3, 1)
    )

    # Coûts
    hourly_cost = fields.Float('Coût horaire de l\'équipe', digits='Product Price')
    estimated_monthly_cost = fields.Float(
        'Coût mensuel estimé', 
        compute='_compute_estimated_cost',
        digits='Product Price'
    )

    # Méta-données
    active = fields.Boolean('Actif', default=True)
    company_id = fields.Many2one('res.company', default=lambda self: self.env.company)

    @api.depends('member_ids')
    def _compute_member_count(self):
        for team in self:
            team.member_count = len(team.member_ids)

    @api.depends('member_ids.employee_skill_ids.skill_id')
    def _compute_team_skills(self):
        for team in self:
            # Récupérer toutes les compétences des membres de l'équipe
            skills = self.env['hr.skill']
            for member in team.member_ids:
                skills |= member.employee_skill_ids.mapped('skill_id')
            team.team_skill_ids = skills

    def _compute_current_operations(self):
        for team in self:
            assignments = self.env['bsr.team.assignment'].search([
                ('team_id', '=', team.id),
                ('state', 'in', ['planned', 'in_progress'])
            ])
            team.current_operations_count = len(assignments)

    def _compute_total_operations(self):
        for team in self:
            assignments = self.env['bsr.team.assignment'].search([
                ('team_id', '=', team.id)
            ])
            team.total_operations_count = len(assignments)

    def _compute_avg_performance(self):
        for team in self:
            assignments = self.env['bsr.team.assignment'].search([
                ('team_id', '=', team.id),
                ('performance_rating', '>', 0)
            ])
            if assignments:
                team.avg_performance_rating = sum(assignments.mapped('performance_rating')) / len(assignments)
            else:
                team.avg_performance_rating = 0.0

    @api.depends('member_count', 'hourly_cost')
    def _compute_estimated_cost(self):
        for team in self:
            # Estimation basée sur 160h/mois par membre
            monthly_hours = 160 * team.member_count
            team.estimated_monthly_cost = monthly_hours * team.hourly_cost

    # Actions de workflow
    def action_activate(self):
        """Activer l'équipe"""
        for team in self:
            if team.state != 'draft':
                raise ValidationError(_('Seules les équipes en brouillon peuvent être activées.'))
            if not team.leader_id:
                raise ValidationError(_('Une équipe doit avoir un chef d\'équipe pour être activée.'))
            team.state = 'active'
            team.message_post(body=_('Équipe activée'))

    def action_deactivate(self):
        """Désactiver l'équipe"""
        for team in self:
            if team.state not in ['active', 'seasonal']:
                raise ValidationError(_('Seules les équipes actives ou saisonnières peuvent être désactivées.'))
            # Vérifier s'il n'y a pas d'opérations en cours
            if team.current_operations_count > 0:
                raise ValidationError(_('Impossible de désactiver une équipe avec des opérations en cours.'))
            team.state = 'inactive'
            team.message_post(body=_('Équipe désactivée'))

    def action_archive(self):
        """Archiver l'équipe"""
        for team in self:
            if team.current_operations_count > 0:
                raise ValidationError(_('Impossible d\'archiver une équipe avec des opérations en cours.'))
            team.state = 'archived'
            team.active = False
            team.message_post(body=_('Équipe archivée'))

    def action_view_assignments(self):
        """Voir les affectations de cette équipe"""
        self.ensure_one()
        action = self.env.ref('bsr_agri_rh.action_bsr_team_assignment').read()[0]
        action['domain'] = [('team_id', '=', self.id)]
        action['context'] = {'default_team_id': self.id}
        return action

    def action_seasonal_mode(self):
        """Passer en mode saisonnier"""
        for team in self:
            if team.state != 'active':
                raise ValidationError(_('Seules les équipes actives peuvent passer en mode saisonnier.'))
            team.state = 'seasonal'
            team.message_post(body=_('Équipe en mode saisonnier'))

    # Actions utilitaires
    def action_view_assignments(self):
        """Action pour voir les affectations de l'équipe"""
        self.ensure_one()
        return {
            'name': f'Affectations de {self.name}',
            'type': 'ir.actions.act_window',
            'res_model': 'bsr.team.assignment',
            'view_mode': 'tree,calendar,form',
            'domain': [('team_id', '=', self.id)],
            'context': {'default_team_id': self.id},
        }

    def action_view_members(self):
        """Action pour voir les membres de l'équipe"""
        self.ensure_one()
        return {
            'name': f'Membres de {self.name}',
            'type': 'ir.actions.act_window',
            'res_model': 'hr.employee',
            'view_mode': 'kanban,tree,form',
            'domain': [('id', 'in', self.member_ids.ids)],
        }

    # Validations
    @api.constrains('leader_id', 'member_ids')
    def _check_leader_in_members(self):
        for team in self:
            if team.leader_id and team.leader_id not in team.member_ids:
                team.member_ids = [(4, team.leader_id.id)]

    @api.constrains('start_date', 'end_date')
    def _check_dates(self):
        for team in self:
            if team.start_date and team.end_date:
                if team.start_date > team.end_date:
                    raise ValidationError(_('La date de début ne peut pas être postérieure à la date de fin.'))

    @api.constrains('max_concurrent_operations')
    def _check_max_operations(self):
        for team in self:
            if team.max_concurrent_operations < 1:
                raise ValidationError(_('Le nombre maximum d\'opérations simultanées doit être d\'au moins 1.'))

    @api.model
    def create(self, vals):
        if not vals.get('code'):
            vals['code'] = self.env['ir.sequence'].next_by_code('bsr.agri.team') or 'TEAM-NEW'
        return super().create(vals)

    def name_get(self):
        result = []
        for team in self:
            name = team.name
            if team.code:
                name = f"[{team.code}] {name}"
            if team.team_type:
                type_dict = dict(team._fields['team_type'].selection)
                name += f" ({type_dict.get(team.team_type, '')})"
            result.append((team.id, name))
        return result

    # Méthodes de recherche et recommandation
    def get_available_teams_for_operation(self, operation_type, required_skills=None, date_start=None, date_end=None):
        """Trouver les équipes disponibles pour un type d'opération"""
        domain = [
            ('state', '=', 'active'),
            ('current_operations_count', '<', self.max_concurrent_operations)
        ]
        
        # Filtrer par type si spécifique
        if operation_type in ['seeding', 'harvest', 'treatment', 'irrigation', 'maintenance']:
            domain.append(('team_type', 'in', [operation_type, 'general']))
        
        teams = self.search(domain)
        
        # Filtrer par compétences si requises
        if required_skills:
            teams = teams.filtered(lambda t: any(skill in t.team_skill_ids for skill in required_skills))
        
        return teams