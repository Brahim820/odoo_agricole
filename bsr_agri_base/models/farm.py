# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from odoo.exceptions import ValidationError


class Farm(models.Model):
    _name = 'bsr.farm'
    _description = 'Ferme'
    _order = 'name'

    name = fields.Char('Nom de la ferme', required=True)
    code = fields.Char('Code de la ferme')
    description = fields.Text('Description')
    
    # Informations de contact
    partner_id = fields.Many2one('res.partner', string='Propriétaire/Exploitant')
    email = fields.Char('Email')
    phone = fields.Char('Téléphone')
    mobile = fields.Char('Mobile')
    
    # Adresse
    street = fields.Char('Rue')
    street2 = fields.Char('Rue 2')
    city = fields.Char('Ville')
    state_id = fields.Many2one('res.country.state', string='État/Région')
    zip = fields.Char('Code postal')
    country_id = fields.Many2one('res.country', string='Pays')
    
    # Informations techniques
    total_surface = fields.Float('Surface totale (hectares)', digits=(10, 2))
    cultivated_surface = fields.Float('Surface cultivée (hectares)', compute='_compute_cultivated_surface', store=True, digits=(10, 2))
    
    # Relations
    parcel_ids = fields.One2many('bsr.parcel', 'farm_id', string='Parcelles')
    parcel_count = fields.Integer('Nombre de parcelles', compute='_compute_parcel_count')
    
    # Relations avec les équipements
    equipment_ids = fields.One2many('maintenance.equipment', 'farm_id', string='Équipements de maintenance')
    equipment_count = fields.Integer('Nombre d\'équipements', compute='_compute_equipment_count')
    vehicle_ids = fields.One2many('fleet.vehicle', 'farm_id', string='Véhicules')
    vehicle_count = fields.Integer('Nombre de véhicules', compute='_compute_vehicle_count')
    irrigation_consumable_ids = fields.Many2many('bsr.irrigation.consumable', 'bsr_farm_irrigation_rel', 'farm_id', 'consumable_id', string='Consommables d\'irrigation')
    irrigation_consumable_count = fields.Integer('Nombre de consommables', compute='_compute_irrigation_consumable_count')
    
    # Statut
    active = fields.Boolean('Actif', default=True)
    state = fields.Selection([
        ('draft', 'Brouillon'),
        ('to_validate', 'À Valider'),
        ('validated', 'Validée'),
        ('operational', 'Opérationnelle'),
        ('suspended', 'Suspendue'),
        ('archived', 'Archivée'),
    ], string='État', default='draft', required=True, tracking=True)
    
    @api.depends('parcel_ids.surface')
    def _compute_cultivated_surface(self):
        for farm in self:
            farm.cultivated_surface = sum(farm.parcel_ids.mapped('surface'))
    
    @api.depends('parcel_ids')
    def _compute_parcel_count(self):
        for farm in self:
            farm.parcel_count = len(farm.parcel_ids)

    @api.depends('equipment_ids')
    def _compute_equipment_count(self):
        for farm in self:
            farm.equipment_count = len(farm.equipment_ids)

    @api.depends('vehicle_ids')
    def _compute_vehicle_count(self):
        for farm in self:
            farm.vehicle_count = len(farm.vehicle_ids)

    @api.depends('irrigation_consumable_ids')
    def _compute_irrigation_consumable_count(self):
        for farm in self:
            farm.irrigation_consumable_count = len(farm.irrigation_consumable_ids)

    # Contraintes
    @api.constrains('state')
    def _check_state_change(self):
        """Vérifier les conditions pour les changements d'état"""
        for farm in self:
            if farm.state == 'operational' and not farm.parcel_ids:
                raise ValidationError(_('Une ferme ne peut être opérationnelle sans parcelles.'))

    def unlink(self):
        """Empêcher la suppression si des parcelles sont liées"""
        for farm in self:
            if farm.parcel_ids:
                raise ValidationError(
                    _('Impossible de supprimer la ferme "%s" car elle contient %d parcelle(s). '
                      'Veuillez d\'abord supprimer ou déplacer toutes les parcelles.') % 
                    (farm.name, len(farm.parcel_ids))
                )
        return super().unlink()

    @api.model
    def create(self, vals):
        """Générer automatiquement un code de ferme si non fourni"""
        if not vals.get('code'):
            vals['code'] = self.env['ir.sequence'].next_by_code('bsr.farm.code') or 'FARM-NEW'
        return super().create(vals)

    # Méthodes de workflow
    def action_submit_for_validation(self):
        """Soumettre la ferme pour validation"""
        for farm in self:
            if not farm.name or not farm.total_surface:
                raise ValidationError(_('Veuillez remplir le nom de la ferme et sa surface totale avant de soumettre.'))
            farm.state = 'to_validate'

    def action_validate(self):
        """Valider la ferme"""
        for farm in self:
            if farm.state != 'to_validate':
                raise ValidationError(_('Seules les fermes "À Valider" peuvent être validées.'))
            farm.state = 'validated'

    def action_set_operational(self):
        """Rendre la ferme opérationnelle"""
        for farm in self:
            if farm.state != 'validated':
                raise ValidationError(_('Seules les fermes validées peuvent devenir opérationnelles.'))
            farm.state = 'operational'

    def action_suspend(self):
        """Suspendre la ferme"""
        for farm in self:
            if farm.state not in ['validated', 'operational']:
                raise ValidationError(_('Seules les fermes validées ou opérationnelles peuvent être suspendues.'))
            farm.state = 'suspended'

    def action_reactivate(self):
        """Réactiver la ferme"""
        for farm in self:
            if farm.state != 'suspended':
                raise ValidationError(_('Seules les fermes suspendues peuvent être réactivées.'))
            farm.state = 'operational' if farm.parcel_ids else 'validated'

    def action_archive(self):
        """Archiver la ferme"""
        for farm in self:
            if farm.state in ['draft', 'to_validate']:
                raise ValidationError(_('Les fermes en brouillon ou à valider ne peuvent pas être archivées.'))
            farm.state = 'archived'
            farm.active = False

    def action_reset_to_draft(self):
        """Remettre en brouillon"""
        for farm in self:
            if farm.state != 'to_validate':
                raise ValidationError(_('Seules les fermes "À Valider" peuvent être remises en brouillon.'))
            farm.state = 'draft'

    # Actions existantes

    def action_view_parcels(self):
        """Action pour voir les parcelles de la ferme"""
        self.ensure_one()
        return {
            'name': f'Parcelles de {self.name}',
            'type': 'ir.actions.act_window',
            'res_model': 'bsr.parcel',
            'view_mode': 'tree,form',
            'domain': [('farm_id', '=', self.id)],
            'context': {'default_farm_id': self.id},
        }

    def action_irrigation_consumable(self):
        """Action pour voir les consommables d'irrigation de la ferme"""
        self.ensure_one()
        return {
            'name': f'Consommables d\'irrigation - {self.name}',
            'type': 'ir.actions.act_window',
            'res_model': 'bsr.irrigation.consumable',
            'view_mode': 'kanban,tree,form',
            'domain': [('farm_ids', 'in', [self.id])],
            'context': {'default_farm_ids': [(4, self.id)]},
        }