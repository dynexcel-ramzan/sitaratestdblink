from odoo import models, fields, api, _
from  odoo import models
from odoo.exceptions import UserError
from dateutil.relativedelta import relativedelta
from datetime import datetime, timedelta


class PlotDetailXlS(models.AbstractModel):
    _name = 'report.de_commission_report.commission_report_xlx'
    _description = 'Commission report'
    _inherit = 'report.report_xlsx.abstract'
    
    
    def generate_xlsx_report(self, workbook, data, lines):
        docs = self.env['commission.wizard'].browse(self.env.context.get('active_id'))
        sheet = workbook.add_worksheet('Commission report')
        bold = workbook. add_format({'bold': True, 'align': 'center','bg_color': '#FFFF99','border': True})
        title = workbook.add_format({'bold': True, 'align': 'center', 'font_size': 15, 'border': True})
        header_row_style = workbook.add_format({'bold': True, 'align': 'center', 'border':True})
        format2 = workbook.add_format({'align': 'center'})
        format3 = workbook.add_format({'align': 'center','bold': True,'border': True,})
        
        sheet.write('C1:D1', 'SITARA GREEN CITY' ,title)
        sheet.write('C2:D2', 'COMMISSION REPORT' ,title)

        sheet.set_column(0, 0, 30)
        sheet.set_column(1, 1, 25)
        sheet.set_column(2, 2, 25)
        sheet.set_column(3, 3, 25)
        sheet.set_column(4, 4, 25)
        sheet.set_column(5, 5, 25)
        sheet.set_column(6, 6, 25)
        sheet.set_column(7, 7, 25)

        sheet.write(2, 0, 'SR NO', header_row_style)
        sheet.write(2, 1, 'Plot No', header_row_style)
        sheet.write(2, 2, 'Customer Name', header_row_style)
        sheet.write(2, 3, 'Dealer Name', header_row_style)
        sheet.write(2, 4, "Commission", header_row_style)
        sheet.write(2, 5, "Commission Payment Date", header_row_style)
        sheet.write(2, 6, "Dealer Phone", header_row_style)
        sheet.write(2, 7, "Dealer Mobile", header_row_style)
        row = 3


        commission_detail = self.env['product.product'].search([])

        
        row = 3
        col_no = 0 
        sr_no = 1
        total_commission=0
        for plt in commission_detail:
            if plt.commission_amount > 0:
                
                sheet.write(row, col_no, str(sr_no), format2)
                col_no += 1
                sheet.write(row, col_no, str(plt.name), format2)
                col_no += 1
                sheet.write(row, col_no, str(plt.partner_id.name if plt.partner_id else ' '), format2)
                col_no += 1
                sheet.write(row, col_no, str(plt.booking_id.dealer_id.name if plt.booking_id.dealer_id.name else ' '), format2)
                col_no += 1
                sheet.write(row, col_no, round(plt.commission_amount,4), format2)
                total_commission += plt.commission_amount
                col_no += 1
                for line in plt.booking_id.order_line:
                    if line.product_id.name == plt.name:
                        sheet.write(row, col_no, str(line.commission_date if line.commission_date else ' '), format2)
                        col_no += 1
                sheet.write(row, col_no, str(plt.phone), format2)
                sheet.write(row, col_no, str(plt.mobile), format2)
                col_no =0
                sr_no += 1
                row += 1
            
            
        sheet.write(row, 0, str(), header_row_style)
        sheet.write(row, 1, str(), header_row_style)
        sheet.write(row, 2, str(), header_row_style)
        sheet.write(row, 3, str(), header_row_style)
        sheet.write(row, 4, round(total_commission,2), header_row_style)
        sheet.write(row, 5, str(), header_row_style)
        row += 1
        
            
            




            