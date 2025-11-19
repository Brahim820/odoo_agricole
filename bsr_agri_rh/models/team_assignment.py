# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from odoo.exceptions import ValidationError
from datetime import datetime, timedelta
import logging

_logger = logging.getLogger(__name__)

class TeamAssignment(models.Model):
    _name = 'bsr.team.assignment'
    _description = 'Affectation d\'Équipe'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _order = 'start_date desc, priority desc'

    # Identification
    name = fields.Char('Référence', readonly=True, default='/')
    priority = fields.Selection([
        ('0', 'Normale'),
        ('1', 'Importante'),
        ('2', 'Urgente'),
        ('3', 'Critique'),
    ], string='Priorité', default='0')

    # Relations principales
    team_id = fields.Many2one(
        'bsr.agri.team',
        string='Équipe',
        required=True,
        ondelete='cascade',
        tracking=True
    )
    operation_id = fields.Many2one(
        'bsr.culture.operation',
        string='Opération',
        required=True,
        ondelete='cascade',
        tracking=True
    )

    # Relations liées (pour faciliter les recherches)
    campaign_id = fields.Many2one(
        related='operation_id.campaign_id',
        string='Campagne',
        store=True,
        readonly=True
    )
    culture_id = fields.Many2one(
        related='operation_id.culture_id',
        string='Culture',
        store=True,
        readonly=True
    )
    farm_id = fields.Many2one(
        related='operation_id.farm_id',
        string='Ferme',
        store=True,
        readonly=True
    )
    parcel_id = fields.Many2one(
        related='operation_id.parcel_id',
        string='Parcelle',
        store=True,
        readonly=True
    )

    # Planification
    start_date = fields.Datetime('Date et heure de début', required=True, tracking=True)
    end_date = fields.Datetime('Date et heure de fin', required=True, tracking=True)
    duration_planned = fields.Float('Durée planifiée (heures)', compute='_compute_duration_planned', store=True)

    # Réalisation
    actual_start_date = fields.Datetime('Début effectif', tracking=True)
    actual_end_date = fields.Datetime('Fin effective', tracking=True)
    duration_actual = fields.Float('Durée réelle (heures)', compute='_compute_duration_actual', store=True)

    # État et workflow
    state = fields.Selection([
        ('draft', 'Brouillon'),
        ('planned', 'Planifiée'),
        ('confirmed', 'Confirmée'),
        ('in_progress', 'En cours'),
        ('paused', 'En pause'),
        ('completed', 'Terminée'),
        ('cancelled', 'Annulée'),
    ], string='État', default='draft', required=True, tracking=True)

    # Membres affectés
    assigned_member_ids = fields.Many2many(
        'hr.employee',
        'bsr_assignment_member_rel',
        'assignment_id',
        'employee_id',
        string='Membres affectés',
        domain="[('id', 'in', team_member_ids)]"
    )
    team_member_ids = fields.Many2many(
        related='team_id.member_ids',
        string='Membres de l\'équipe',
        readonly=True
    )
    member_count = fields.Integer('Nombre de membres affectés', compute='_compute_member_count')

    # Compétences
    required_skill_ids = fields.Many2many(
        'hr.skill',
        'bsr_assignment_skill_rel',
        'assignment_id',
        'skill_id',
        string='Compétences requises'
    )
    missing_skill_ids = fields.Many2many(
        'hr.skill',
        string='Compétences manquantes',
        compute='_compute_missing_skills'
    )
    skill_match_rate = fields.Float(
        'Taux de correspondance compétences (%)',
        compute='_compute_skill_match_rate'
    )

    # Performance et évaluation
    performance_rating = fields.Selection([
        ('1', 'Très mauvais'),
        ('2', 'Mauvais'),
        ('3', 'Moyen'),
        ('4', 'Bon'),
        ('5', 'Excellent'),
    ], string='Évaluation performance')
    
    quality_rating = fields.Selection([
        ('1', 'Très mauvais'),
        ('2', 'Mauvais'),
        ('3', 'Moyen'),
        ('4', 'Bon'),
        ('5', 'Excellent'),
    ], string='Évaluation qualité')

    # Coûts et ressources
    estimated_cost = fields.Float('Coût estimé', digits='Product Price')
    actual_cost = fields.Float('Coût réel', digits='Product Price')
    hourly_rate = fields.Float('Taux horaire équipe', related='team_id.hourly_cost', readonly=True)

    # Conditions de travail
    weather_conditions = fields.Text('Conditions météorologiques')
    work_conditions = fields.Text('Conditions de travail')
    safety_notes = fields.Text('Notes sécurité')

    # Équipements utilisés
    equipment_ids = fields.Many2many(
        'maintenance.equipment',
        string='Équipements utilisés'
    )
    vehicle_ids = fields.Many2many(
        'fleet.vehicle',
        string='Véhicules utilisés'
    )

    # Résultats et production
    work_area_covered = fields.Float('Surface travaillée (ha)', digits=(10, 4))
    production_quantity = fields.Float('Quantité produite')
    production_unit = fields.Many2one('uom.uom', string='Unité de mesure')

    # Notes et commentaires
    description = fields.Html('Description de l\'affectation')
    notes = fields.Text('Notes')
    team_feedback = fields.Text('Retour de l\'équipe')
    supervisor_notes = fields.Text('Notes superviseur')

    # Méta-données
    active = fields.Boolean('Actif', default=True)
    company_id = fields.Many2one('res.company', default=lambda self: self.env.company)

    # Champs calculés
    delay_hours = fields.Float('Retard (heures)', compute='_compute_delay')
    is_delayed = fields.Boolean('En retard', compute='_compute_delay')
    efficiency_rate = fields.Float('Taux d\'efficacité (%)', compute='_compute_efficiency_rate')

    @api.depends('start_date', 'end_date')
    def _compute_duration_planned(self):
        for assignment in self:
            if assignment.start_date and assignment.end_date:
                delta = assignment.end_date - assignment.start_date
                assignment.duration_planned = delta.total_seconds() / 3600.0
            else:
                assignment.duration_planned = 0.0

    @api.depends('actual_start_date', 'actual_end_date')
    def _compute_duration_actual(self):
        for assignment in self:
            if assignment.actual_start_date and assignment.actual_end_date:
                delta = assignment.actual_end_date - assignment.actual_start_date
                assignment.duration_actual = delta.total_seconds() / 3600.0
            else:
                assignment.duration_actual = 0.0

    @api.depends('assigned_member_ids')
    def _compute_member_count(self):
        for assignment in self:
            assignment.member_count = len(assignment.assigned_member_ids)

    @api.depends('required_skill_ids', 'assigned_member_ids')
    def _compute_missing_skills(self):
        for assignment in self:
            if not assignment.required_skill_ids or not assignment.assigned_member_ids:
                assignment.missing_skill_ids = False
                continue

            # Compétences disponibles dans l'équipe
            available_skills = self.env['hr.skill']
            for member in assignment.assigned_member_ids:
                available_skills |= member.employee_skill_ids.mapped('skill_id')

            # Compétences manquantes
            missing = assignment.required_skill_ids - available_skills
            assignment.missing_skill_ids = missing

    @api.depends('required_skill_ids', 'missing_skill_ids')
    def _compute_skill_match_rate(self):
        for assignment in self:
            if not assignment.required_skill_ids:
                assignment.skill_match_rate = 100.0
            else:
                required_count = len(assignment.required_skill_ids)
                missing_count = len(assignment.missing_skill_ids)
                matched_count = required_count - missing_count
                assignment.skill_match_rate = (matched_count / required_count) * 100.0

    @api.depends('end_date', 'actual_end_date', 'state')
    def _compute_delay(self):
        now = fields.Datetime.now()
        for assignment in self:
            if assignment.state in ['completed'] and assignment.actual_end_date and assignment.end_date:
                # Calculer le retard par rapport à la date planifiée
                delta = assignment.actual_end_date - assignment.end_date
                assignment.delay_hours = delta.total_seconds() / 3600.0
                assignment.is_delayed = delta.total_seconds() > 0
            elif assignment.state in ['in_progress', 'confirmed', 'planned'] and assignment.end_date:
                # Vérifier si on est en retard par rapport au planning
                delta = now - assignment.end_date
                assignment.delay_hours = max(0, delta.total_seconds() / 3600.0)
                assignment.is_delayed = now > assignment.end_date
            else:
                assignment.delay_hours = 0.0
                assignment.is_delayed = False

    @api.depends('duration_planned', 'duration_actual')
    def _compute_efficiency_rate(self):
        for assignment in self:
            if assignment.duration_actual and assignment.duration_planned:
                assignment.efficiency_rate = (assignment.duration_planned / assignment.duration_actual) * 100.0
            else:
                assignment.efficiency_rate = 0.0

    # Actions de workflow
    def action_plan(self):
        """Planifier l'affectation"""
        for assignment in self:
            if assignment.state != 'draft':
                raise ValidationError(_('Seules les affectations en brouillon peuvent être planifiées.'))
            assignment.state = 'planned'
            assignment.message_post(body=_('Affectation planifiée'))

    def action_confirm(self):
        """Confirmer l'affectation"""
        for assignment in self:
            if assignment.state != 'planned':
                raise ValidationError(_('Seules les affectations planifiées peuvent être confirmées.'))
            if not assignment.assigned_member_ids:
                raise ValidationError(_('Au moins un membre doit être affecté.'))
            assignment.state = 'confirmed'
            assignment.message_post(body=_('Affectation confirmée'))

    def action_start(self):
        """Démarrer l'affectation"""
        for assignment in self:
            if assignment.state != 'confirmed':
                raise ValidationError(_('Seules les affectations confirmées peuvent être démarrées.'))
            assignment.state = 'in_progress'
            if not assignment.actual_start_date:
                assignment.actual_start_date = fields.Datetime.now()
            assignment.message_post(body=_('Affectation démarrée'))

    def action_pause(self):
        """Mettre en pause l'affectation"""
        for assignment in self:
            if assignment.state != 'in_progress':
                raise ValidationError(_('Seules les affectations en cours peuvent être mises en pause.'))
            assignment.state = 'paused'
            assignment.message_post(body=_('Affectation mise en pause'))

    def action_resume(self):
        """Reprendre l'affectation"""
        for assignment in self:
            if assignment.state != 'paused':
                raise ValidationError(_('Seules les affectations en pause peuvent être reprises.'))
            assignment.state = 'in_progress'
            assignment.message_post(body=_('Affectation reprise'))

    def action_complete(self):
        """Terminer l'affectation"""
        for assignment in self:
            if assignment.state not in ['in_progress', 'paused']:
                raise ValidationError(_('L\'affectation doit être en cours ou en pause pour être terminée.'))
            assignment.state = 'completed'
            if not assignment.actual_end_date:
                assignment.actual_end_date = fields.Datetime.now()
            assignment.message_post(body=_('Affectation terminée'))

    def action_cancel(self):
        """Annuler l'affectation"""
        for assignment in self:
            if assignment.state in ['completed']:
                raise ValidationError(_('Une affectation terminée ne peut pas être annulée.'))
            assignment.state = 'cancelled'
            assignment.message_post(body=_('Affectation annulée'))

    # Contraintes et validations
    @api.constrains('start_date', 'end_date')
    def _check_dates(self):
        for assignment in self:
            if assignment.start_date and assignment.end_date:
                if assignment.start_date >= assignment.end_date:
                    raise ValidationError(_('La date de début doit être antérieure à la date de fin.'))

    @api.constrains('actual_start_date', 'actual_end_date')
    def _check_actual_dates(self):
        for assignment in self:
            if assignment.actual_start_date and assignment.actual_end_date:
                if assignment.actual_start_date >= assignment.actual_end_date:
                    raise ValidationError(_('La date de début effective doit être antérieure à la date de fin effective.'))

    @api.constrains('team_id', 'start_date', 'end_date')
    def _check_team_availability(self):
        for assignment in self:
            if assignment.state in ['confirmed', 'in_progress'] and assignment.team_id:
                # Vérifier les conflits de planning
                conflicting = self.search([
                    ('team_id', '=', assignment.team_id.id),
                    ('id', '!=', assignment.id),
                    ('state', 'in', ['confirmed', 'in_progress']),
                    '|',
                    '&', ('start_date', '<=', assignment.start_date), ('end_date', '>', assignment.start_date),
                    '&', ('start_date', '<', assignment.end_date), ('end_date', '>=', assignment.end_date),
                ])
                if conflicting:
                    raise ValidationError(_('L\'équipe %s est déjà affectée durant cette période.') % assignment.team_id.name)

    @api.model
    def create(self, vals):
        if vals.get('name', '/') == '/':
            vals['name'] = self.env['ir.sequence'].next_by_code('bsr.team.assignment') or '/'
        return super().create(vals)

    def name_get(self):
        result = []
        for assignment in self:
            name = f"{assignment.name} - {assignment.team_id.name}"
            if assignment.operation_id:
                name += f" / {assignment.operation_id.name}"
            result.append((assignment.id, name))
        return result

    # Méthodes utilitaires
    def auto_assign_members(self):
        """Affecter automatiquement les membres avec les bonnes compétences"""
        for assignment in self:
            if assignment.required_skill_ids and assignment.team_id.member_ids:
                suitable_members = self.env['hr.employee']
                
                for member in assignment.team_id.member_ids:
                    member_skills = member.employee_skill_ids.mapped('skill_id')
                    if any(skill in member_skills for skill in assignment.required_skill_ids):
                        suitable_members |= member
                
                assignment.assigned_member_ids = suitable_members

    def get_recommended_members(self):
        """Obtenir une recommandation de membres pour cette affectation"""
        self.ensure_one()
        if not self.required_skill_ids or not self.team_id.member_ids:
            return self.team_id.member_ids

        # Scorer chaque membre selon ses compétences
        member_scores = []
        for member in self.team_id.member_ids:
            score = 0
            member_skills = member.employee_skill_ids.mapped('skill_id')
            
            for required_skill in self.required_skill_ids:
                if required_skill in member_skills:
                    # Bonus selon le niveau de compétence
                    skill_line = member.employee_skill_ids.filtered(lambda s: s.skill_id == required_skill)
                    if skill_line and skill_line[0].skill_level_id:
                        score += skill_line[0].skill_level_id.level_progress / 100.0
                    else:
                        score += 0.5  # Score par défaut si pas de niveau
            
            member_scores.append((member, score))
        
        # Trier par score décroissant
        member_scores.sort(key=lambda x: x[1], reverse=True)
        return [member for member, score in member_scores]