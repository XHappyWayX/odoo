from odoo import fields, models, api
from datetime import timedelta
from odoo.exceptions import UserError

class TestModel(models.Model):
    _name = "test_model"
    _description = "Test Model"
    _order = "id desc"

    name = fields.Char(required=True, default="Unknown")
    description = fields.Text()
    postcode = fields.Char()
    date_availability = fields.Date(copy=False, default=fields.Date.today() + timedelta(days=90))
    expected_price = fields.Float(required=True, )
    selling_price = fields.Float(required=True, readonly=True, copy=False, default=0.0)
    bedrooms = fields.Integer(default=2)
    living_area = fields.Integer()
    facades = fields.Integer()
    garage = fields.Boolean()
    garden = fields.Boolean()
    garden_area = fields.Integer()
    garden_orientation = fields.Selection(selection=[('north', 'North'), ('south', 'South'), ('east', 'East'), ('west', 'West')],)
    active = fields.Boolean(default=True)
    status = fields.Selection(selection=[('new', 'New'), ('offer_received', 'Offer Received'), ('offer_accepted', 'Offer Accepted'), ('sold', 'Sold'), ('canceled', 'Canceled')], readonly=True, default='new')
    property_type_id = fields.Many2one(comodel_name="property.type", string="Property Type")
    sale_person_id = fields.Many2one(comodel_name="res.users", string="Sales Person", default=lambda self: self.env.user)
    buyer_id = fields.Many2one(comodel_name="res.partner", string="Buyer", copy=False)
    tags_ids = fields.Many2many(comodel_name="property.tag", string="Tags")
    test_ids = fields.One2many("property.offer", "property_id", string="Test Models")
    total_area = fields.Float(store=True, compute="_compute_total_area")
    best_price = fields.Float(store=True, compute="_compute_best_price")

    @api.depends("test_ids")
    def _compute_best_price(self):
        for record in self:
            if record.test_ids:
                record.best_price = max(record.test_ids.mapped("price"))
            else:
                record.best_price = 0

    @api.depends("living_area", "garden_area")
    def _compute_total_area(self):
        for record in self:
            record.total_area = record.living_area + record.garden_area

    @api.onchange("garden")
    def _onchange_garden(self):
        if self.garden:
            self.garden_area = 10
            self.garden_orientation = "north"
        else:
            self.garden_area = 0
            self.garden_orientation = None

    def action_sold(self):
        for record in self:
            if record.status == "canceled":
                raise UserError("Canceled properties cannot be sold.")
            elif record.status == "sold":
                raise UserError("Properties already sold.")
            elif record.buyer_id == False:
                raise UserError("No buyer selected.")
            else:
                record.status = "sold"

    def action_canceled(self):
        for record in self:
            if record.status == "canceled":
                raise UserError("Properties already canceled.")
            elif record.status == "sold":
                raise UserError("Sold properties cannot be canceled.")
            else:
                record.status = "canceled"

    @api.ondelete(at_uninstall=False)
    def _check_status_before_delete(self):
        for record in self:
            if record.status not in ["new", "canceled"]:
                raise UserError("Only canceled or new properties can be deleted.")

    _sql_constraints = [
        ("check_expected_price", "CHECK(expected_price > 0)", "The expected price must be strictly positive."),
        ("check_selling_price", "CHECK(selling_price >= 0)", "The selling price must be positive or zero."),

    ]

class UserExtension(models.Model):
    _inherit = "res.users"
    _description = "User Extension"

    property_ids = fields.One2many("test_model", "buyer_id", string="Sailing Properties", domain="[('status', '!=', 'sold'), ('status', '!=', 'canceled')]")