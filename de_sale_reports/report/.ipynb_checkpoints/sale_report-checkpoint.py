from odoo import models, fields, api, _
from  odoo import models
from odoo.exceptions import UserError
from dateutil.relativedelta import relativedelta
from datetime import datetime, timedelta


class PlotStatusXlS(models.AbstractModel):
    _name = 'report.de_sale_reports.acc_ledger_report_xlx'
    _description = 'Property Sale report'
    _inherit = 'report.report_xlsx.abstract'
    
    
    def generate_xlsx_report(self, workbook, data, lines):
        docs = self.env['acc.ledger.wizard'].browse(self.env.context.get('active_id'))
        sheet = workbook.add_worksheet('Property Sale Report')
        bold = workbook. add_format({'bold': True, 'align': 'center','bg_color': '#FFFF99','border': True})
        title = workbook.add_format({'bold': True, 'align': 'center', 'font_size': 20, 'bg_color': '#FFFF99', 'border': True})
        header_row_style = workbook.add_format({'bold': True, 'align': 'center', 'border':True})
        format2 = workbook.add_format({'align': 'center'})
        format3 = workbook.add_format({'align': 'center','bold': True,'border': True,})  
        
        plot_list = []
        plot_payments_list = self.env['account.payment'].search([('state','=','posted'),('date','>=',docs.date_from),('date','<=',docs.date_to)])
        for plt_paym in plot_payments_list:
            plot_list.append(plt_paym.plot_id.id)
            
        plots = self.env['product.product'].search([])
        plot_location_list = []
        plot_location = self.env['op.property.location'].search([])
        plot_categories = []
        uniq_location_list = []        
        plot_category = self.env['product.category'].search([('can_be_property','=',True)])
        for plt_categ in plot_category:
            plot_categories.append(plt_categ.id)
        for plt_loc in plot_location:
            if plt_loc.location_id:
                plot_location_list.append(plt_loc.location_id.id)
        uniq_location_list = set(plot_location_list)  
        uniq_category_list = set(plot_categories)
        
        sheet.set_column(1, 1, 20)
        sheet.set_column(2, 2, 20)
        sheet.set_column(3, 3, 20)
        sheet.set_column(4, 4, 20)
       
        sheet.write(2,0,'Phase', header_row_style)
        sheet.write(2,1 , 'Category',header_row_style)
        sheet.write(2,2 , 'No Of Plots',header_row_style)
        sheet.write(2,3 , "Total Marla's",header_row_style)
        sheet.write(2,4 , "Sale Price",header_row_style)
        row = 3
        all_grand_total_number_of_plot_price=0
        all_grand_total_number_of_marlas=0
        all_grand_total_number_of_plots=0
        
        for phase in uniq_location_list:
            phase_count=0
            grand_total_number_of_plots = 0
            grand_total_number_of_marlas = 0
            grand_total_number_of_plot_price = 0
            total_number_of_marlas = 0
            total_number_of_plots = 0
            plot_phase = self.env['op.property.location'].search([('id','=', phase)], limit=1)
            for categ in uniq_category_list:
                total_number_of_plots = 0
                total_number_of_plot_price = 0
                plot_category = self.env['product.category'].search([('id','=', categ)], limit=1)
                phase_plots = self.env['product.product'].search([('id','in',plot_list),('categ_id','=', plot_category.id),('property_location_id.location_id','=',plot_phase.id),('state' ,'not in',('available','unconfirm'))] )
                for pl in phase_plots:
                    total_number_of_plots += 1
                    total_number_of_marlas += pl.plot_area_marla
                    plot_payments = self.env['account.payment'].search([('plot_id','=',pl.id),('state','=','posted')])
                    for plt_pay in plot_payments:
                        total_number_of_plot_price += plt_pay.amount
                
                if phase_count==0:
                    sheet.write(row, 0, str(plot_phase.name), format2)
                    phase_count += 1
                else:
                    sheet.write(row, 0, str(), format2)
                sheet.write(row, 1, str(plot_category.name), format2) 
                sheet.write(row, 2, '{0:,}'.format(int(round(total_number_of_plots))), format2)
                grand_total_number_of_plots += total_number_of_plots
                sheet.write(row, 3, round(total_number_of_marlas,2), format2)
                grand_total_number_of_marlas += total_number_of_marlas
                sheet.write(row, 4, '{0:,}'.format(int(round(total_number_of_plot_price))), format2)
                grand_total_number_of_plot_price += total_number_of_plot_price
                row += 1
                
            sheet.write(row, 0, str(), header_row_style)
            sheet.write(row, 1, str(), header_row_style) 
            sheet.write(row, 2, '{0:,}'.format(int(round(grand_total_number_of_plots))),  header_row_style)
            all_grand_total_number_of_plots += grand_total_number_of_plots
            sheet.write(row, 3, round(grand_total_number_of_marlas,2),  header_row_style)
            all_grand_total_number_of_marlas += grand_total_number_of_marlas
            sheet.write(row, 4, '{0:,}'.format(int(round(grand_total_number_of_plot_price))),  header_row_style)
            all_grand_total_number_of_plot_price += grand_total_number_of_plot_price
            row += 1
            
            
        sheet.write(row, 0, 'Grand Total', header_row_style)
        sheet.write(row, 1, str(), header_row_style) 
        sheet.write(row, 2, '{0:,}'.format(int(round(all_grand_total_number_of_plots))),  header_row_style)
        sheet.write(row, 3, round(all_grand_total_number_of_marlas,2),  header_row_style)
        sheet.write(row, 4, '{0:,}'.format(int(round(all_grand_total_number_of_plot_price))),  header_row_style)
        row += 1     
            