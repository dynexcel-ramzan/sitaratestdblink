
# -*- coding: utf-8 -*-

from odoo import api, fields, models, _
from odoo.exceptions import UserError


class RegisterPayWizard(models.TransientModel):
    _name = "register.pay.wizard"
    _description = "Register Pay wizard"

    token_amount = fields.Float(string='Amount', required=True)
    partner_id = fields.Many2one('res.partner', string='Customer', required=True)
    processing_fee = fields.Boolean(string='Processing Fee Include') 
    processing_fee_submit = fields.Boolean(string='Processing Fee Submitted')
    membership_fee_submit = fields.Boolean(string='Membership Fee Submitted')
    remarks = fields.Char(string='Remarks')
    membership_fee = fields.Boolean(string='Membership Fee Include')
    date = fields.Date(string='Date', required=True, default=fields.date.today())
    allow_amount = fields.Float(string='Allow Amount')
    installment_id = fields.Many2one('order.installment.line', string='Installment')
    check_number = fields.Char(string='Check Number')
    type = fields.Selection([
        ('fee', 'Fee'),
        ('book', 'Booking'),
        ('allott', 'Allottment'),
        ('installment', 'Installment'),
        ], string='Type', required=True)
    
    journal_id = fields.Many2one('account.journal', string='Journal', required=True, domain=[('type','in',('bank','cash'))])
    sale_id = fields.Many2one('sale.order', string='Order')
    
    @api.onchange('installment_id')
    def onchange_installment(self):
        for line in self:
            if line.installment_id:
                line.token_amount = line.installment_id.amount_residual
    
    
    @api.constrains('amount_residual')
    def _check_state(self):
        for line in self:
            if line.amount_residual<=0:
                for order_line in line.order_line:
                    order_line.update({
                         'state':  'posted_sold',
                    })   
    
    def action_confirm(self):
        payment_amount=self.token_amount
        ext_payment_amount=self.token_amount
        batch_payment_list=[]
        total_advance_remaining_amt=self.sale_id.booking_amount_residual + self.sale_id.allotment_amount_residual
        if self.processing_fee==True:
            processing_fee_amount=0
            self.sale_id.update({
               'processing_fee_submit': True 
            })
            
            for o_line in self.sale_id.order_line:
                processing_fee_amount=o_line.product_id.categ_id.process_fee 
                if  processing_fee_amount > 0:
                    payment_amount = payment_amount - processing_fee_amount
                    vals = {
                     'partner_id': self.partner_id.id,
                     'date': self.date,
                     'journal_id': self.journal_id.id,
                     'amount': processing_fee_amount,
                     'ref': self.check_number,
                     'payment_type': 'inbound',
                     'order_id': self.sale_id.id,
                     'plot_id': o_line.product_id.id,
                     
                     'type': 'fee',
                     'processing_fee_submit': True,
                     }
                    record = self.env['account.payment'].sudo().create(vals)
                    record.action_post()
                    batch_payment_list.append(record.id)
        if self.membership_fee==True:
            membership_fee_amount=0
            self.sale_id.update({
               'membership_fee_submit': True 
            })
            for o_line in self.sale_id.order_line:
                membership_fee_amount=o_line.product_id.categ_id.allottment_fee
                if  membership_fee_amount > 0: 
                    payment_amount = payment_amount - membership_fee_amount
                    vals = {
                     'partner_id': self.partner_id.id,
                     'date': self.date,
                     'journal_id': self.journal_id.id,
                     'amount': membership_fee_amount,
                     'ref': self.check_number,
                     'payment_type': 'inbound',
                     'order_id': self.sale_id.id,
                     'plot_id': o_line.product_id.id,
                     'type': 'fee',
                     'membership_fee_submit': True,
                     }
                    record = self.env['account.payment'].sudo().create(vals)
                    record.action_post()
                    batch_payment_list.append(record.id)

        difference_amount = 0 
        reconcile_list = []
        for rorder in self.sale_id.order_line:
            rorder.product_id.product_tmpl_id.compute_amount_total()
            rorder_amount_residual = rorder.product_id.amount_residual
            devision_prct = (payment_amount/self.sale_id.amount_total) * rorder.price_subtotal
            if devision_prct > rorder_amount_residual:
                difference_amount +=  devision_prct - rorder_amount_residual 
                devision_prct = rorder_amount_residual
                reconcile_list.append(rorder.id)   
            vals = {
                'partner_id': self.partner_id.id,
                'date': self.date,
                'journal_id': self.journal_id.id,
                'amount': devision_prct,
                'remarks': self.remarks,
                'ref': self.check_number,
                'payment_type': 'inbound',
                'order_id': self.sale_id.id,
                'plot_id': rorder.product_id.id,
                'type': self.type,
                'installment_id': self.installment_id.id,
                }
            record_pay = self.env['account.payment'].sudo().create(vals)
            record_pay.action_post()
            batch_payment_list.append(record_pay.id)
            for intial_line in self.sale_id.order_line:
                if rorder.id==intial_line.id :                     
                    payment_list = []
                    for pay_line in intial_line.product_id.payment_ids:
                        payment_list.append(pay_line.id)
                    if record_pay:
                        payment_list.append(record_pay.id)
                    intial_line.product_id.payment_ids=payment_list
                    
        if difference_amount > 0:
            for diff_order in self.sale_id.order_line:
                if difference_amount > diff_order.product_id.amount_residual and diff_order.product_id.amount_residual > 0 and diff_order.id not in reconcile_list:
                    difference_amount =  difference_amount - diff_order.product_id.amount_residual 
                    
                    vals = {
                        'partner_id': self.partner_id.id,
                        'date': self.date,
                        'journal_id': self.journal_id.id,
                        'amount': diff_order.product_id.amount_residual,
                        'ref': self.check_number,
                        'remarks': self.remarks,
                        'payment_type': 'inbound',
                        'order_id': self.sale_id.id,
                        'plot_id': diff_order.product_id.id,
                        'type': self.type,
                        'installment_id': self.installment_id.id,
                        }
                    record_pay = self.env['account.payment'].sudo().create(vals)
                    record_pay.action_post()
                    batch_payment_list.append(record_pay.id)
                    for df_line in self.sale_id.order_line:
                        if diff_order.id==df_line.id :
                            payment_list = []
                            for pay_line in df_line.product_id.payment_ids:
                                payment_list.append(pay_line.id)
                            if record_pay:
                                payment_list.append(record_pay.id)
                            df_line.product_id.payment_ids=payment_list

                elif difference_amount <= diff_order.product_id.amount_residual and diff_order.product_id.amount_residual > 0 and diff_order.id not in reconcile_list:
                    vals = {
                        'partner_id': self.partner_id.id,
                        'date': self.date,
                        'journal_id': self.journal_id.id,
                        'amount': difference_amount,
                        'ref': self.check_number,
                        'remarks': self.remarks,
                        'payment_type': 'inbound',
                        'order_id': self.sale_id.id,
                        'plot_id': diff_order.product_id.id,
                        'plot_id': o_line.product_id.id,
                        'type': self.type,
                        'installment_id': self.installment_id.id,
                        }
                    record_pay = self.env['account.payment'].sudo().create(vals)
                    record_pay.action_post()
                    batch_payment_list.append(record_pay.id)
                    difference_amount =  0 
                    for diff_o_line in self.sale_id.order_line:
                        if diff_order.id==diff_o_line.id :
                            payment_list = []
                            for pay_line in diff_o_line.product_id.payment_ids:
                                payment_list.append(pay_line.id)
                            if record_pay:
                                payment_list.append(record_pay.id)
                            diff_o_line.product_id.payment_ids=payment_list
                
        remaining_amount = 0    
        advance_amount = (((self.sale_id.amount_total)/100) * 25)
        if advance_amount < self.sale_id.amount_paid:
            remaining_amount = ext_payment_amount - total_advance_remaining_amt
        if  remaining_amount > 0 and self.type in ('allott','book'):
            for installment_line in self.sale_id.installment_line_ids:
                if installment_line.amount_residual > 0:
                    if installment_line.amount_residual < remaining_amount:
                        installment_line.update({
                        'amount_paid': installment_line.amount_paid + installment_line.amount_residual,
                        'payment_date':self.date,
                        'remarks': 'Paid' ,
                        })    
                        installment_line.update({
                        'amount_residual': 0
                        })    
                    elif installment_line.amount_residual == remaining_amount:    
                        installment_line.update({
                        'amount_paid': installment_line.amount_paid + installment_line.amount_residual,
                        'payment_date':self.date,
                        'remarks': 'Paid' ,
                        })    
                        installment_line.update({
                        'amount_residual': 0
                        })
                        break
                    elif installment_line.amount_residual > remaining_amount:   
                        installment_line.update({
                        'amount_paid': installment_line.amount_paid + remaining_amount,
                        'payment_date':self.date,
                        'remarks': 'Partial Payment' ,
                        })    
                        installment_line.update({
                        'amount_residual': installment_line.amount_residual - remaining_amount
                        })
                        break

        if self.installment_id:            
            status= 'Partial Payment'
            installment_amount = self.installment_id.amount_residual - self.token_amount 
            if installment_amount > 0:
                self.installment_id.update({
                'amount_paid': self.installment_id.amount_paid + self.token_amount,
                'payment_date':self.date,
                'remarks': status ,
                })    
                self.installment_id.update({
                'amount_residual': self.installment_id.amount_residual - self.token_amount
                })
            elif installment_amount==0:
                self.installment_id.update({
                'amount_paid': self.installment_id.amount_paid + self.token_amount,
                'payment_date':self.date,
                'remarks': status ,
                })    
                self.installment_id.update({
                'amount_residual': self.installment_id.amount_residual - self.token_amount
                })
                self.installment_id.update({
                'remarks': 'Paid' ,
                }) 
            # group payment    
            elif installment_amount < 0:
                remaining_amount = self.token_amount - self.installment_id.amount_residual
                
                self.installment_id.update({
                'amount_paid': self.installment_id.amount_paid + self.installment_id.amount_residual,
                'payment_date':self.date,
                'remarks': 'Paid' ,
                })    
                self.installment_id.update({
                'amount_residual': 0
                })

                for installment_line in self.sale_id.installment_line_ids:
                    if installment_line.amount_residual > 0 and remaining_amount > 0:
                        if installment_line.amount_residual < remaining_amount:
                            installment_line.update({
                            'amount_paid': installment_line.amount_paid + installment_line.amount_residual,
                            'payment_date':self.date,
                            'remarks': 'Paid' ,
                            })    
                            installment_line.update({
                            'amount_residual': 0
                            })    
                        elif installment_line.amount_residual == remaining_amount: 
                            installment_line.update({
                             'amount_paid': installment_line.amount_paid + installment_line.amount_residual,
                             'payment_date':self.date,
                             'remarks': 'Paid' ,
                            })    
                            installment_line.update({
                            'amount_residual': 0
                            })
                            break
                        elif installment_line.amount_residual > remaining_amount: 

                            installment_line.update({
                            'amount_paid': installment_line.amount_paid + remaining_amount,
                            'payment_date':self.date,
                            'remarks': 'Partial Payment' ,
                            })    
                            installment_line.update({
                            'amount_residual': installment_line.amount_residual - remaining_amount
                            })
                            remaining_amount = 0
                            break

        batch_vals = {
            'batch_type': 'inbound',
            'journal_id': self.journal_id.id,
            'partner_id':  self.partner_id.id,
            'check_number':  self.check_number,
            'narration':  ' Customer Payments '+ str(self.token_amount) +' - '+ str(self.partner_id.name),  
            'order_id': self.sale_id.id,
            'date': self.date,
            'state': 'reconciled',
        } 
        batch=self.env['account.batch.payment'].create(batch_vals)
        batch.payment_ids=batch_payment_list
        batch.update({
           'state': 'reconciled',
        })
        self.sale_id._compute_property_amount()
        self.sale_id.action_confirm_booking()
        self.sale_id.action_register_allottment()                    
        self.sale_id._compute_property_amount()                    
