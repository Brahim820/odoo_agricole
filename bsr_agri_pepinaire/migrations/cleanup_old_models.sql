-- Script SQL pour nettoyer les anciens modèles pepiniere.vente
-- À exécuter manuellement si la migration automatique échoue

-- Supprimer les données liées aux anciens modèles
DELETE FROM ir_model_data 
WHERE model IN ('pepiniere.vente', 'pepiniere.vente.line');

-- Supprimer les vues liées
DELETE FROM ir_ui_view 
WHERE model IN ('pepiniere.vente', 'pepiniere.vente.line');

-- Supprimer les actions liées
DELETE FROM ir_act_window 
WHERE res_model IN ('pepiniere.vente', 'pepiniere.vente.line');

-- Supprimer les menus liés
DELETE FROM ir_ui_menu 
WHERE action IN (
    SELECT CONCAT('ir.actions.act_window,', id::text)
    FROM ir_act_window 
    WHERE res_model IN ('pepiniere.vente', 'pepiniere.vente.line')
);

-- Supprimer les règles d'accès
DELETE FROM ir_model_access 
WHERE model_id IN (
    SELECT id FROM ir_model 
    WHERE model IN ('pepiniere.vente', 'pepiniere.vente.line')
);

-- Supprimer les champs
DELETE FROM ir_model_fields 
WHERE model IN ('pepiniere.vente', 'pepiniere.vente.line');

-- Supprimer les contraintes
DELETE FROM ir_model_constraint 
WHERE model IN (
    SELECT id FROM ir_model 
    WHERE model IN ('pepiniere.vente', 'pepiniere.vente.line')
);

-- Supprimer les sélections de champs
DELETE FROM ir_model_fields_selection
WHERE field_id IN (
    SELECT id FROM ir_model_fields
    WHERE model IN ('pepiniere.vente', 'pepiniere.vente.line')
);

-- Supprimer les modèles eux-mêmes
DELETE FROM ir_model 
WHERE model IN ('pepiniere.vente', 'pepiniere.vente.line');

-- Supprimer les tables si elles existent
DROP TABLE IF EXISTS pepiniere_vente_line CASCADE;
DROP TABLE IF EXISTS pepiniere_vente CASCADE;

-- Nettoyer le cache
DELETE FROM ir_attachment 
WHERE res_model IN ('pepiniere.vente', 'pepiniere.vente.line');

-- Commit les changements
COMMIT;
