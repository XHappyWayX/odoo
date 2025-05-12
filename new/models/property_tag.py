from odoo import fields, models

class PropertyTag(models.Model):
    _name = "property.tag"
    _description = "Property tags"

    name = fields.Char(required=True)

    _sql_constraints = [
        ("tag_name_uniq", "unique (name)", "Tag name already exists!"),
    ]