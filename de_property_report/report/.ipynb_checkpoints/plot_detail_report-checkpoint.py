from odoo import models, fields, api, _
from  odoo import models
from odoo.exceptions import UserError
from dateutil.relativedelta import relativedelta
from datetime import datetime, timedelta


class PlotDetailXlS(models.AbstractModel):
    _name = 'report.de_property_report.detail_report_xlx'
    _description = 'Plot Detail report'
    _inherit = 'report.report_xlsx.abstract'
    
    
    def generate_xlsx_report(self, workbook, data, lines):
        docs = self.env['plot.detail.wizard'].browse(self.env.context.get('active_id'))
        sheet = workbook.add_worksheet('Plot Detail Report')
        bold = workbook. add_format({'bold': True, 'align': 'center','bg_color': '#FFFF99','border': True})
        title = workbook.add_format({'bold': True, 'align': 'center', 'font_size': 15, 'border': True})
        header_row_style = workbook.add_format({'bold': True, 'align': 'center', 'border':True})
        format2 = workbook.add_format({'align': 'center'})
        format3 = workbook.add_format({'align': 'center','bold': True,'border': True,}) 
        
        if docs.type=='available': 
            sheet.write('C1:D1', 'SITARA GREEN CITY' ,title)
            sheet.write('C2:D2', 'DETAIL OF AVAILABLE PLOTS' ,title)
        elif docs.type=='unconfirm': 
            sheet.write('C1:D1', 'SITARA GREEN CITY' ,title)
            sheet.write('C2:D2', 'DETAIL OF UNCONFIRMED RESERVE PLOTS' ,title)
        elif docs.type=='reserved': 
            sheet.write('C1:D1', 'SITARA GREEN CITY' ,title)
            sheet.write('C2:D2', 'DETAIL OF CONFIRMED RESERVE PLOTS' ,title)
        elif docs.type=='booked': 
            sheet.write('C1:D1', 'SITARA GREEN CITY' ,title)
            sheet.write('C2:D2', 'DETAIL OF BOOKED PLOTS' ,title)
        elif docs.type=='un_posted_sold': 
            sheet.write('C1:D1', 'SITARA GREEN CITY' ,title)
            sheet.write('C2:D2', 'DETAIL OF SOLD PLOTS' ,title)
        elif docs.type=='posted_sold': 
            sheet.write('C1:D1', 'SITARA GREEN CITY' ,title)
            sheet.write('C2:D2', 'DETAIL OF ALL PLOTS' ,title)
            
        
        sheet.set_column(1, 1, 20)
        sheet.set_column(2, 2, 20)
        sheet.set_column(3, 3, 20)
        sheet.set_column(4, 4, 20)
        sheet.set_column(5, 5, 20)
        sheet.set_column(6, 6, 20)   
        sheet.set_column(7, 7, 20)   
        sheet.set_column(8, 8, 20)   
        sheet.set_column(9, 9, 20)   
        sheet.set_column(10, 10, 20)   
        sheet.set_column(11, 11, 20)   
        sheet.set_column(12, 12, 20)   
        sheet.set_column(13, 13, 20) 
        sheet.set_column(14, 14, 20) 
        sheet.set_column(15, 15, 30)   
        plots_detail = self.env['product.product'].search([]) 
        if docs.type=='available': 
            plots_detail = self.env['product.product'].search([('state','=','available')])
        if docs.type=='unconfirm': 
            plots_detail = self.env['product.product'].search([('state','=','unconfirm')])    
        if docs.type=='reserved': 
            plots_detail = self.env['product.product'].search([('state','=','reserved'),('booking_validity','!=',False)]) 
        if docs.type=='booked': 
            plots_detail = self.env['product.product'].search([('state','=','booked'),('date_validity','!=',False)])
        if docs.type=='un_posted_sold': 
            plots_detail = self.env['product.product'].search([('state','in', ('un_posted_sold', 'posted_sold'))])
        if docs.type=='posted_sold': 
            plots_detail = self.env['product.product'].search([('state','in', ('reserved','booked','un_posted_sold','posted_sold'))])    
        col_no = 0    
        sheet.write(2, col_no, 'SR.NO', header_row_style)
        col_no += 1  
        sheet.write(2, col_no, 'PLOT STATUS', header_row_style)
        col_no += 1  
        if docs.type!='available': 
            sheet.write(2, col_no, 'NAME OF BUYER',header_row_style)
            col_no += 1 
            sheet.write(2, col_no, 'PHONE OF BUYER',header_row_style)
            col_no += 1 
            sheet.write(2, col_no, 'MOBILE OF BUYER',header_row_style)
            col_no += 1 
        sheet.write(2, col_no, 'PLOT NO.',header_row_style)
        col_no += 1  
        sheet.write(2, col_no, "CATEGORY",header_row_style)
        col_no += 1  
        sheet.write(2, col_no, 'SIZE',header_row_style) 
        col_no += 1 
        if docs.type in ('reserved', 'booked', 'un_posted_sold'):
            sheet.write(2, col_no, "ADVANCE AMOUNT RECEIVED",header_row_style)
            col_no += 1  
            sheet.write(2, col_no, "% OF AMOUNT RECEIVED",header_row_style)
            col_no += 1  
        if docs.type in ('unconfirm', 'reserved'): 
            sheet.write(2, col_no, 'DATE OF RESERVATION',header_row_style)
            col_no += 1 
            sheet.write(2, col_no, "VALIDITY",header_row_style)
            col_no += 1  
        sheet.write(2, col_no, "PHASE",header_row_style)
        if docs.type =='posted_sold':
            sheet.write(2, col_no, 'PHASE',header_row_style)
            col_no += 1
            sheet.write(2, col_no, 'TOTAL AMOUNT',header_row_style)
            col_no += 1 
            sheet.write(2, col_no, "AMOUNT RECEIVED TO-DATE",header_row_style)
            col_no += 1
            sheet.write(2, col_no, "BALANCE DUE AMOUNT",header_row_style)
            col_no += 1
            sheet.write(2, col_no, "OVERDUE AMOUNT",header_row_style)
            col_no += 1
            sheet.write(2, col_no, "OVERDUE DAYS",header_row_style)
            col_no += 1
            sheet.write(2, col_no, "Due Date",header_row_style)
            col_no += 1
            sheet.write(2, col_no, "REMARKS",header_row_style)
            col_no += 1
            
        col_no = 0  
        
        row = 3
        sr_no = 1
        total_plot_area_marla=0
        total_adv_amount_received=0
        total_list_price=0
        total_overdue_days = 0
        total_overdue_days_amount = 0
        total_amount_paid = 0
        total_amount_residual = 0
        for plt in plots_detail:
            col_no=0
            adv_amount_received=0
            amt_percent_received=0
            for amt_receive in plt.payment_ids:
                adv_amount_received += amt_receive.amount
            amt_percent_received =  (adv_amount_received/plt.list_price if plt.list_price>0 else 1) * 100 
            sheet.write(row, col_no, str(sr_no), format2)
            col_no += 1 
            plot_status=''
            if plt.state=='available':
                plot_status='Available'
            elif plt.state=='unconfirm':
                plot_status='Un-Confirm'
            elif plt.state=='reserved':
                plot_status='Reserved'
            elif plt.state=='booked':
                plot_status='Booked'
            elif plt.state=='un_posted_sold':
                plot_status='Alloted'
            elif plt.state=='posted_sold':
                plot_status='Posted Sold'
                
            sheet.write(row, col_no, str(plot_status), format2)
            col_no += 1
            if docs.type!='available': 
                sheet.write(row, col_no, str(plt.partner_id.name if plt.partner_id else ' '), format2)
                col_no += 1
                sheet.write(row, col_no, str(plt.partner_id.phone if plt.partner_id.phone else ' '), format2)
                col_no += 1
                sheet.write(row, col_no, str(plt.partner_id.mobile if plt.partner_id.mobile else ' '), format2)
                col_no += 1
            sheet.write(row, col_no, str(plt.name), format2)
            col_no += 1
            sheet.write(row, col_no, str(plt.categ_id.name), format2)
            col_no += 1
            sheet.write(row, col_no, str(round(plt.plot_area_marla,2)), format2) 
            total_plot_area_marla += plt.plot_area_marla
            col_no += 1
            if docs.type in ('reserved', 'booked', 'un_posted_sold'): 
                sheet.write(row, col_no, '{0:,}'.format(int(round(adv_amount_received))), format2)
                total_adv_amount_received += adv_amount_received
                col_no += 1
                sheet.write(row, col_no, round(amt_percent_received,4), format2)
                col_no += 1
            if docs.type in ('unconfirm', 'reserved'): 
                sheet.write(row, col_no, str(plt.date_reservation), format2)
                col_no += 1
                sheet.write(row, col_no, str(plt.date_validity), format2)
                col_no += 1
            if docs.type =='posted_sold':
                sheet.write(row, col_no, str(plt.property_location_id.location_id.name), format2)
                col_no += 1
                sheet.write(row, col_no, '{0:,}'.format(int(round(plt.list_price))), format2)
                total_list_price += plt.list_price
                col_no += 1
                sheet.write(row, col_no, '{0:,}'.format(int(round(plt.amount_paid))), format2)
                total_amount_paid += plt.amount_paid 
                col_no += 1
                sheet.write(row, col_no, '{0:,}'.format(int(round(plt.amount_residual))), format2)
                total_amount_residual += plt.amount_residual
                col_no += 1
                overdue_days = 0
                overdue_days_amount = 0
                remarks = ''
                due_date_report= ''
                if plt.booking_validity:
                    if plt.state=='reserved' and fields.date.today() > plt.booking_validity:
                        overdue_days = (fields.date.today() - plt.booking_validity).days
                        overdue_days_amount = plt.booking_amount - plt.amount_paid
                        due_date_report = plt.booking_validity
                        remarks = 'Booking Amount Overdue'
                if plt.date_validity:
                    if plt.state=='booked' and fields.date.today() > plt.date_validity:
                        overdue_days = (fields.date.today() - plt.date_validity).days
                        overdue_days_amount = (plt.allottment_amount + plt.booking_amount) - plt.amount_paid  
                        due_date_report = plt.date_validity 
                        remarks = 'Allotment Amount Overdue'
                if plt.booking_id.state=='sale':
                    for installment in plt.booking_id.installment_line_ids:
                        if fields.date.today() > installment.date and installment.remarks != 'Paid':
                            overdue_days = (fields.date.today() - installment.date).days
                            overdue_days_amount = installment.amount_residual - installment.amount_paid
                            due_date_report = installment.date
                            remarks = installment.name  
                                
                    
                sheet.write(row, col_no, '{0:,}'.format(int(round(overdue_days_amount))), format2)
                total_overdue_days_amount +=  overdue_days_amount
                col_no += 1
                sheet.write(row, col_no, '{0:,}'.format(int(round(overdue_days))), format2)
                total_overdue_days += overdue_days
                col_no += 1
                sheet.write(row, col_no, str(due_date_report), format2)
                col_no += 1
                sheet.write(row, col_no, str(remarks), format2)
                col_no += 1 
            if docs.type !='posted_sold':
                sheet.write(row, col_no, str(plt.property_location_id.location_id.name), format2)
                col_no += 0
                
            col_no =1
            sr_no += 1
            row += 1
            
        sheet.write(row, col_no, str(), header_row_style)
        col_no += 1
        if docs.type!='available': 
            sheet.write(row, col_no, str(), header_row_style)
            col_no += 1
            sheet.write(row, col_no, str(), header_row_style)
            col_no += 1
        sheet.write(row, col_no, str(), header_row_style)
        col_no += 1
        sheet.write(row, col_no, str(), header_row_style)
        col_no += 1
        sheet.write(row, col_no, str(round(total_plot_area_marla,2)), header_row_style) 
        col_no += 1
        if docs.type in ('reserved', 'booked', 'un_posted_sold'): 
            sheet.write(row, col_no, '{0:,}'.format(int(round(total_adv_amount_received))), header_row_style)
            col_no += 1
            sheet.write(row, col_no, str(), header_row_style)
            col_no += 1
        if docs.type in ('unconfirm', 'reserved'): 
            sheet.write(row, col_no, str(), header_row_style)
            col_no += 1
            sheet.write(row, col_no, str(), header_row_style)
            col_no += 1
        if docs.type =='posted_sold':
            sheet.write(row, col_no, str(), header_row_style)
            col_no += 1
            sheet.write(row, col_no, '{0:,}'.format(int(round(total_list_price))), header_row_style)
            col_no += 1
            sheet.write(row, col_no, '{0:,}'.format(int(round(total_amount_paid))), header_row_style)
            col_no += 1
            sheet.write(row, col_no, '{0:,}'.format(int(round(total_amount_residual))), header_row_style)
            col_no += 1
            sheet.write(row, col_no, '{0:,}'.format(int(round(total_overdue_days_amount))), header_row_style)
            col_no += 1
            sheet.write(row, col_no, '{0:,}'.format(int(round(total_overdue_days))), header_row_style)
            col_no += 1
            
        if docs.type !='posted_sold':
            sheet.write(row, col_no, str(), header_row_style)
            col_no += 0    
            
                
                
            