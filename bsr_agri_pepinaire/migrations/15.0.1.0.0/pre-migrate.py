# -*- coding: utf-8 -*-

def migrate(cr, version):
    """
    Migration pour supprimer les anciens modèles pepiniere.vente et pepiniere.vente.line
    qui ont été remplacés par l'intégration avec sale.order
    """
    if not version:
        return

    # Supprimer les données liées aux anciens modèles
    cr.execute("""
        DELETE FROM ir_model_data 
        WHERE model IN ('pepiniere.vente', 'pepiniere.vente.line')
    """)
    
    # Supprimer les vues liées
    cr.execute("""
        DELETE FROM ir_ui_view 
        WHERE model IN ('pepiniere.vente', 'pepiniere.vente.line')
    """)
    
    # Supprimer les actions liées
    cr.execute("""
        DELETE FROM ir_act_window 
        WHERE res_model IN ('pepiniere.vente', 'pepiniere.vente.line')
    """)
    
    # Supprimer les règles d'accès
    cr.execute("""
        DELETE FROM ir_model_access 
        WHERE model_id IN (
            SELECT id FROM ir_model 
            WHERE model IN ('pepiniere.vente', 'pepiniere.vente.line')
        )
    """)
    
    # Supprimer les champs
    cr.execute("""
        DELETE FROM ir_model_fields 
        WHERE model IN ('pepiniere.vente', 'pepiniere.vente.line')
    """)
    
    # Supprimer les contraintes
    cr.execute("""
        DELETE FROM ir_model_constraint 
        WHERE model IN (
            SELECT id FROM ir_model 
            WHERE model IN ('pepiniere.vente', 'pepiniere.vente.line')
        )
    """)
    
    # Supprimer les modèles eux-mêmes
    cr.execute("""
        DELETE FROM ir_model 
        WHERE model IN ('pepiniere.vente', 'pepiniere.vente.line')
    """)
    
    # Supprimer les tables si elles existent
    cr.execute("""
        DROP TABLE IF EXISTS pepiniere_vente_line CASCADE
    """)
    cr.execute("""
        DROP TABLE IF EXISTS pepiniere_vente CASCADE
    """)
