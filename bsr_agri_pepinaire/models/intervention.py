# -*- coding: utf-8 -*-

from odoo import models, fields, api


class PepiniereIntervention(models.Model):
    _name = 'pepiniere.intervention'
    _description = 'Intervention culturale'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _order = 'date desc'

    name = fields.Char(string='Référence', required=True, copy=False, readonly=True, default='/')
    lot_id = fields.Many2one('pepiniere.lot.plant', string='Lot', required=True, ondelete='cascade', tracking=True)
    date = fields.Date(string='Date', required=True, default=fields.Date.today, tracking=True)
    
    # Type d'intervention
    type_intervention = fields.Selection([
        ('arrosage', 'Arrosage'),
        ('fertilisation', 'Fertilisation'),
        ('traitement', 'Traitement phytosanitaire'),
        ('taille', 'Taille'),
        ('repiquage', 'Repiquage'),
        ('desherbage', 'Désherbage'),
        ('autre', 'Autre'),
    ], string='Type d\'intervention', required=True, tracking=True)
    
    # Détails
    description = fields.Text(string='Description')
    produit_utilise = fields.Char(string='Produit utilisé')
    quantite_produit = fields.Float(string='Quantité produit')
    unite_produit = fields.Char(string='Unité')
    
    # Ressources humaines
    employe_id = fields.Many2one('hr.employee', string='Employé', tracking=True)
    duree = fields.Float(string='Durée (heures)')
    
    # Coûts
    cout_main_oeuvre = fields.Float(string='Coût main d\'œuvre')
    cout_produit = fields.Float(string='Coût produit')
    cout = fields.Float(string='Coût total', compute='_compute_cout', store=True)
    
    # État
    state = fields.Selection([
        ('planifie', 'Planifié'),
        ('en_cours', 'En cours'),
        ('termine', 'Terminé'),
        ('annule', 'Annulé'),
    ], string='État', default='planifie', required=True, tracking=True)
    
    notes = fields.Text(string='Notes')
    
    @api.model
    def create(self, vals):
        if vals.get('name', '/') == '/':
            vals['name'] = self.env['ir.sequence'].next_by_code('pepiniere.intervention') or '/'
        return super(PepiniereIntervention, self).create(vals)
    
    @api.depends('cout_main_oeuvre', 'cout_produit')
    def _compute_cout(self):
        for record in self:
            record.cout = record.cout_main_oeuvre + record.cout_produit
    
    def action_en_cours(self):
        self.write({'state': 'en_cours'})
    
    def action_termine(self):
        self.write({'state': 'termine'})
    
    def action_annule(self):
        self.write({'state': 'annule'})
