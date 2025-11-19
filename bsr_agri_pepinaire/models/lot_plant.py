# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from odoo.exceptions import ValidationError


class PepiniereLotPlant(models.Model):
    _name = 'pepiniere.lot.plant'
    _description = 'Lot de plants'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _order = 'date_semis desc'

    name = fields.Char(string='Référence', required=True, copy=False, readonly=True, default='/')
    espece_id = fields.Many2one('pepiniere.espece', string='Espèce', required=True, tracking=True)
    variete_id = fields.Many2one('pepiniere.variete', string='Variété', required=True, tracking=True, 
                                  domain="[('espece_id', '=', espece_id)]")
    
    # Dates et cycle de vie
    date_semis = fields.Date(string='Date de semis', required=True, default=fields.Date.today, tracking=True)
    date_germination = fields.Date(string='Date de germination', tracking=True)
    date_repiquage = fields.Date(string='Date de repiquage', tracking=True)
    date_sortie_prevue = fields.Date(string='Date de sortie prévue', compute='_compute_date_sortie_prevue', store=True)
    date_sortie_reelle = fields.Date(string='Date de sortie réelle', tracking=True)
    
    # Quantités
    quantite_semis = fields.Integer(string='Quantité semée', required=True, tracking=True)
    quantite_germee = fields.Integer(string='Quantité germée', tracking=True)
    quantite_repiquee = fields.Integer(string='Quantité repiquée', tracking=True)
    quantite_disponible = fields.Integer(string='Quantité disponible', compute='_compute_quantite_disponible', 
                                          store=True, tracking=True)
    quantite_vendue = fields.Integer(string='Quantité vendue', compute='_compute_quantite_vendue', store=True)
    taux_germination = fields.Float(string='Taux de germination (%)', compute='_compute_taux_germination', store=True)
    
    # Localisation
    emplacement = fields.Char(string='Emplacement')
    serre_id = fields.Many2one('pepiniere.serre', string='Serre')
    
    # État
    state = fields.Selection([
        ('semis', 'Semis'),
        ('germination', 'Germination'),
        ('repiquage', 'Repiquage'),
        ('croissance', 'Croissance'),
        ('pret', 'Prêt à vendre'),
        ('vendu', 'Vendu'),
        ('cloture', 'Clôturé'),
    ], string='État', default='semis', required=True, tracking=True)
    
    # Coûts et prix
    cout_total = fields.Float(string='Coût total', compute='_compute_cout_total', store=True)
    cout_unitaire = fields.Float(string='Coût unitaire', compute='_compute_cout_unitaire', store=True)
    prix_vente_unitaire = fields.Float(string='Prix de vente unitaire', related='variete_id.prix_vente_unitaire')
    
    # Relations
    intervention_ids = fields.One2many('pepiniere.intervention', 'lot_id', string='Interventions')
    sale_line_ids = fields.One2many('sale.order.line', 'lot_plant_id', string='Lignes de vente')
    
    # Notes
    notes = fields.Text(string='Notes')
    
    active = fields.Boolean(string='Actif', default=True)
    
    @api.model
    def create(self, vals):
        if vals.get('name', '/') == '/':
            vals['name'] = self.env['ir.sequence'].next_by_code('pepiniere.lot.plant') or '/'
        return super(PepiniereLotPlant, self).create(vals)
    
    @api.depends('date_semis', 'variete_id.espece_id.duree_pepiniere')
    def _compute_date_sortie_prevue(self):
        for record in self:
            if record.date_semis and record.variete_id.espece_id.duree_pepiniere:
                from datetime import timedelta
                record.date_sortie_prevue = record.date_semis + timedelta(days=record.variete_id.espece_id.duree_pepiniere)
            else:
                record.date_sortie_prevue = False
    
    @api.depends('quantite_repiquee', 'quantite_vendue')
    def _compute_quantite_disponible(self):
        for record in self:
            record.quantite_disponible = record.quantite_repiquee - record.quantite_vendue
    
    @api.depends('sale_line_ids.product_uom_qty', 'sale_line_ids.order_id.state')
    def _compute_quantite_vendue(self):
        for record in self:
            # Compter uniquement les lignes de commandes confirmées
            confirmed_lines = record.sale_line_ids.filtered(
                lambda l: l.order_id.state in ['sale', 'done']
            )
            record.quantite_vendue = sum(confirmed_lines.mapped('product_uom_qty'))
    
    @api.depends('quantite_semis', 'quantite_germee')
    def _compute_taux_germination(self):
        for record in self:
            if record.quantite_semis > 0:
                record.taux_germination = (record.quantite_germee / record.quantite_semis) * 100
            else:
                record.taux_germination = 0.0
    
    @api.depends('intervention_ids.cout')
    def _compute_cout_total(self):
        for record in self:
            record.cout_total = sum(record.intervention_ids.mapped('cout'))
    
    @api.depends('cout_total', 'quantite_disponible')
    def _compute_cout_unitaire(self):
        for record in self:
            if record.quantite_disponible > 0:
                record.cout_unitaire = record.cout_total / record.quantite_disponible
            else:
                record.cout_unitaire = 0.0
    
    def action_germination(self):
        self.write({'state': 'germination'})
    
    def action_repiquage(self):
        self.write({'state': 'repiquage'})
    
    def action_croissance(self):
        self.write({'state': 'croissance'})
    
    def action_pret(self):
        self.write({'state': 'pret'})
    
    def action_cloture(self):
        self.write({'state': 'cloture'})


class PepiniereSerre(models.Model):
    _name = 'pepiniere.serre'
    _description = 'Serre'
    _order = 'name'

    name = fields.Char(string='Nom', required=True)
    code = fields.Char(string='Code')
    superficie = fields.Float(string='Superficie (m²)')
    capacite = fields.Integer(string='Capacité (plants)')
    type_serre = fields.Selection([
        ('tunnel', 'Tunnel'),
        ('verre', 'Verre'),
        ('ombriere', 'Ombrière'),
    ], string='Type')
    active = fields.Boolean(string='Actif', default=True)
