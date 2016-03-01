[['date_invoice','=',time.strftime('%Y-%m-%d')]]


update account_voucher v
set amount = (select sum(vl.amount) from account_voucher_line vl
where v.state = 'draft' and v.id = vl.voucher_id and v.amount < '0.0001'
group by v.id, vl.id)




UPDATE  account_voucher v
SET     amount = p.amount
FROM    (
        SELECT  voucher_id, SUM(amount) AS amount
        FROM    account_voucher_line
        GROUP BY
                voucher_id
        ) p
WHERE   v.id = p.voucher_id and v.state = 'draft'


date_format = '%Y-%m-%d'

joining_date = '2013-08-23'
current_date = (datetime.today()).strftime(date_format)

d1 = datetime.strptime(joining_date, date_format).date()
d2 = datetime.strptime(current_date, date_format).date()
r = relativedelta(d2,d1)

print r.years
print r.months
print r.days


#object.write({'smslog' : time.strftime('%Y-%m-%d %H:%M:%S',time.gmtime(time.time()+7*24*3600))})
#object.write({'smslog' : time.strftime('%Y-%m-%d %H:%M:%S',time.gmtime(time.time()))})
datetime.datetime.now().time()
object.write({'smslog' : datetime.datetime.now()})


    action = {
        'type': 'ir.actions.client',
        'tag': 'action_warn',
        'name': 'Incomplete Date',
        'params': {
           'title': 'SMS Notification Cancelled',
           'text':  'Please make sure to put JOB, EMPLOYER, TRIP, TRIP JOB LOCATION, CONTACT OF LOCAL BRANCH',
           'sticky': True
        }
    }


    if object.trjob_id and object.partner_id and object.trip_id.job_country_id and company_id.phone
    
    

thelink = "http://api.clickatell.com/http/sendmsg?password=YNZYHCMDTHaCDO&user=gagamba1&api_id=3502830&"

mobile = (object.mobile).strip() if object.mobile else ''

#offer received
if mobile and not object.datesms_ro:
    sysm = {}
    sysm['model'] = 'tapplicant'
    sysm['type'] = 'notification'
    sysm['subject'] = 'System SMS Sent: Offer Received'
    sysm['res_id'] = object.id
    sysm['author_id'] =  user.id
    sysm['body'] = 'Hi ' + object.name + ', u r selected as ' + (object.trjob_id.name or 'employee') + ' by ' + (object.partner_id.name or 'our Client') + ' to ' + (object.trip_id.job_country_id.name or 'their job location') + ', contact us at ' + (object.company_id.phone or 'our local branch') + '. Keep offer details confidential. Contact JobsGlobal.com to Sign contract ASAP. Auto MSG. do not reply'
    env['mail.message'].create(sysm)
    object.write({'datesms_ro' : datetime.datetime.now()})

#to sign offer
date_format = '%Y-%m-%d'
joining_date = (object.create_date.split(' '))[0]
current_date = (datetime.datetime.today()).strftime(date_format)
d1 = datetime.datetime.strptime(joining_date, date_format).date()
d2 = datetime.datetime.strptime(current_date, date_format).date()
r = d2 - d1
if mobile and not object.hasoffersigned and not object.datesms_os and r.days > 7:
    sysm = {}
    sysm['model'] = 'tapplicant'
    sysm['type'] = 'notification'
    sysm['subject'] = 'System SMS Sent: Sign Offer'
    sysm['res_id'] = object.id
    sysm['author_id'] =  user.id
    sysm['body'] = 'Hi ' + object.name + ', Reminder yr job offer signing deadline ending, please visit us now to sign, offers not signed for over a week may get invalid. Contact JobsGlobal.com, Auto MSG. do not reply'
    env['mail.message'].create(sysm)
    object.write({'datesms_os' : datetime.datetime.now()})

#medical exam
if mobile and not object.datesms_am and object.clinic_id:
    sysm = {}
    sysm['model'] = 'tapplicant'
    sysm['type'] = 'notification'
    sysm['subject'] = 'System SMS Sent: Medical Exam'
    sysm['res_id'] = object.id
    sysm['author_id'] =  user.id
    sysm['body'] = 'Hi ' + object.name + ', Reminder to do ur job abroad medical exam b4 deadlines, if done already pls submit to us. Contact JobsGlobal.com. Auto MSG. do not reply'
    env['mail.message'].create(sysm)
    object.write({'datesms_am' : datetime.datetime.now()})

#endorsed for visa
if mobile and not object.datesms_ev and object.dateendorsedvisa:
    sysm = {}
    sysm['model'] = 'tapplicant'
    sysm['type'] = 'notification'
    sysm['subject'] = 'System SMS Sent: Endorsed for Visa'
    sysm['res_id'] = object.id
    sysm['author_id'] =  user.id
    sysm['body'] = 'Hi ' + object.name + ', Ur visa to ' + (object.partner_id.name or 'our Client') + ' sent for processing. Dont resign till visa issued, Never respond to any MONEY REQUEST by staff, deposit only to JobsGlobal official BDO account. Contact JobsGlobal.com, Auto MSG. do not reply'
    env['mail.message'].create(sysm)
    object.write({'datesms_ev' : datetime.datetime.now()})

