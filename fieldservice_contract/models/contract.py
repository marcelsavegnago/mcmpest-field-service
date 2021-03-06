# Copyright 2019 Akretion <raphael.reverdy@akretion.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import api, fields, models


class ContractContract(models.Model):
    _inherit = 'contract.contract'

    fsm_location_id = fields.Many2one(
        string='FSM Location',
        comodel_name='fsm.location',
        inverse_name='contract_ids',
        copy=True,
    )

    invoiceable_stage_ids = fields.Many2many(
        string='Invoiceable stages',
        comodel_name='fsm.stage',
        domain=[['stage_type', '=', 'order']],
        default=lambda x: x._default_invoiceable_stage()
    )

    fsm_order_count = fields.Integer(
        string='FSM Orders', compute='_compute_fsm_counts')
    fsm_recurring_count = fields.Integer(
        string='FSM Recurrings', compute='_compute_fsm_counts')

    @api.multi
    @api.depends('contract_line_ids')
    def _compute_fsm_counts(self):
        for contract in self:
            contract.fsm_recurring_count = self.env['fsm.recurring']. \
                search_count([
                    ('contract_line_id', 'in', contract.contract_line_ids.ids)
                ])
            contract.fsm_order_count = self.env['fsm.order'].search_count([
                ('contract_id', '=', contract.id)
            ])

    def _default_invoiceable_stage(self):
        return self.env.ref('fieldservice.fsm_stage_completed').ids

    @api.multi
    def action_view_fsm_recurring(self):
        fsm_recurrings = self.contract_line_ids.mapped('fsm_recurring_id')
        action = self.env.ref(
            'fieldservice_recurring.action_fsm_recurring').read()[0]
        if len(fsm_recurrings) > 1:
            action['domain'] = [('id', 'in', fsm_recurrings.ids)]
        elif len(fsm_recurrings) == 1:
            action['views'] = [
                (self.env.ref(
                    'fieldservice_recurring.fsm_recurring_form_view').id,
                    'form')]
            action['res_id'] = fsm_recurrings.id
        else:
            action = {'type': 'ir.actions.act_window_close'}
        return action

    @api.multi
    def action_view_fsm_order(self):
        # fetch all orders:
        #    - created directly
        #    - created by recurring
        line_ids = self.contract_line_ids.ids
        action = self.env.ref(
            'fieldservice.action_fsm_dash_order').read()[0]
        action['domain'] = [('contract_line_id', 'in', line_ids)]
        return action
