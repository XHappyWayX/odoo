from odoo import fields, models, Command
from odoo.exceptions import UserError

class EstateProperty(models.Model):
    _inherit = 'test_model'
    _description = "Estate Property Extension"

    def action_sold(self, vals):
        res = super().action_sold()
        journal = self.env['account.journal'].search([('type', '=', 'sale')], limit=1)
        for property in self:
            if not property.buyer_id:
                raise UserError('No partner defined for this property.')

            self.env['account.move'].create({
                'partner_id': property.buyer_id.id,
                'move_type': 'out_invoice',
                'journal_id': journal.id,
                'invoice_line_ids': [
                    Command.create({
                        'name': 'Commission (6%)',
                        'quantity': 1,
                        'price_unit': property.selling_price * 0.06,
                    }),
                    Command.create({
                        'name': 'Administrative fees',
                        'quantity': 1,
                        'price_unit': 100.0,
                    }),
                ],
            })
        return res
