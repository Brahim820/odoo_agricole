# -*- coding: utf-8 -*-

from odoo import models, fields, api


class PepiniereVariete(models.Model):
    _name = 'pepiniere.variete'
    _description = 'Variété de plante'
    _order = 'name'

    name = fields.Char(string='Nom de la variété', required=True)
    code = fields.Char(string='Code', required=True, copy=False)
    espece_id = fields.Many2one('pepiniere.espece', string='Espèce', required=True, ondelete='restrict')
    description = fields.Text(string='Description')
    image = fields.Binary(string='Image')
    
    # Caractéristiques
    rendement_moyen = fields.Float(string='Rendement moyen')
    resistance_maladies = fields.Text(string='Résistance aux maladies')
    particularites = fields.Text(string='Particularités')
    
    # Paramètres de production
    prix_vente_unitaire = fields.Float(string='Prix de vente unitaire')
    cout_production_unitaire = fields.Float(string='Coût de production unitaire')
    
    # Relations
    lot_ids = fields.One2many('pepiniere.lot.plant', 'variete_id', string='Lots')
    lot_count = fields.Integer(string='Nombre de lots', compute='_compute_lot_count')
    
    active = fields.Boolean(string='Actif', default=True)
    
    _sql_constraints = [
        ('code_unique', 'unique(code)', 'Le code de la variété doit être unique!')
    ]
    
    @api.depends('lot_ids')
    def _compute_lot_count(self):
        for record in self:
            record.lot_count = len(record.lot_ids)
