from odoo import fields, models

class PropertyTag(models.Model):
    _name = "property.tag"
    _description = "Property tags"
    _order = "name"

    name = fields.Char(required=True)
    color = fields.Integer()

    _sql_constraints = [
        ("tag_name_uniq", "unique (name)", "Tag name already exists!"),
    ]