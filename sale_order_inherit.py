from odoo import models, fields, api


class SaleOrderInherit(models.Model):
    _inherit = 'sale.order'

    def action_confirm(self):
        res = super(SaleOrderInherit, self).action_confirm()
        similar_products = {}
        for line in self.order_line:
            product = line.product_id.id
            quantity = line.product_uom_qty
            if product in similar_products:
                for similar_product in similar_products[product]:
                    if similar_product.product_id.id == product:
                        similar_product.product_uom_qty += quantity
                        break
            else:
                similar_products[product] = [line]
        current_picking = self.env['stock.picking'].search([('sale_id', '=', self.id)])
        self.write({'picking_ids': [(5, 0, 0)]})
        for product_id, lines in similar_products.items():
            move_lines = []
            for line in lines:
                move_lines.append((0, 0, {
                    'product_id': line.product_id.id if line.product_id else None,
                    'product_uom_qty': line.product_uom_qty if line.product_uom_qty else None,
                    'location_id': current_picking.location_id.id,
                    'location_dest_id': current_picking.location_dest_id.id,
                    'name': line.product_id.name,
            }))
            new_picking = self.env['stock.picking'].create({
                'picking_type_id': current_picking.picking_type_id.id,
                'location_id': current_picking.location_id.id,
                'location_dest_id': current_picking.location_dest_id.id,
                'move_ids_without_package': move_lines,
            })
            self.write({'picking_ids': [(4, new_picking.id)]})
        return res

