# -*- coding: utf-8 -*-

from odoo import models, fields, api


class PepinieireEspece(models.Model):
    _name = 'pepiniere.espece'
    _description = 'Espèce de plante'
    _order = 'name'

    name = fields.Char(string='Nom de l\'espèce', required=True)
    code = fields.Char(string='Code', required=True, copy=False)
    nom_scientifique = fields.Char(string='Nom scientifique')
    famille = fields.Char(string='Famille botanique')
    description = fields.Text(string='Description')
    image = fields.Binary(string='Image')
    
    # Caractéristiques culturales
    duree_germination = fields.Integer(string='Durée germination (jours)')
    duree_pepiniere = fields.Integer(string='Durée en pépinière (jours)')
    temperature_optimale = fields.Float(string='Température optimale (°C)')
    besoin_eau = fields.Selection([
        ('faible', 'Faible'),
        ('moyen', 'Moyen'),
        ('eleve', 'Élevé'),
    ], string='Besoin en eau')
    
    # Relations
    variete_ids = fields.One2many('pepiniere.variete', 'espece_id', string='Variétés')
    variete_count = fields.Integer(string='Nombre de variétés', compute='_compute_variete_count')
    
    active = fields.Boolean(string='Actif', default=True)
    
    _sql_constraints = [
        ('code_unique', 'unique(code)', 'Le code de l\'espèce doit être unique!')
    ]
    
    @api.depends('variete_ids')
    def _compute_variete_count(self):
        for record in self:
            record.variete_count = len(record.variete_ids)
