# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from odoo.exceptions import ValidationError


class IrrigationSystem(models.Model):
    _name = 'bsr.irrigation.system'
    _description = 'Système d\'irrigation'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _order = 'name'

    name = fields.Char('Nom du système', required=True, tracking=True)
    code = fields.Char('Code', tracking=True)
    description = fields.Text('Description')
    
    # Type et caractéristiques techniques
    irrigation_type = fields.Selection([
        ('drip', 'Goutte-à-goutte'),
        ('sprinkler', 'Aspersion'),
        ('micro_spray', 'Micro-aspersion'),
        ('surface', 'Irrigation de surface'),
        ('subsurface', 'Irrigation souterraine'),
        ('center_pivot', 'Pivot central'),
        ('manual', 'Irrigation manuelle'),
    ], string='Type d\'irrigation', required=True, tracking=True)
    
    # Capacités techniques
    max_flow_rate = fields.Float('Débit maximum (L/h)', digits=(12, 2))
    max_pressure = fields.Float('Pression maximale (bar)', digits=(8, 2))
    coverage_area = fields.Float('Surface couverte (hectares)', digits=(10, 4))
    water_efficiency = fields.Float('Efficacité hydrique (%)', digits=(5, 2), default=85.0)
    
    # Localisation et équipements
    farm_id = fields.Many2one('bsr.farm', string='Ferme', required=True, tracking=True)
    equipment_id = fields.Many2one('maintenance.equipment', string='Équipement de maintenance')
    
    # Relations avec autres modèles
    zone_ids = fields.One2many('bsr.irrigation.zone', 'system_id', string='Zones d\'irrigation')
    zone_count = fields.Integer('Nombre de zones', compute='_compute_zone_count')
    
    # Consommables et coûts
    consumable_ids = fields.Many2many(
        'bsr.irrigation.consumable', 
        'irrigation_system_consumable_rel',
        'system_id', 'consumable_id',
        string='Consommables utilisés'
    )
    
    # État et maintenance
    state = fields.Selection([
        ('draft', 'Brouillon'),
        ('active', 'Actif'),
        ('maintenance', 'En maintenance'),
        ('broken', 'En panne'),
        ('suspended', 'Suspendu'),
        ('archived', 'Archivé'),
    ], string='État', default='draft', required=True, tracking=True)
    
    installation_date = fields.Date('Date d\'installation', tracking=True)
    last_maintenance_date = fields.Date('Dernière maintenance')
    next_maintenance_date = fields.Date('Prochaine maintenance', compute='_compute_next_maintenance_date', store=True)
    maintenance_frequency_days = fields.Integer('Fréquence maintenance (jours)', default=90)
    
    # Statistiques d'usage
    total_water_consumed = fields.Float('Eau consommée totale (L)', compute='_compute_usage_stats', store=True)
    total_operating_hours = fields.Float('Heures de fonctionnement', compute='_compute_usage_stats', store=True)
    session_count = fields.Integer('Nombre de sessions', compute='_compute_usage_stats', store=True)
    
    # Informations complémentaires
    active = fields.Boolean('Actif', default=True)
    notes = fields.Text('Notes')
    
    @api.depends('zone_ids')
    def _compute_zone_count(self):
        for system in self:
            system.zone_count = len(system.zone_ids)
    
    @api.depends('last_maintenance_date', 'maintenance_frequency_days')
    def _compute_next_maintenance_date(self):
        for system in self:
            if system.last_maintenance_date and system.maintenance_frequency_days:
                from datetime import timedelta
                system.next_maintenance_date = system.last_maintenance_date + timedelta(days=system.maintenance_frequency_days)
            else:
                system.next_maintenance_date = False
    
    @api.depends('zone_ids.session_ids')
    def _compute_usage_stats(self):
        for system in self:
            sessions = self.env['bsr.irrigation.session'].search([
                ('zone_id', 'in', system.zone_ids.ids),
                ('state', '=', 'completed')
            ])
            system.total_water_consumed = sum(sessions.mapped('water_consumed'))
            system.total_operating_hours = sum(sessions.mapped('duration_hours'))
            system.session_count = len(sessions)
    
    # Contraintes et validations
    @api.constrains('max_flow_rate', 'max_pressure', 'coverage_area')
    def _check_technical_specs(self):
        for system in self:
            if system.max_flow_rate and system.max_flow_rate <= 0:
                raise ValidationError(_('Le débit maximum doit être positif.'))
            if system.max_pressure and system.max_pressure <= 0:
                raise ValidationError(_('La pression maximale doit être positive.'))
            if system.coverage_area and system.coverage_area <= 0:
                raise ValidationError(_('La surface couverte doit être positive.'))
    
    @api.constrains('water_efficiency')
    def _check_water_efficiency(self):
        for system in self:
            if system.water_efficiency and not (0 <= system.water_efficiency <= 100):
                raise ValidationError(_('L\'efficacité hydrique doit être comprise entre 0 et 100%.'))
    
    # Méthodes de workflow
    def action_activate(self):
        """Activer le système d'irrigation"""
        for system in self:
            if system.state not in ['draft', 'suspended']:
                raise ValidationError(_('Seuls les systèmes en brouillon ou suspendus peuvent être activés.'))
            system.state = 'active'
    
    def action_suspend(self):
        """Suspendre le système d'irrigation"""
        for system in self:
            if system.state != 'active':
                raise ValidationError(_('Seuls les systèmes actifs peuvent être suspendus.'))
            system.state = 'suspended'
    
    def action_set_maintenance(self):
        """Mettre en maintenance"""
        for system in self:
            if system.state not in ['active', 'suspended']:
                raise ValidationError(_('Seuls les systèmes actifs ou suspendus peuvent être mis en maintenance.'))
            system.state = 'maintenance'
    
    def action_set_broken(self):
        """Marquer comme en panne"""
        for system in self:
            if system.state in ['archived']:
                raise ValidationError(_('Un système archivé ne peut pas être marqué en panne.'))
            system.state = 'broken'
    
    def action_archive(self):
        """Archiver le système"""
        for system in self:
            system.state = 'archived'
            system.active = False
    
    def action_reset_to_draft(self):
        """Remettre en brouillon"""
        for system in self:
            system.state = 'draft'
    
    # Actions métier
    def action_create_maintenance_request(self):
        """Créer une demande de maintenance"""
        self.ensure_one()
        if not self.equipment_id:
            # Créer automatiquement un équipement de maintenance si nécessaire
            equipment = self.env['maintenance.equipment'].create({
                'name': f'Système irrigation - {self.name}',
                'category_id': self._get_or_create_irrigation_category().id,
                'farm_id': self.farm_id.id if hasattr(self.farm_id, 'id') else False,
            })
            self.equipment_id = equipment.id
        
        return {
            'name': _('Demande de maintenance'),
            'type': 'ir.actions.act_window',
            'res_model': 'maintenance.request',
            'view_mode': 'form',
            'context': {
                'default_equipment_id': self.equipment_id.id,
                'default_name': f'Maintenance - {self.name}',
            },
            'target': 'new',
        }
    
    def action_view_zones(self):
        """Voir les zones d'irrigation"""
        self.ensure_one()
        return {
            'name': f'Zones - {self.name}',
            'type': 'ir.actions.act_window',
            'res_model': 'bsr.irrigation.zone',
            'view_mode': 'tree,form',
            'domain': [('system_id', '=', self.id)],
            'context': {'default_system_id': self.id},
        }
    
    def action_view_sessions(self):
        """Voir l'historique des sessions"""
        self.ensure_one()
        return {
            'name': f'Sessions - {self.name}',
            'type': 'ir.actions.act_window',
            'res_model': 'bsr.irrigation.session',
            'view_mode': 'tree,form',
            'domain': [('zone_id', 'in', self.zone_ids.ids)],
        }
    
    def _get_or_create_irrigation_category(self):
        """Obtenir ou créer la catégorie d'équipement irrigation"""
        category = self.env['maintenance.equipment.category'].search([
            ('name', '=', 'Irrigation')
        ], limit=1)
        if not category:
            category = self.env['maintenance.equipment.category'].create({
                'name': 'Irrigation',
            })
        return category
    
    @api.model
    def create(self, vals):
        """Générer automatiquement un code si non fourni"""
        if not vals.get('code'):
            vals['code'] = self.env['ir.sequence'].next_by_code('bsr.irrigation.system') or 'SYS-NEW'
        return super().create(vals)

    def name_get(self):
        """Format d'affichage personnalisé"""
        result = []
        for record in self:
            name = f"{record.name}"
            if record.code:
                name = f"[{record.code}] {name}"
            if record.irrigation_type:
                type_label = dict(record._fields['irrigation_type'].selection).get(record.irrigation_type)
                name += f" ({type_label})"
            result.append((record.id, name))
        return result