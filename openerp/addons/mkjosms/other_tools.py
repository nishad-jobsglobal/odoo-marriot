SmsTrip = 16274,14708

def sendSMS(mobile, msg):
    thelink = "http://api.clickatell.com/http/sendmsg?password=YNZYHCMDTHaCDO&user=gagamba1&api_id=3502830&"
    ames={}
    ames['msg'] = msg
    ames['gateway_id'] = 1
    ames['mobile'] = mobile
    ames['name'] = thelink + "to=" + mobile + "&" + 'text=' + msg
    env['sms.smsclient.queue'].sudo().create(ames)
    

#start Process
if (object.trip_id or False) and object.trip_id.id in SmsTrip:
    thelink = "http://api.clickatell.com/http/sendmsg?password=YNZYHCMDTHaCDO&user=gagamba1&api_id=3502830&"
    mobile = (object.mobile).strip() if object.mobile else ''

    #offer received
    if mobile and not object.datesms_ro and not object.datetravel:
        sysm = {}
        sysm['model'] = 'tapplicant'
        sysm['type'] = 'notification'
        sysm['subject'] = 'System SMS Sent: Offer Received'
        sysm['res_id'] = object.id
        sysm['body'] = 'Hi ' + object.name + ', u r selected as ' + (object.trjob_id.name or 'employee') + ' by ' + (object.partner_id.name or 'Ur Employer') + ' to ' + (object.trip_id.job_country_id.name or 'their job location') + ', contact us at ' + (object.company_id.phone or 'our local branch') + '. Keep offer details confidential. Contact JobsGlobal.com to Sign contract ASAP. Auto MSG. do not reply'
        env['mail.message'].create(sysm)
        object.write({'datesms_ro' : datetime.datetime.now()})
        sendSMS(mobile, sysm['body'])

    #to sign offer
    date_format = '%Y-%m-%d'
    joining_date = (object.create_date.split(' '))[0]
    current_date = (datetime.datetime.today()).strftime(date_format)
    d1 = datetime.datetime.strptime(joining_date, date_format).date()
    d2 = datetime.datetime.strptime(current_date, date_format).date()
    r = d2 - d1
    if mobile and not object.hasoffersigned and not object.datesms_os and r.days > 7 and not object.datetravel:
        sysm = {}
        sysm['model'] = 'tapplicant'
        sysm['type'] = 'notification'
        sysm['subject'] = 'System SMS Sent: Sign Offer'
        sysm['res_id'] = object.id
        sysm['body'] = 'Hi ' + object.name + ', Reminder yr job offer signing deadline ending, please visit us now to sign, offers not signed for over a week may get invalid. Contact JobsGlobal.com, Auto MSG. do not reply'
        env['mail.message'].create(sysm)
        object.write({'datesms_os' : datetime.datetime.now()})
        sendSMS(mobile, sysm['body'])

    #medical exam
    if mobile and not object.datesms_am and object.clinic_id and not object.datetravel:
        sysm = {}
        sysm['model'] = 'tapplicant'
        sysm['type'] = 'notification'
        sysm['subject'] = 'System SMS Sent: Medical Exam'
        sysm['res_id'] = object.id
        sysm['body'] = 'Hi ' + object.name + ', Reminder to do ur job abroad medical exam b4 deadlines, if done already pls submit to us. Contact JobsGlobal.com. Auto MSG. do not reply'
        env['mail.message'].create(sysm)
        object.write({'datesms_am' : datetime.datetime.now()})
        sendSMS(mobile, sysm['body'])

    #endorsed for visa
    if mobile and not object.datesms_ev and object.dateendorsedvisa and not object.datetravel:
        sysm = {}
        sysm['model'] = 'tapplicant'
        sysm['type'] = 'notification'
        sysm['subject'] = 'System SMS Sent: Endorsed for Visa'
        sysm['res_id'] = object.id
        sysm['body'] = 'Hi ' + object.name + ', Ur visa to ' + (object.partner_id.name or 'Ur Employer') + ' sent for processing. Dont resign till visa issued, Never respond to any MONEY REQUEST by staff, deposit only to JobsGlobal official BDO account. Contact JobsGlobal.com, Auto MSG. do not reply'
        env['mail.message'].create(sysm)
        object.write({'datesms_ev' : datetime.datetime.now()})
        sendSMS(mobile, sysm['body'])

    #endorsed for visa and 2 weeks passed
    date_format = '%Y-%m-%d'
    joining_date = ((object.datesms_ev or current_date).split(' '))[0]
    d1 = datetime.datetime.strptime(joining_date, date_format).date()
    r = d2 - d1
    if mobile and not object.datesms_ef and object.dateendorsedvisa and not object.datevisareceived and r.days > 14 and not object.datetravel:
        sysm = {}
        sysm['model'] = 'tapplicant'
        sysm['type'] = 'notification'
        sysm['subject'] = 'System SMS Sent: Waiting for Visa'
        sysm['res_id'] = object.id
        sysm['body'] = 'Hi ' + object.name + ', Ur visa still in process. May take a while, will update U if ready, dont resign till visa approved, Contact JobsGlobal.com, Auto MSG. do not reply'
        env['mail.message'].create(sysm)
        object.write({'datesms_ef' : datetime.datetime.now()})
        sendSMS(mobile, sysm['body'])

    #Visa Received
    if mobile and not object.datesms_vr and object.datevisareceived and not object.datetravel:
        sysm = {}
        sysm['model'] = 'tapplicant'
        sysm['type'] = 'notification'
        sysm['subject'] = 'System SMS Sent: VISA Received'
        sysm['res_id'] = object.id
        sysm['body'] = 'Congrats ' + object.name + ', Visa for ' + (object.partner_id.name or 'Ur Employer') + ' to ' + (object.trip_id.job_country_id.name or 'their job location') + ' is ready. Please contact ' + (object.company_id.phone or 'our local branch') + ' now. Remember, never respond to any money request except to official JobsGlobal BDO account. Auto MSG. do not reply'
        env['mail.message'].create(sysm)
        object.write({'datesms_vr' : datetime.datetime.now()})
        sendSMS(mobile, sysm['body'])

    #Gamca
    if mobile and not object.datesms_gn and not object.gamcanotneeded and object.gamcaclinic and not object.datetravel:
        sysm = {}
        sysm['model'] = 'tapplicant'
        sysm['type'] = 'notification'
        sysm['subject'] = 'System SMS Sent: For Gamca'
        sysm['res_id'] = object.id
        sysm['body'] = 'Hi ' + object.name + ', pls do GAMCA medical exam b4 deadlines for ' + (object.partner_id.name or 'Ur Employer') + ' visa, if done pls contact us at ' + (object.company_id.phone or 'our local branch') + '. Auto MSG. do not reply'
        env['mail.message'].create(sysm)
        object.write({'datesms_gn' : datetime.datetime.now()})
        sendSMS(mobile, sysm['body'])

        
    #Ticket Cleared
    if mobile and not object.datesms_ct and object.dateticketissueclear and not object.flightdetails:
        sysm = {}
        sysm['model'] = 'tapplicant'
        sysm['type'] = 'notification'
        sysm['subject'] = 'System SMS Sent: Cleared for Ticket'
        sysm['res_id'] = object.id
        sysm['body'] = 'Hi ' + object.name + ', Ur ticket to ' + (object.trip_id.job_country_id.name or 'Client job location') + ' was requested, be prepared for travelling soon once issued. Auto MSG. do not reply'
        env['mail.message'].create(sysm)
        object.write({'datesms_ct' : datetime.datetime.now()})
        sendSMS(mobile, sysm['body'])

        
    #Ticket Issued
    if mobile and not object.datesms_ti and object.flightdetails:
        sysm = {}
        sysm['model'] = 'tapplicant'
        sysm['type'] = 'notification'
        sysm['subject'] = 'System SMS Sent: Ticket Issued'
        sysm['res_id'] = object.id
        sysm['body'] = 'Hi ' + object.name + ', ticket for ' + (object.partner_id.name or 'Ur Employer') + ' to '  + (object.trip_id.job_country_id.name or 'their job location') + ' On ' + (object.datetravel or '[ask travel date]') + ' to ' + (object.trip_id.job_country_id.name or 'their job location') + ', contact us at ' + (object.company_id.phone or 'our local branch') + ' 4 details. Auto MSG. do not reply'
        env['mail.message'].create(sysm)
        object.write({'datesms_ti' : datetime.datetime.now()})
        sendSMS(mobile, sysm['body'])


    #Travel
    date_format = '%Y-%m-%d'
    joining_date = ((object.datetravel or current_date).split(' '))[0]
    d1 = datetime.datetime.strptime(joining_date, date_format).date()
    r = d2 - d1
    if mobile and not object.datesms_tt and object.datetravel and r.days == 2:
        sysm = {}
        sysm['model'] = 'tapplicant'
        sysm['type'] = 'notification'
        sysm['subject'] = 'System SMS Sent: Travelling within 24 HOURS'
        sysm['res_id'] = object.id
        sysm['body'] = 'Hi ' + object.name + ', Reminder of Ur travel on ' + (object.datetravel or '[ask travel date]') + ', be in the airport 3 hours before flight to have time for travel processing. Have a safe trip and wish you all the best.'
        env['mail.message'].create(sysm)
        object.write({'datesms_tt' : datetime.datetime.now()})
        sendSMS(mobile, sysm['body'])
       
        
        

#_____