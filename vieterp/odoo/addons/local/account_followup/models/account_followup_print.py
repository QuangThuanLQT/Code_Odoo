# -*- coding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2004-2010 Tiny SPRL (<http://tiny.be>).
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as
#    published by the Free Software Foundation, either version 3 of the
#    License, or (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################

import time
import odoo
from odoo import models, fields, _
from collections import defaultdict
from odoo.report import report_sxw
from odoo.exceptions import Warning

class report_rappel(report_sxw.rml_parse):
    _name = 'account_followup.report.rappel'

    def __init__(self, cr, uid, name, context=None):
        super(report_rappel, self).__init__(cr, uid, name, context=context)
        self.localcontext.update({
            'time': time,
            'ids_to_objects': self._ids_to_objects,
            'getLines': self._lines_get,
            'get_text': self._get_text
        })

    def _ids_to_objects(self, ids):
        all_lines = []
        env = odoo.api.Environment(self.cr, self.uid, {})
        for line in env['account_followup.stat.by.partner'].browse(ids):
            if line not in all_lines:
                all_lines.append(line)
        return all_lines

    def _lines_get(self, stat_by_partner_line):
        return self._lines_get_with_partner(stat_by_partner_line.partner_id, stat_by_partner_line.company_id.id)

    def _lines_get_with_partner(self, partner, company_id):
        env = odoo.api.Environment(self.cr, self.uid, {})
        moveline_obj = env['account.move.line']
        move_lines = moveline_obj.search([
            ('partner_id', '=', partner.id),
            ('account_id.user_type_id.type', '=', 'receivable'),
            ('reconciled', '=', False),
            ('company_id', '=', company_id),
            '|', ('date_maturity', '=', False), ('date_maturity', '<=', fields.Date.today(self)),
        ])

        # lines_per_currency = {currency: [line data, ...], ...}
        lines_per_currency = defaultdict(list)
        for line in move_lines:
            currency = line.currency_id or line.company_id.currency_id
            line_data = {
                'name': line.move_id.name,
                'ref': line.ref,
                'date': line.date,
                'date_maturity': line.date_maturity,
                'balance': line.amount_currency if currency != line.company_id.currency_id else line.debit - line.credit,
                'blocked': line.blocked,
                'currency_id': currency,
            }
            lines_per_currency[currency].append(line_data)

        return [{'line': lines, 'currency': currency} for currency, lines in lines_per_currency.items()]

    def _get_text(self, stat_line, followup_id):
        env = odoo.api.Environment(self.cr, self.uid, {})
        fp_obj = env['account_followup.followup']
        fp_line = fp_obj.browse(followup_id).followup_line_ids
        if not fp_line:
            raise Warning(_('Error!'), _("The followup plan defined for the current company does not have any followup action."))
        #the default text will be the first fp_line in the sequence with a description.
        default_text = ''
        li_delay = []
        for line in fp_line:
            if not default_text and line.description:
                default_text = line.description
            li_delay.append(line.delay)
        li_delay.sort(reverse=True)
        a = {}
        #look into the lines of the partner that already have a followup level, and take the description of the higher level for which it is available
        partner_lines = env['account.move.line'].search([
            ('partner_id','=',stat_line.partner_id.id),
            ('reconciled', '=', False),
            ('company_id','=',stat_line.company_id.id),
            ('blocked','=',False),
            ('debit','!=',False),
            ('account_id.user_type_id.type', '=', 'receivable'),
            ('followup_line_id','!=',False)
        ])
        partner_max_delay = 0
        partner_max_text = ''
        for i in partner_lines:
            if i.followup_line_id.delay > partner_max_delay and i.followup_line_id.description:
                partner_max_delay = i.followup_line_id.delay
                partner_max_text = i.followup_line_id.description
        text = partner_max_delay and partner_max_text or default_text
        if text:
            lang_obj = env['res.lang']
            languages = lang_obj.search([('code', '=', stat_line.partner_id.lang)])
            date_format = languages and languages[0].date_format or '%Y-%m-%d'
            text = text % {
                'partner_name': stat_line.partner_id.name,
                'date': time.strftime(date_format),
                'company_name': stat_line.company_id.name,
                'user_signature': env['res.users'].browse(self.uid).signature or '',
            }
        return text

class report_followup(models.AbstractModel):
    _name = 'report.account_followup.report_followup'
    _inherit = 'report.abstract_report'
    _template = 'account_followup.report_followup'
    _wrapped_report_class = report_rappel

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4: