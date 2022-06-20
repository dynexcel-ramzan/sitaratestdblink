from odoo import models, fields, api, _
from  odoo import models
from odoo.exceptions import UserError
from dateutil.relativedelta import relativedelta
from datetime import datetime, timedelta




class AdvanceReceivableXlS(models.AbstractModel):
    _name = 'report.de_property_report.adv_receive_xlx'
    _description = 'Advance Receivable report'
    _inherit = 'report.report_xlsx.abstract'
    
    
    def generate_xlsx_report(self, workbook, data, lines):
        docs = self.env['advance.receivable.wizard'].browse(self.env.context.get('active_id'))
        sheet = workbook.add_worksheet('Forcast Receivables Report')
        bold = workbook. add_format({'bold': True, 'align': 'center','bg_color': '#FFFF99','border': True})
        title = workbook.add_format({'bold': True, 'align': 'center', 'font_size': 14, 'border': True})
        header_row_style = workbook.add_format({'bold': True, 'align': 'center', 'border':True})
        format2 = workbook.add_format({'align': 'center'})
        format3 = workbook.add_format({'align': 'center','bold': True,'border': True,})                
        sheet.set_column(1, 1, 20)
        sheet.set_column(2, 2, 20)
        sheet.set_column(3, 3, 25)
        sheet.set_column(4, 4, 30)
        sheet.set_column(5, 5, 20)
        sheet.set_column(6, 6, 35)
        
        if docs.type=='date_wise_paid':
            sheet.write('C1:D1', 'SITARA GREEN CITY' ,title)
            sheet.write('C2:D2', 'MONTHLY DATE WISE RECEIVED' ,title)
            sheet.write('B3:B3','Date From', header_row_style)
            sheet.write('C3:C3',docs.date_from.strftime('%d-%b-%Y'), header_row_style)
            sheet.write('D3:D3','Date To', header_row_style)
            sheet.write('E3:E3',docs.date_to.strftime('%d-%b-%Y'), header_row_style)
        if docs.type=='date_wise':
            sheet.write('C1:D1', 'SITARA GREEN CITY' ,title)
            sheet.write('C2:D2', 'MONTHLY DATE WISE RECEIVABLES' ,title)
            sheet.write('B3:B3','Date From', header_row_style)
            sheet.write('C3:C3',docs.date_from.strftime('%d-%b-%Y'), header_row_style)
            sheet.write('D3:D3','Date To', header_row_style)
            sheet.write('E3:E3',docs.date_to.strftime('%d-%b-%Y'), header_row_style)
        if docs.type=='month':
            sheet.write('B1:C1', 'SITARA GREEN CITY' ,title)
            sheet.write('B2:C2', 'MONTH WISE RECEIVABLES' ,title) 
            sheet.write('A3:A3','Month', header_row_style)
            sheet.write('B3:B3','FROM: '+docs.date_from.strftime('%b-%Y'), header_row_style)
            sheet.write('C3:C3','To: '+docs.date_to.strftime('%b-%Y'), header_row_style)
        if docs.type=='year':
            sheet.write('B1:C1', 'SITARA GREEN CITY' ,title)
            sheet.write('B2:C2', 'YEAR WISE RECEIVABLES' ,title)
            sheet.write('A3:A3','YEAR', header_row_style)
            sheet.write('B3:B3','FROM: '+docs.date_from.strftime('%Y'), header_row_style)
            sheet.write('C3:C3','TO: '+docs.date_to.strftime('%Y'), header_row_style)
        
        date_wise_receivables = []
        monthly_receivables = []
        yearly_receivables = []
        """
        unconfirm_plot_list = self.env['product.product'].search([('state','=','unconfirm'),('booking_validity', '>=' , docs.date_from),('booking_validity', '<=' , docs.date_to) ])
        for unconf_plot in unconfirm_plot_list:
            line_vals = {
                'date':  unconf_plot.booking_validity,
                'plot_no':  unconf_plot.name , 
                'amount':   unconf_plot.booking_amount ,
                'remarks': '' ,
            }
            date_wise_receivables.append(line_vals)
            
        reserve_plot_list = self.env['product.product'].search([('state','=','reserved'),('booking_validity', '>=' , docs.date_from),('booking_validity', '<=' , docs.date_to) ])
        for reserve_plot in reserve_plot_list:  
            if not reserve_plot.booking_id:
                token_amt = reserve_plot.booking_amount - reserve_plot.amount_paid
                line_vals = {
                    'date':  reserve_plot.booking_validity,
                    'plot_no':  reserve_plot.name , 
                    'amount':  token_amt if token_amt > 0 else 0,
                    'remarks': '' ,
                }
                date_wise_receivables.append(line_vals)                
            elif reserve_plot.booking_id:
                line_vals = {
                    'date':  reserve_plot.booking_validity,
                    'plot_no':  reserve_plot.name , 
                    'amount':  reserve_plot.booking_id.booking_amount_residual,
                    'remarks': '' ,
                }
                date_wise_receivables.append(line_vals)
        """        
        booked_plot_list = self.env['product.product'].search([('state','in',('booked','un_posted_sold')),('date_validity', '>=' , docs.date_from),('date_validity', '<=' , docs.date_to) ])
        for book_plot in booked_plot_list:  
            if book_plot.booking_id:
                if book_plot.booking_id.allotment_amount_residual > 0:
                    line_vals = {
                        'date':  book_plot.date_validity ,
                        'plot_no': book_plot.name , 
                        'amount':  book_plot.booking_id.allotment_amount_residual ,
                        'remarks': 'Allotment Amount Residual' ,
                    }
                    date_wise_receivables.append(line_vals)
                    
        plot_installment_list = self.env['product.product'].search([('state','in',('booked','un_posted_sold'))])
        for plot_installment in plot_installment_list:  
            if plot_installment.booking_id:
                if plot_installment.booking_id.installment_amount_residual > 0:
                    for installment in plot_installment.booking_id.installment_line_ids:
                        if installment.date >= docs.date_from and installment.date <= docs.date_to and installment.remarks!='Paid' and installment.amount_residual > 0:
                            line_vals = {
                                'date':  installment.date ,
                                'plot_no': plot_installment.name , 
                                'amount':  installment.amount_residual ,
                                'remarks': installment.name ,
                            }
                            date_wise_receivables.append(line_vals)            
         
        if  docs.type=='date_wise_paid':
            paid_booked_plot_list = self.env['product.product'].search([('state','in',('booked','un_posted_sold')),('date_validity', '>=' , docs.date_from),('date_validity', '<=' , docs.date_to) ])
            date_wise_receivables = []
            for paid_book_plot in paid_booked_plot_list:
                total_paid_amount = 0
                for paid_payment in paid_book_plot.payment_ids:
                    if paid_payment.date >= docs.date_from and  paid_payment.date <= docs.date_to:
                        total_paid_amount += paid_payment.amount
                if  total_paid_amount > 0:       
                    paid_line_vals = {
                        'date':  paid_payment.date ,
                        'plot_no': paid_book_plot.name , 
                        'amount':  total_paid_amount ,
                        'remarks': 'Paid Amount on '+str(paid_payment.date ) ,
                    }
                    date_wise_receivables.append(paid_line_vals)
            
        if  docs.type=='month':
            month_list = []
            for monthly in date_wise_receivables:
                month_list.append(monthly['date'].month) 
            uniq_month_list = set(month_list)
            for uniq_month in uniq_month_list:
                period = ''
                mothly_total_amt = 0
                for monthly_receive in date_wise_receivables:
                    if monthly_receive['date'].month==uniq_month:
                        period=monthly_receive['date'].strftime('%b-%Y')
                        mothly_total_amt += monthly_receive['amount']
                month_vals = {
                    'date':  '' ,
                    'plot_no': '' ,
                    'period': period,
                    'amount':  mothly_total_amt ,
                    'remarks': '' ,
                }
                monthly_receivables.append(month_vals)
            date_wise_receivables = monthly_receivables    
                
        if  docs.type=='year':
            year_list = []
            yearly_receivables = []
            for monthly in date_wise_receivables:
                year_list.append(monthly['date'].year) 
            uniq_year_list = set(year_list)
            for uniq_year in uniq_year_list:
                period = ''
                yearly_total_amt = 0
                for yearly_receive in date_wise_receivables:
                    if yearly_receive['date'].year==uniq_year:
                        period=yearly_receive['date'].strftime('%Y')
                        yearly_total_amt += yearly_receive['amount']
                year_vals = {
                    'date':  '' ,
                    'plot_no': '' ,
                    'period': period,
                    'amount':  yearly_total_amt ,
                    'remarks': '' ,
                }
                yearly_receivables.append(year_vals)
            date_wise_receivables = yearly_receivables
            
        col_no=0
        sheet.write(3,col_no,  'SR.NO', header_row_style)
        col_no += 1
        if docs.type in ('date_wise','date_wise_paid'):
            sheet.write(3,col_no , 'DATE',  header_row_style)
            col_no += 1        
            sheet.write(3,col_no , 'PLOT NO.', header_row_style)
            col_no += 1
        if  docs.type=='month':
            sheet.write(3,col_no , 'MONTH',  header_row_style)
            col_no += 1
        if  docs.type=='year':
            sheet.write(3,col_no , 'YEAR',  header_row_style)
            col_no += 1    
            
        sheet.write(3,col_no , "AMOUNT",  header_row_style)
        col_no += 1
        if docs.type in ('date_wise','date_wise_paid'):
            sheet.write(3,col_no , 'REMARKS', header_row_style) 
            
        col_no = 0
        row = 4               
        sr_no = 1 
        total_amount = 0
        
        for receiv in date_wise_receivables:             
            sheet.write(row, col_no, str(sr_no), format2)
            col_no += 1
            if docs.type in ('date_wise','date_wise_paid'):
                sheet.write(row, col_no, str(receiv['date']), format2) 
                col_no += 1            
                sheet.write(row, col_no, str(receiv['plot_no']), format2)
                col_no += 1 
            if  docs.type in ('month','year'):
                sheet.write(row, col_no, str(receiv['period']), format2) 
                col_no += 1
                
            sheet.write(row, col_no, '{0:,}'.format(int(round(receiv['amount']))), format2)
            col_no += 1
            total_amount += float(receiv['amount'])
            if docs.type in ('date_wise','date_wise_paid'):
                sheet.write(row, col_no, str(receiv['remarks']), format2)                
            col_no = 0
            row += 1
            sr_no += 1
            
        sheet.write(row, col_no, str(), header_row_style)
        col_no += 1
        sheet.write(row, col_no, str(), header_row_style) 
        col_no += 1
        if docs.type in ('date_wise','date_wise_paid'):
            sheet.write(row, col_no, str(), header_row_style)
            col_no += 1
        sheet.write(row, col_no, str('{0:,}'.format(int(round(total_amount)))), header_row_style)
        col_no += 1
        if docs.type in ('date_wise','date_wise_paid'):
            sheet.write(row, col_no, str(), header_row_style) 
        col_no = 0
        row += 1
            