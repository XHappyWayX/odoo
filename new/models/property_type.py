from odoo import fields, models

class PropertyType(models.Model):
    _name = "property.type"
    _description = "Property types"

    type_name = fields.Char(required=True)
    property_ids = fields.One2many("test_model", "property_type_id", string="Properties")

    _sql_constraints = [
        ("type_name_uniq", "unique (name)", "Type name already exists!"),
    ]