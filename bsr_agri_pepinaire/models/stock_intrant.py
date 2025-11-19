# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from odoo.exceptions import ValidationError


class PepiniereIntrant(models.Model):
    _name = 'pepiniere.intrant'
    _description = 'Intrant de pépinière'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _order = 'name'

    name = fields.Char(string='Nom', required=True, tracking=True)
    code = fields.Char(string='Code', copy=False)
    
    # Catégorie
    categorie = fields.Selection([
        ('semence', 'Semence'),
        ('substrat', 'Substrat'),
        ('engrais', 'Engrais'),
        ('phytosanitaire', 'Produit phytosanitaire'),
        ('pot', 'Pot/Contenant'),
        ('autre', 'Autre'),
    ], string='Catégorie', required=True, tracking=True)
    
    # Informations produit
    description = fields.Text(string='Description')
    fournisseur_id = fields.Many2one('res.partner', string='Fournisseur', 
                                      domain="[('supplier_rank', '>', 0)]")
    
    # Unités et stock
    unite = fields.Selection([
        ('kg', 'Kilogramme'),
        ('l', 'Litre'),
        ('unite', 'Unité'),
        ('sac', 'Sac'),
        ('boite', 'Boîte'),
    ], string='Unité', required=True, default='unite')
    
    stock_actuel = fields.Float(string='Stock actuel', compute='_compute_stock', store=True)
    stock_minimum = fields.Float(string='Stock minimum', default=0.0)
    stock_alerte = fields.Boolean(string='Alerte stock', compute='_compute_stock_alerte', store=True)
    
    # Prix
    prix_unitaire = fields.Float(string='Prix unitaire')
    devise_id = fields.Many2one('res.currency', string='Devise', 
                                 default=lambda self: self.env.company.currency_id)
    
    # Relations
    mouvement_ids = fields.One2many('pepiniere.mouvement.intrant', 'intrant_id', string='Mouvements')
    
    active = fields.Boolean(string='Actif', default=True)
    
    @api.depends('mouvement_ids.quantite', 'mouvement_ids.type_mouvement')
    def _compute_stock(self):
        for record in self:
            entrees = sum(record.mouvement_ids.filtered(lambda m: m.type_mouvement == 'entree').mapped('quantite'))
            sorties = sum(record.mouvement_ids.filtered(lambda m: m.type_mouvement == 'sortie').mapped('quantite'))
            record.stock_actuel = entrees - sorties
    
    @api.depends('stock_actuel', 'stock_minimum')
    def _compute_stock_alerte(self):
        for record in self:
            record.stock_alerte = record.stock_actuel <= record.stock_minimum


class PepiniereMouvementIntrant(models.Model):
    _name = 'pepiniere.mouvement.intrant'
    _description = 'Mouvement d\'intrant'
    _order = 'date desc'

    name = fields.Char(string='Référence', required=True, copy=False, readonly=True, default='/')
    intrant_id = fields.Many2one('pepiniere.intrant', string='Intrant', required=True, ondelete='cascade')
    date = fields.Date(string='Date', required=True, default=fields.Date.today)
    
    type_mouvement = fields.Selection([
        ('entree', 'Entrée'),
        ('sortie', 'Sortie'),
    ], string='Type', required=True)
    
    quantite = fields.Float(string='Quantité', required=True)
    unite = fields.Selection(related='intrant_id.unite', string='Unité', readonly=True)
    
    # Origine/Destination
    origine = fields.Char(string='Origine/Destination')
    lot_id = fields.Many2one('pepiniere.lot.plant', string='Lot concerné')
    
    # Coût
    cout_unitaire = fields.Float(string='Coût unitaire')
    cout_total = fields.Float(string='Coût total', compute='_compute_cout_total', store=True)
    
    notes = fields.Text(string='Notes')
    
    @api.model
    def create(self, vals):
        if vals.get('name', '/') == '/':
            vals['name'] = self.env['ir.sequence'].next_by_code('pepiniere.mouvement.intrant') or '/'
        return super(PepiniereMouvementIntrant, self).create(vals)
    
    @api.depends('quantite', 'cout_unitaire')
    def _compute_cout_total(self):
        for record in self:
            record.cout_total = record.quantite * record.cout_unitaire
