from odoo import models, fields, api, _
from  odoo import models
from odoo.exceptions import UserError
from dateutil.relativedelta import relativedelta
from datetime import datetime, timedelta


class PlotStatusXlS(models.AbstractModel):
    _name = 'report.de_property_report.status_report_xlx'
    _description = 'Plot Status report'
    _inherit = 'report.report_xlsx.abstract'
    
    
    def generate_xlsx_report(self, workbook, data, lines):
        docs = self.env['plot.status.wizard'].browse(self.env.context.get('active_id'))
        sheet = workbook.add_worksheet('Plot Status Report')
        bold = workbook. add_format({'bold': True, 'align': 'center','bg_color': '#FFFF99','border': True})
        title = workbook.add_format({'bold': True, 'align': 'center', 'font_size': 14, 'border': True})
        header_row_style = workbook.add_format({'bold': True, 'align': 'center', 'border':True})
        format2 = workbook.add_format({'align': 'center'})
        format3 = workbook.add_format({'align': 'center','bold': True,'border': True,})        
        plots = self.env['product.product'].search([])
        plot_location_list = []
        uniq_location_list = self.env['op.property.location'].search([('phase_location','=',True),('id','in',docs.phase_ids.ids)], order='sequence ASC')
        plot_categories = []
        plot_category = self.env['product.category'].search([('can_be_property','=',True)])
        for plt_categ in plot_category:
            plot_categories.append(plt_categ.id)          
        uniq_category_list = set(plot_categories)
        
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
        sheet.set_column(12, 14, 20)   
        sheet.set_column(13, 15, 20)     
        sheet.write('C1:D1', 'SITARA GREEN CITY' ,title)
        sheet.write('C2:D2', 'PLOTS STATUS DETAIL' ,title)
        sheet.write('E2:E2',  str(docs.date.strftime('%d-%b-%Y')) ,header_row_style)
            
        sheet.write(2,0,'Phase', header_row_style)
        sheet.write(2,1 , 'Category',header_row_style)
        sheet.write(2,2 , 'No Of Plots',header_row_style)
        sheet.write(2,3 , "Total Marla's",header_row_style)
        sheet.write(2,4 , 'Available Plots',header_row_style) 
        sheet.write(2,5 , "Available Plot Marla's",header_row_style)
        sheet.write(2,6 , 'Un-Confirm Plots',header_row_style)
        sheet.write(2,7 , "Un-Confirm Plots Marla's",header_row_style)
        sheet.write(2,8 , "Token Plots",header_row_style)
        sheet.write(2,9 , "Token Plots Marla's",header_row_style)
        sheet.write(2,10 , "Booked Plots", header_row_style)
        sheet.write(2,11 , "Booked Plots Marla's", header_row_style)
        sheet.write(2,12 , "Alloted Plots", header_row_style)
        sheet.write(2,13 , "Alloted Plots Marla's", header_row_style)
        sheet.write(2,14 , "All Sold Plots", header_row_style)
        sheet.write(2,15 , "All Sold Plots Marla's", header_row_style)
        row = 3
        phase_grand_total_number_of_plots = 0
        phase_grand_total_number_of_marlas = 0
        phase_grand_available_total_number_of_plots = 0
        phase_grand_available_total_number_of_marlas = 0
        phase_grand_unconfirm_total_number_of_plots = 0
        phase_grand_unconfirm_total_number_of_marlas = 0
        phase_grand_reserve_total_number_of_plots = 0
        phase_grand_reserve_total_number_of_marlas = 0
        phase_grand_booked_total_number_of_plots = 0
        phase_grand_booked_total_number_of_marlas = 0
        phase_grand_sold_total_number_of_plots = 0
        phase_grand_sold_total_number_of_marlas = 0
        phase_grand_all_sold_total_number_of_plots = 0
        phase_grand_all_sold_total_number_of_marlas = 0
        phase_count_total = 0
        for phase in uniq_location_list:
            phase_count_total += 1
            phase_count=0
            grand_total_number_of_plots = 0
            grand_total_number_of_marlas = 0
            grand_available_total_number_of_plots = 0
            grand_available_total_number_of_marlas = 0
            grand_unconfirm_total_number_of_plots = 0
            grand_unconfirm_total_number_of_marlas = 0
            grand_reserve_total_number_of_plots = 0
            grand_reserve_total_number_of_marlas = 0
            grand_booked_total_number_of_plots = 0
            grand_booked_total_number_of_marlas = 0
            grand_sold_total_number_of_plots = 0
            grand_sold_total_number_of_marlas = 0
            grand_all_sold_total_number_of_plots = 0
            grand_all_sold_total_number_of_marlas = 0 
            plot_phase = self.env['op.property.location'].search([('id','=', phase.id)], limit=1)
            for categ in uniq_category_list:
                total_number_of_plots = 0
                total_number_of_marlas = 0
                available_total_number_of_plots = 0
                available_total_number_of_marlas = 0
                unconfirm_total_number_of_plots = 0
                unconfirm_total_number_of_marlas = 0
                reserve_total_number_of_plots = 0
                reserve_total_number_of_marlas = 0
                booked_total_number_of_plots = 0
                booked_total_number_of_marlas = 0
                sold_total_number_of_plots = 0
                sold_total_number_of_marlas = 0 
                all_sold_total_number_of_plots = 0
                all_sold_total_number_of_marlas = 0 
                plot_category = self.env['product.category'].search([('id','=', categ)], limit=1)
                phase_plots = self.env['product.product'].search([('categ_id','=', plot_category.id),('property_location_id.location_id','=',plot_phase.id)] )
                for pl in phase_plots:
                    total_number_of_plots += 1
                    total_number_of_marlas += pl.plot_area_marla
                    if pl.state=='available':
                        available_total_number_of_plots += 1
                        available_total_number_of_marlas += pl.plot_area_marla
                    if pl.state=='unconfirm':
                        unconfirm_total_number_of_plots += 1
                        unconfirm_total_number_of_marlas += pl.plot_area_marla
                    if pl.state=='reserved':
                        reserve_total_number_of_plots += 1
                        reserve_total_number_of_marlas += pl.plot_area_marla 
                    if pl.state=='booked':
                        booked_total_number_of_plots += 1
                        booked_total_number_of_marlas += pl.plot_area_marla
                    if pl.state in ('un_posted_sold','posted_sold'):
                        sold_total_number_of_plots += 1
                        sold_total_number_of_marlas += pl.plot_area_marla
                    if pl.state in ('reserved','booked','un_posted_sold','posted_sold'):
                        all_sold_total_number_of_plots += 1
                        all_sold_total_number_of_marlas += pl.plot_area_marla  
                
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
                sheet.write(row, 4, '{0:,}'.format(int(round(available_total_number_of_plots))), format2)
                grand_available_total_number_of_plots += available_total_number_of_plots
                sheet.write(row, 5, round(available_total_number_of_marlas,2), format2) 
                grand_available_total_number_of_marlas += available_total_number_of_marlas
                sheet.write(row, 6, '{0:,}'.format(int(round(unconfirm_total_number_of_plots))), format2)
                grand_unconfirm_total_number_of_plots += unconfirm_total_number_of_plots
                sheet.write(row, 7, round(unconfirm_total_number_of_marlas,2), format2)
                grand_unconfirm_total_number_of_marlas += unconfirm_total_number_of_marlas
                sheet.write(row, 8, '{0:,}'.format(int(round(reserve_total_number_of_plots))), format2)
                grand_reserve_total_number_of_plots += reserve_total_number_of_plots
                sheet.write(row, 9, round(reserve_total_number_of_marlas,2), format2)
                grand_reserve_total_number_of_marlas += reserve_total_number_of_marlas
                sheet.write(row, 10, '{0:,}'.format(int(round(booked_total_number_of_plots))), format2)
                grand_booked_total_number_of_plots += booked_total_number_of_plots
                sheet.write(row, 11, round(booked_total_number_of_marlas,2), format2)
                grand_booked_total_number_of_marlas += booked_total_number_of_marlas
                sheet.write(row, 12, '{0:,}'.format(int(round(sold_total_number_of_plots))), format2)
                grand_sold_total_number_of_plots += sold_total_number_of_plots
                sheet.write(row, 13, round(sold_total_number_of_marlas,2), format2)
                grand_sold_total_number_of_marlas += sold_total_number_of_marlas
                sheet.write(row, 14, '{0:,}'.format(int(round(all_sold_total_number_of_plots))), format2)
                grand_all_sold_total_number_of_plots += all_sold_total_number_of_plots
                sheet.write(row, 15, round(all_sold_total_number_of_marlas,2), format2)
                grand_all_sold_total_number_of_marlas += all_sold_total_number_of_marlas
                row += 1
                
            
            sheet.write(row, 0, 'Total', header_row_style)
            sheet.write(row, 1, str(), header_row_style) 
            sheet.write(row, 2, '{0:,}'.format(int(round(grand_total_number_of_plots))), header_row_style)
            phase_grand_total_number_of_plots += grand_total_number_of_plots
            sheet.write(row, 3, round(grand_total_number_of_marlas,2), header_row_style)
            phase_grand_total_number_of_marlas += grand_total_number_of_marlas
            sheet.write(row, 4, '{0:,}'.format(int(round(grand_available_total_number_of_plots))), header_row_style)
            phase_grand_available_total_number_of_plots += grand_available_total_number_of_plots
            
            
            sheet.write(row, 5, round(grand_available_total_number_of_marlas,2), header_row_style)
            phase_grand_available_total_number_of_marlas += grand_available_total_number_of_marlas
            
            sheet.write(row, 6, '{0:,}'.format(int(round(grand_unconfirm_total_number_of_plots))), header_row_style)
            phase_grand_unconfirm_total_number_of_plots += grand_unconfirm_total_number_of_plots
            
            sheet.write(row, 7, round(grand_unconfirm_total_number_of_marlas,2), header_row_style)
            phase_grand_unconfirm_total_number_of_marlas += grand_unconfirm_total_number_of_marlas
            sheet.write(row, 8, '{0:,}'.format(int(round(grand_reserve_total_number_of_plots))), header_row_style)
            phase_grand_reserve_total_number_of_plots += grand_reserve_total_number_of_plots
            sheet.write(row, 9, round(grand_reserve_total_number_of_marlas,2), header_row_style)
            phase_grand_reserve_total_number_of_marlas += grand_reserve_total_number_of_marlas
            sheet.write(row, 10, '{0:,}'.format(int(round(grand_booked_total_number_of_plots))), header_row_style)
            phase_grand_booked_total_number_of_plots += grand_booked_total_number_of_plots
            sheet.write(row, 11, round(grand_booked_total_number_of_marlas,2), header_row_style)
            phase_grand_booked_total_number_of_marlas += grand_booked_total_number_of_marlas
            sheet.write(row, 12, '{0:,}'.format(int(round(grand_sold_total_number_of_plots))), header_row_style)
            phase_grand_sold_total_number_of_plots += grand_sold_total_number_of_plots
            sheet.write(row, 13, round(grand_sold_total_number_of_marlas,2), header_row_style)
            phase_grand_sold_total_number_of_marlas += grand_sold_total_number_of_marlas
            sheet.write(row, 14, '{0:,}'.format(int(round(grand_all_sold_total_number_of_plots))), header_row_style)
            phase_grand_all_sold_total_number_of_plots += grand_all_sold_total_number_of_plots
            sheet.write(row, 15, round(grand_all_sold_total_number_of_marlas,2), header_row_style)
            phase_grand_all_sold_total_number_of_marlas += grand_all_sold_total_number_of_marlas
            row += 1
         
        if phase_count_total > 1: 
            row += 1    
            sheet.write(row, 0, 'Grand Total', header_row_style)
            sheet.write(row, 1, str(), header_row_style) 
            sheet.write(row, 2, '{0:,}'.format(int(round(phase_grand_total_number_of_plots))), header_row_style)
            sheet.write(row, 3, round(phase_grand_total_number_of_marlas,2), header_row_style)
            sheet.write(row, 4, '{0:,}'.format(int(round(phase_grand_available_total_number_of_plots))), header_row_style) 
            
            sheet.write(row, 5, round(phase_grand_available_total_number_of_marlas,2), header_row_style) 
            sheet.write(row, 6, '{0:,}'.format(int(round(phase_grand_unconfirm_total_number_of_plots))), header_row_style)
            sheet.write(row, 7, round(phase_grand_unconfirm_total_number_of_marlas,2), header_row_style)
            sheet.write(row, 8, '{0:,}'.format(int(round(phase_grand_reserve_total_number_of_plots))), header_row_style)
            sheet.write(row, 9, round(phase_grand_reserve_total_number_of_marlas,2), header_row_style)
            sheet.write(row, 10, '{0:,}'.format(int(round(phase_grand_booked_total_number_of_plots))), header_row_style)
            sheet.write(row, 11, round(phase_grand_booked_total_number_of_marlas,2), header_row_style)
            sheet.write(row, 12, '{0:,}'.format(int(round(phase_grand_sold_total_number_of_plots))), header_row_style)
            sheet.write(row, 13, round(phase_grand_sold_total_number_of_marlas,2), header_row_style)
            sheet.write(row, 14, '{0:,}'.format(int(round(phase_grand_all_sold_total_number_of_plots))), header_row_style)
            sheet.write(row, 15, round(phase_grand_all_sold_total_number_of_marlas,2), header_row_style)
            row += 1    