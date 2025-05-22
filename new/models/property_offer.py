from odoo import fields, models, api
from datetime import timedelta, date
from odoo.exceptions import ValidationError, UserError


class PropertyOffer(models.Model):
    _name = "property.offer"
    _description = "Property Offer"
    _order = "price desc"

    price = fields.Float(required=True)
    status = fields.Selection(selection=[('accepted', 'Accepted'), ('refused', 'Refused')], copy=False, readonly=True)
    buyer_id = fields.Many2one('res.partner', string='Buyer', required=True)
    property_id = fields.Many2one('test_model', string='Property', required=True, ondelete='cascade')
    validity = fields.Integer(store=True, default=7, compute="_compute_validity", inverse="_compute_date_deadline")
    date_deadline = fields.Date(store=True, compute="_compute_date_deadline", inverse="_compute_validity")
    property_type_id = fields.Many2one(related='property_id.property_type_id')

    @api.depends("validity")
    def _compute_date_deadline(self):
        for record in self:
            now = record.create_date or date.today()
            if record.validity >= 0:
                record.date_deadline = now + timedelta(record.validity)
            else:
                record.validity = 0
                record.date_deadline = now + timedelta(record.validity)
    @api.depends("date_deadline")
    def _compute_validity(self):
        for record in self:
            if record.date_deadline and record.date_deadline > record.create_date.date():
                record.validity = (record.date_deadline - record.create_date.date()).days
            else:
                record.validity = 1

    def action_accept(self):
        self._check_price()
        for record in self:
            record.property_id.status = 'offer_accepted'
            record.status = 'accepted'
            record.property_id.selling_price = record.price
            record.property_id.buyer_id = record.buyer_id

    def action_refuse(self):
        for record in self:
            record.status = 'refused'

    @api.constrains('price', 'property_id.expected_price')
    def _check_price(self):
        for record in self:
            if record.property_id.expected_price * 0.9 > record.price:
                record.property_id.selling_price = 0
                raise ValidationError("The price must be at least 90% of the expected price.")

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if vals.get('property_id'):
                property = self.env['test_model'].browse(vals['property_id'])
                if property.test_ids.filtered(lambda o: o.price > vals.get('price', 0.0)):
                    raise UserError("The offer must be higher than existing offers.")
                property.status = 'offer_received'
        return super().create(vals_list)

    _sql_constraints = [
        ('check_price', 'CHECK(price > 0)', 'The price must be strictly positive.')
    ]