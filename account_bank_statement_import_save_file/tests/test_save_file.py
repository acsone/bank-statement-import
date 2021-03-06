# -*- coding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    This module copyright (C) 2015 Therp BV <http://therp.nl>.
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
import base64
from mock import patch
from openerp.tests.common import TransactionCase


acc_number = 'BE1234567890'


class TestSaveFile(TransactionCase):
    def test_SaveFile(self):
        with patch.object(
                self.env.registry
                .models['account.bank.statement.import'].__class__,
                '_parse_file'
        ) as _parse_file:
            _parse_file.side_effect = lambda data_file: (
                'EUR',
                acc_number,
                [{
                    'name': '000000123',
                    'date': '2013-06-26',
                    'transactions': [{
                        'name': 'KBC-INVESTERINGSKREDIET 787-5562831-01',
                        'date': '2013-06-26',
                        'amount': 42,
                        'unique_import_id': 'hello',
                    }],
                }],
            )
            import_wizard = self.env['account.bank.statement.import']
            journal_id = self.env['res.partner.bank'].search([
                ('acc_number', '=', acc_number),
            ]).journal_id.id
            if not journal_id:
                account = import_wizard._create_bank_account(acc_number)
                journal_id = self.env['account.journal']\
                    .search([
                        '|',
                        ('currency.name', '=', 'EUR'),
                        ('currency', '=', False)
                    ]).ids[0]
                account.journal_id = journal_id
            action = import_wizard.with_context(journal_id=journal_id)\
                .create({'data_file': base64.b64encode('hello world')})\
                .import_file()
            for statement in self.env['account.bank.statement'].browse(
                    action['context']['statement_ids']):
                self.assertEqual(
                    base64.b64decode(statement.import_file.datas),
                    'hello world')
