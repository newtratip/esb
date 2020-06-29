# Copyright 2020 Ecosoft Co., Ltd (http://ecosoft.co.th/)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html)

from odoo import api, fields, models


class SaleOrder(models.Model):
    _inherit = "sale.order"

    so_created = fields.Boolean(default=False)

    discount_waranty = fields.Monetary(
        string="Waranty Discount",
        digits="Discount",
        compute="_compute_discount",
    )
    discount_special = fields.Monetary(
        string="Special Discount",
        digits="Discount",
        compute="_compute_discount",
    )
    discount_last = fields.Float(
        string="Discount",
        digits="Discount",
        default=0.0,
    )
    discount_last_amount = fields.Monetary(
        string="Amount Discount",
        digits="Discount",
        compute="_compute_discount",
    )
    discount_special = fields.Float(
        string="Special Discount",
        digits="Discount",
        default=0.0,
    )
    discount_special_amount = fields.Monetary(
        string="Amount Special Discount",
        digits="Discount",
        compute="_compute_discount",
    )
    partner_bank_id = fields.Many2one(
        comodel_name="res.partner.bank",
        string="Bank Account",
        domain="['|', ('company_id', '=', False), ('company_id', '=', company_id)]",
    )

    # _sql_constraints = [
    #     (
    #         "discount_last_limit",
    #         "CHECK (discount_last <= 100.0)",
    #         "Discount must be lower than 100%.",
    #     ),
    #     (
    #         "discount_special_limit",
    #         "CHECK (discount_special <= 100.0)",
    #         "Discount must be lower than 100%.",
    #     ),
    # ]

    @api.depends("order_line")
    def _compute_discount(self):
        for record in self:
            discount_waranty = 0.00
            discount_special = 0.00
            for line in record.order_line:
                discount_waranty += line.subtotal_no_disc * line.discount / 100
                discount_special += line.subtotal_no_disc * line.discount2 / 100
            record.discount_waranty = discount_waranty
            record.discount_special = discount_special

            # total = sum(record.order_line.mapped("subtotal_no_disc"))
            # record.discount_last_amount = total * record.discount_last / 100
            # record.discount_special_amount = (total - record.discount_last_amount) * record.discount_special / 100

    @api.model
    def create(self, vals):
        vals["so_created"] = True
        return super().create(vals)

    def copy_data(self, default=None):
        if default is None:
            default = {}
        default["type_id"] = self.type_id.id
        return super().copy_data(default)

    def _prepare_invoice(self):
        self.ensure_one()
        invoice_vals = super()._prepare_invoice()
        # invoice_vals["discount_last"] = self.discount_last
        # invoice_vals["discount_special"] = self.discount_special
        invoice_vals["invoice_partner_bank_id"] = self.partner_bank_id.id
        return invoice_vals


class SaleOrderLine(models.Model):
    _inherit = "sale.order.line"

    subtotal_no_disc = fields.Monetary(
        string="Subtotal Before Discount",
        store=True,
        compute="_compute_subtotal_no_disc",
        currency_field="currency_id",
        help="Subtotal not including discount",
    )

    @api.depends("product_uom_qty", "price_unit")
    def _compute_subtotal_no_disc(self):
        for record in self:
            record.subtotal_no_disc = record.product_uom_qty * record.price_unit
