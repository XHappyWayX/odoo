from odoo import fields, models, api

class PropertyType(models.Model):
    _name = "property.type"
    _description = "Property types"
    _order = "type_name"

    type_name = fields.Char(required=True)
    property_ids = fields.One2many("test_model", "property_type_id", string="Properties")
    sequence = fields.Integer('Sequence', default=1,)
    display_name = fields.Char(related='type_name', store=True)
    offer_ids = fields.One2many("property.offer", "property_type_id", string="Offers")
    offer_count = fields.Integer(compute='_compute_offer_count', store=True)

    @api.depends('offer_ids')
    def _compute_offer_count(self):
        for record in self:
            record.offer_count = len(record.offer_ids)

    _sql_constraints = [
        ("type_name_uniq", "unique (type_name)", "Type name already exists!"),
    ]