from odoo import models, fields, api, _
from  odoo import models
from odoo.exceptions import UserError
from dateutil.relativedelta import relativedelta
from datetime import datetime, timedelta




class DealerReportXlS(models.AbstractModel):
    _name = 'report.de_property_report.dealer_xlx'
    _description = 'Dealer report'
    _inherit = 'report.report_xlsx.abstract'
    
    
    def generate_xlsx_report(self, workbook, data, lines):
        docs = self.env['dealer.report.wizard'].browse(self.env.context.get('active_id'))
        sheet = workbook.add_worksheet('Dealer Report')
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
        sheet.set_column(7, 7, 20)
        sheet.set_column(8, 8, 20)
        
        if docs.type=='summary':
            sheet.write('C1:D1', 'SITARA GREEN CITY' ,title)
            sheet.write('C2:D2', 'SUMMARY REPORT' ,title)
            sheet.write('B3:B3','Date From', header_row_style)
            sheet.write('C3:C3',docs.date_from.strftime('%d-%b-%Y'), header_row_style)
            sheet.write('D3:D3','Date To', header_row_style)
            sheet.write('E3:E3',docs.date_to.strftime('%d-%b-%Y'), header_row_style)
        
            sheet.write(2,0,'SR#', header_row_style)
            sheet.write(2,1 , 'DEALER',header_row_style)
            sheet.write(2,2, 'PHONE OF DEALER',header_row_style)
            sheet.write(2,3 , 'MOBILE OF DEALER',header_row_style)
            sheet.write(2,4 , 'NO OF PLOTS',header_row_style)
            sheet.write(2,5 , "TOTAL MARLAS",header_row_style)
            sheet.write(2,6 , 'TOTAL AMOUNT',header_row_style) 
            sheet.write(2,7 , 'AMOUNT RECEIVED',header_row_style)
            sheet.write(2,8 , 'AMOUNT DUE',header_row_style)
            total_plots_total_price = 0
            total_plots_total_price_received = 0
            gtotal_amount_residual = 0
            row = 3
            dealer_list = []
            dealer_plots = self.env['product.product'].search([('state','in',('unconfirm','reserved','booked','un_posted_sold','posted_sold')),('date_validity', '>=' , docs.date_from),('date_validity', '<=' , docs.date_to),('partner_id.active_dealer','=', True) ])
            for dealer in dealer_plots: 
                dealer_list.append(dealer.partner_id.id)  
            uniq_dealer_list = set(dealer_list)  
            summary_sr_no = 1
            for uniq_dealer in uniq_dealer_list:
                dealer_plots_details = self.env['product.product'].search([('state','in',('unconfirm','reserved','booked','un_posted_sold','posted_sold')),('date_validity', '>=' , docs.date_from),('date_validity', '<=' , docs.date_to),('partner_id','=', uniq_dealer) ])
                dealer_vals = self.env['res.partner'].search([('id','=',uniq_dealer)], limit=1)
                number_of_plots = 0
                number_of_plots_marlas = 0
                plots_total_price = 0
                plots_total_price_received = 0
                total_amount_residual = 0
                for plt in dealer_plots_details:
                    number_of_plots += 1 
                    number_of_plots_marlas += plt.plot_area_marla  
                    plots_total_price += plt.list_price 
                    plots_total_price_received += plt.amount_paid
                    total_amount_residual += plt.amount_residual    
                sheet.write(row,0, summary_sr_no , format2)
                sheet.write(row,1 , str(dealer_vals.name), format2)
                sheet.write(row,2 , str(dealer_vals.mobile), format2)
                sheet.write(row,3 , str(dealer_vals.phone), format2)
                sheet.write(row,4 , str(number_of_plots), format2)
                sheet.write(row,5 , str(round(number_of_plots_marlas,2)), format2)
                sheet.write(row,6 , str('{0:,}'.format(int(round(plots_total_price)))), format2) 
                total_plots_total_price += plots_total_price
                sheet.write(row,7 , str('{0:,}'.format(int(round(plots_total_price_received)))), format2)
                total_plots_total_price_received += plots_total_price_received
                sheet.write(row,8 , str('{0:,}'.format(int(round(total_amount_residual)))), format2)
                gtotal_amount_residual += total_amount_residual
                summary_sr_no += 1
                row += 1
            sheet.write(row,0,  str('TOTAL'), header_row_style)
            sheet.write(row,1 , str(),header_row_style)
            sheet.write(row,2 , str(),header_row_style)
            sheet.write(row,3 , str(),header_row_style)
            sheet.write(row,4 , str(),header_row_style)
            sheet.write(row,5 , str(),header_row_style)    
            sheet.write(row,6 , str('{0:,}'.format(int(round(total_plots_total_price)))),header_row_style)
            sheet.write(row,7 , str('{0:,}'.format(int(round(total_plots_total_price_received)))),header_row_style)
            sheet.write(row,8 , str('{0:,}'.format(int(round(gtotal_amount_residual)))),header_row_style)
            
        elif  docs.type=='detail':
            row = 3
            sheet.write('C1:D1', 'SITARA GREEN CITY' ,title)
            sheet.write('C2:D2', 'DETAIL REPORT' ,title)
            sheet.write('B3:B3','Date From', header_row_style)
            sheet.write('C3:C3',docs.date_from.strftime('%d-%b-%Y'), header_row_style)
            sheet.write('D3:D3','Date To', header_row_style)
            sheet.write('E3:E3',docs.date_to.strftime('%d-%b-%Y'), header_row_style)
        
            sheet.write(2,0,  'SR#', header_row_style)
            sheet.write(2,1 , 'DEALER',header_row_style)
            sheet.write(2,2 , 'DEALER PHONE',header_row_style)
            sheet.write(2,3 , 'DEALER CONTACT',header_row_style)
            sheet.write(2,4 , 'PLOT',header_row_style)
            sheet.write(2,5 , "TOTAL AMOUNT",header_row_style)
            sheet.write(2,6, 'AMOUNT RECEIVED',header_row_style)
            sheet.write(2,7 , 'AMOUNT DUE',header_row_style)
            sheet.write(2,8 , 'REMARKS',header_row_style)

            dealer_plots = self.env['product.product'].search([('state','in',('unconfirm','reserved','booked','un_posted_sold','posted_sold')),('date_validity', '>=' , docs.date_from),('date_validity', '<=' , docs.date_to),('partner_id.active_dealer','=', True) ]) 
            detail_sr_no = 1
            total_price_detail = 0
            total_amount_paid = 0
            total_amount_residual = 0
            for plt_d in dealer_plots:
                sheet.write(row,0,  str(detail_sr_no), format2)
                sheet.write(row,1 , str(plt_d.partner_id.name),format2)
                sheet.write(row,2 , str(plt_d.partner_id.phone),format2)
                sheet.write(row,3 , str(plt_d.partner_id.mobile),format2)
                sheet.write(row,4 , str(plt_d.name),format2)
                sheet.write(row,5 , str('{0:,}'.format(int(round(plt_d.list_price)))),format2)
                total_price_detail += plt_d.list_price
                sheet.write(row,6 , str('{0:,}'.format(int(round(plt_d.amount_paid)))),format2)
                total_amount_paid += plt_d.amount_paid
                sheet.write(row,7 , str('{0:,}'.format(int(round(plt_d.amount_residual)))),format2)
                total_amount_residual += plt_d.amount_residual
                sheet.write(row,8 , str(),format2)
                detail_sr_no += 1
                row += 1
                
            sheet.write(row,0,  str('TOTAL'), header_row_style)
            sheet.write(row,1 , str(),header_row_style)
            sheet.write(row,2 , str(),header_row_style)
            sheet.write(row,3 , str(),header_row_style)
            sheet.write(row,4 , str(),header_row_style)
            sheet.write(row,5 , str('{0:,}'.format(int(round(total_price_detail)))),header_row_style)
            sheet.write(row,6 , str('{0:,}'.format(int(round(total_amount_paid)))),header_row_style)
            sheet.write(row,7 , str('{0:,}'.format(int(round(total_amount_residual)))),header_row_style)
            sheet.write(row,8 , str(),header_row_style)
            