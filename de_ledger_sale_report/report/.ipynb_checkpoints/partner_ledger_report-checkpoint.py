from odoo import models, fields, api, _
from  odoo import models
from odoo.exceptions import UserError
from dateutil.relativedelta import relativedelta
from datetime import datetime, timedelta


class PartnerLedgerXlS(models.AbstractModel):
    _name = 'report.de_ledger_sale_report.ledger_report_xlx'
    _description = 'Partner Ledger report'
    _inherit = 'report.report_xlsx.abstract'
    
    def generate_xlsx_report(self, workbook, data, lines):
        docs = self.env['partner.ledger.wizard'].browse(self.env.context.get('active_id'))
        sheet = workbook.add_worksheet('Partner Ledger Report')
        bold = workbook.add_format({'bold': True, 'align': 'center','bg_color': '#FFFF99','border': True})
        title = workbook.add_format({'bold': True, 'align': 'center', 'font_size': 20, 'bg_color': '#FFFF99', 'border': True})
        header_row_style = workbook.add_format({'bold': True, 'align': 'center', 'border':True})
        format2 = workbook.add_format({'align': 'center'})
        format3 = workbook.add_format({'align': 'center','bold': True,'border': True,})    
        
        
        sheet.set_column(0, 0, 30)
        sheet.set_column(1, 1, 25)
        sheet.set_column(2, 2, 25)
        sheet.set_column(3, 3, 25)
        sheet.set_column(4, 4, 25)
        sheet.set_column(5, 5, 25)
        
            
        
        sheet.write(2, 0, 'Partner', header_row_style)
        sheet.write(2, 1, 'CNIC', header_row_style)
        sheet.write(2, 2, 'Debit', header_row_style)
        sheet.write(2, 3, "Credit", header_row_style)
        sheet.write(2, 4, "Balance", header_row_style)
        row = 3
        
        
        
        all_partners = []
        partner_ledger = self.env['account.move.line'].search([('date','>=',docs.date_from),('date','<=',docs.date_to),('account_id.user_type_id','=',(1,2)),('move_id.state','!=','cancel')])
        if docs.state== 'all':
            partner_ledger = self.env['account.move.line'].search([('date','>=',docs.date_from),('date','<=',docs.date_to),('account_id.user_type_id','=',(1,2)),('move_id.state','!=','cancel')])
        if docs.state== 'draft':
            partner_ledger = self.env['account.move.line'].search([('date','>=',docs.date_from),('date','<=',docs.date_to),('account_id.user_type_id','=',(1,2)),('move_id.state','=','draft')])
        if docs.state== 'posted':
            partner_ledger = self.env['account.move.line'].search([('date','>=',docs.date_from),('date','<=',docs.date_to),('account_id.user_type_id','=',(1,2)),('move_id.state','=','posted')])
        for uniq_line in partner_ledger:
            all_partners.append(uniq_line.partner_id.id)   
        uniq_partner_ledger = set(all_partners)  
        
        for line in uniq_partner_ledger:
            journal_items = self.env['account.move.line'].search([('partner_id','=',line),('date','>=',docs.date_from),('date','<=',docs.date_to),('account_id.user_type_id','=',(1,2)),('move_id.state','!=','cancel')])
            total_debit = total_credit = total_balnce = 0
            for jv in journal_items:
                total_debit += jv.debit
                total_credit += jv.credit
                total_balnce = total_debit - total_credit
            psrtner = self.env['res.partner'].search([('id','=',line)], limit=1)    
            sheet.write(row, 0, psrtner.name, format2)
            sheet.write(row, 1, psrtner.nic, format2)
            sheet.write(row, 2, total_debit, format2)
            sheet.write(row, 3, total_credit, format2)
            sheet.write(row, 4, total_balnce, format2)
            row += 1
                
    
            