#endorsed for visa and 2 weeks passed
date_format = '%Y-%m-%d'
joining_date = (object.datesms_ev.split(' '))[0]
d1 = datetime.datetime.strptime(joining_date, date_format).date()
r = d2 - d1
if mobile and not object.datesms_ef and object.dateendorsedvisa and not object.datevisareceived and r.days > 14:
    sysm = {}
    sysm['model'] = 'tapplicant'
    sysm['type'] = 'notification'
    sysm['subject'] = 'System SMS Sent: Waiting for Visa'
    sysm['res_id'] = object.id
    sysm['author_id'] =  user.id
    sysm['body'] = 'Hi ' + object.name + ', Ur visa still in process. May take a while, will update U if ready, dont resign till visa approved, Contact JobsGlobal.com, Auto MSG. do not reply'
    env['mail.message'].create(sysm)
    object.write({'datesms_ef' : datetime.datetime.now()})

#Visa Received
if mobile and not object.datesms_vr and object.datevisareceived:
    sysm = {}
    sysm['model'] = 'tapplicant'
    sysm['type'] = 'notification'
    sysm['subject'] = 'System SMS Sent: VISA Received'
    sysm['res_id'] = object.id
    sysm['author_id'] =  user.id
    sysm['body'] = 'Congrats ' + object.name + ', Visa for ' + (object.partner_id.name or 'our Client') + ' to ' + (object.trip_id.job_country_id.name or 'their job location') + ' is ready. Please contact ' + (object.company_id.phone or 'our local branch') + ' now. Remember, never respond to any money request except to official JobsGlobal BDO account. Auto MSG. do not reply'
    env['mail.message'].create(sysm)
    object.write({'datesms_vr' : datetime.datetime.now()})

#Gamca
if mobile and not object.datesms_gn and not object.gamcanotneeded and object.gamcaclinic:
    sysm = {}
    sysm['model'] = 'tapplicant'
    sysm['type'] = 'notification'
    sysm['subject'] = 'System SMS Sent: For Gamca'
    sysm['res_id'] = object.id
    sysm['author_id'] =  user.id
    sysm['body'] = 'Hi ' + object.name + ', pls do GAMCA medical exam b4 deadlines for ' + (object.partner_id.name or 'our Client') + ' visa, if done pls contact us at ' + (object.company_id.phone or 'our local branch') + '. Auto MSG. do not reply'
    env['mail.message'].create(sysm)
    object.write({'datesms_gn' : datetime.datetime.now()})

    
#Ticket
if mobile and not object.datesms_ct and object.dateticketissueclear:
    sysm = {}
    sysm['model'] = 'tapplicant'
    sysm['type'] = 'notification'
    sysm['subject'] = 'System SMS Sent: Cleared for Ticket'
    sysm['res_id'] = object.id
    sysm['author_id'] =  user.id
    sysm['body'] = 'Hi ' + object.name + ', Ur ticket to ' + (object.trip_id.job_country_id.name or 'Client job location') + ' was requested, be prepared for travelling soon once issued. Auto MSG. do not reply'
    env['mail.message'].create(sysm)
    object.write({'datesms_ct' : datetime.datetime.now()})

    
#Ticket
if mobile and not object.datesms_ti and object.flightdetails:
    sysm = {}
    sysm['model'] = 'tapplicant'
    sysm['type'] = 'notification'
    sysm['subject'] = 'System SMS Sent: Ticket Issued'
    sysm['res_id'] = object.id
    sysm['author_id'] =  user.id
    sysm['body'] = 'Hi ' + object.name + ', ticket for ' + (object.partner_id.name or 'our Client') + ' to '  + (object.trip_id.job_country_id.name or 'their job location') + ' On ' + (object.datetravel or '[ask travel date]') + ' to ' + (object.trip_id.job_country_id.name or 'their job location') + ', contact us at ' + (object.company_id.phone or 'our local branch') + ' 4 details. Auto MSG. do not reply'
    env['mail.message'].create(sysm)
    object.write({'datesms_ti' : datetime.datetime.now()})

    
#Travel
date_format = '%Y-%m-%d'
joining_date = (object.datesms_ev.split(' '))[0]
d1 = datetime.datetime.strptime(joining_date, date_format).date()
r = d2 - d1
if mobile and not object.datesms_tt and object.datetravel and r.days == 1:
    sysm = {}
    sysm['model'] = 'tapplicant'
    sysm['type'] = 'notification'
    sysm['subject'] = 'System SMS Sent: Travelling within 24 HOURS'
    sysm['res_id'] = object.id
    sysm['author_id'] =  user.id
    sysm['body'] = 'Hi ' + object.name + ', Reminder of Ur travel on ' + (object.datetravel or '[ask travel date]') + ', be in the airport 3 hours before flight to have time for travel processing. Have a safe trip and wish you all the best.'
    env['mail.message'].create(sysm)
    object.write({'datesms_tt' : datetime.datetime.now()})
   
    
    

#_____