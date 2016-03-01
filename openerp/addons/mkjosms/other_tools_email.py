EmailTrip = 16274,14708

def sendEmail(email, msg, id):
    ames={}
    ames['body_html'] = msg
    ames['mail_message_id'] = id
    ames['state'] = 'outgoing'
    ames['email_to'] = email
    env['mail.mail'].sudo().create(ames)
    

#start Process
if (object.trip_id or False) and object.trip_id.id in EmailTrip:
    user_email = object.user_email or ''

    #offer received
    if user_email and not object.datemal_ro and not object.datetravel:
        sysm = {}
        sysm['model'] = 'tapplicant'
        sysm['type'] = 'notification'
        sysm['subject'] = 'System EMAIL Sent: Offer Received'
        sysm['res_id'] = object.id
        sysm['body'] = 'Hi ' + object.name + ', you are selected as ' + (object.trjob_id.name or 'employee') + ' by ' + (object.partner_id.name or 'Your  Employer') + ' to ' + (object.trip_id.job_country_id.name or 'their job location') + ', contact us at ' + (object.company_id.phone or 'our local branch') + '. Keep offer details confidential. Contact us to Sign contract ASAP. Auto MSG. do not reply'
        id = env['mail.message'].create(sysm)
        object.write({'datemal_ro' : datetime.datetime.now()})
        sendEmail(user_email, sysm['body'], id)

    #to sign offer
    date_format = '%Y-%m-%d'
    joining_date = (object.create_date.split(' '))[0]
    current_date = (datetime.datetime.today()).strftime(date_format)
    d1 = datetime.datetime.strptime(joining_date, date_format).date()
    d2 = datetime.datetime.strptime(current_date, date_format).date()
    r = d2 - d1
    if user_email and not object.hasoffersigned and not object.datemal_os and r.days > 7 and not object.datetravel:
        sysm = {}
        sysm['model'] = 'tapplicant'
        sysm['type'] = 'notification'
        sysm['subject'] = 'System EMAIL Sent: Sign Offer'
        sysm['res_id'] = object.id
        sysm['body'] = 'Hi ' + object.name + ', Reminder your job offer signing deadline ending, please visit us now to sign, offers not signed for over a week may get invalid. Contact JobsGlobal.com, Auto MSG. do not reply'
        id = env['mail.message'].create(sysm)
        object.write({'datemal_os' : datetime.datetime.now()})
        sendEmail(user_email, sysm['body'], id)

    #medical exam
    if user_email and not object.datemal_am and object.clinic_id and not object.datetravel:
        sysm = {}
        sysm['model'] = 'tapplicant'
        sysm['type'] = 'notification'
        sysm['subject'] = 'System EMAIL Sent: Medical Exam'
        sysm['res_id'] = object.id
        sysm['body'] = 'Hi ' + object.name + ', Reminder to do your job abroad medical exam before deadlines, if done already please submit to us. Contact JobsGlobal.com. Auto MSG. do not reply'
        id = env['mail.message'].create(sysm)
        object.write({'datemal_am' : datetime.datetime.now()})
        sendEmail(user_email, sysm['body'], id)

    #endorsed for visa
    if user_email and not object.datemal_ev and object.dateendorsedvisa and not object.datetravel:
        sysm = {}
        sysm['model'] = 'tapplicant'
        sysm['type'] = 'notification'
        sysm['subject'] = 'System EMAIL Sent: Endorsed for Visa'
        sysm['res_id'] = object.id
        sysm['body'] = 'Hi ' + object.name + ', your visa to ' + (object.partner_id.name or  'Your Employer') + ' sent for processing. Dont resign till visa issued, Never respond to any MONEY REQUEST by staff, deposit only to JobsGlobal official BDO account. Contact JobsGlobal.com, Auto MSG. do not reply'
        id = env['mail.message'].create(sysm)
        object.write({'datemal_ev' : datetime.datetime.now()})
        sendEmail(user_email, sysm['body'], id)

    #endorsed for visa and 2 weeks passed
    date_format = '%Y-%m-%d'
    joining_date = ((object.datemal_ev or current_date).split(' '))[0]
    d1 = datetime.datetime.strptime(joining_date, date_format).date()
    r = d2 - d1
    if user_email and not object.datemal_ef and object.dateendorsedvisa and not object.datevisareceived and r.days > 14 and not object.datetravel:
        sysm = {}
        sysm['model'] = 'tapplicant'
        sysm['type'] = 'notification'
        sysm['subject'] = 'System EMAIL Sent: Waiting for Visa'
        sysm['res_id'] = object.id
        sysm['body'] = 'Hi ' + object.name + ', your visa still in process. May take a while, will update You if ready, dont resign till visa approved, Contact JobsGlobal.com, Auto MSG. do not reply'
        id = env['mail.message'].create(sysm)
        object.write({'datemal_ef' : datetime.datetime.now()})
        sendEmail(user_email, sysm['body'], id)

    #Visa Received
    if user_email and not object.datemal_vr and object.datevisareceived and not object.datetravel:
        sysm = {}
        sysm['model'] = 'tapplicant'
        sysm['type'] = 'notification'
        sysm['subject'] = 'System EMAIL Sent: VISA Received'
        sysm['res_id'] = object.id
        sysm['body'] = 'Congrats ' + object.name + ', Visa for ' + (object.partner_id.name or  'Your Employer') + ' to ' + (object.trip_id.job_country_id.name or 'their job location') + ' is ready. Please contact ' + (object.company_id.phone or 'our local branch') + ' now. Remember, never respond to any money request except to official JobsGlobal BDO account. Auto MSG. do not reply'
        id = env['mail.message'].create(sysm)
        object.write({'datemal_vr' : datetime.datetime.now()})
        sendEmail(user_email, sysm['body'], id)

    #Gamca
    if user_email and not object.datemal_gn and not object.gamcanotneeded and object.gamcaclinic and not object.datetravel:
        sysm = {}
        sysm['model'] = 'tapplicant'
        sysm['type'] = 'notification'
        sysm['subject'] = 'System EMAIL Sent: For Gamca'
        sysm['res_id'] = object.id
        sysm['body'] = 'Hi ' + object.name + ', please do GAMCA medical exam before deadlines for ' + (object.partner_id.name or  'Your Employer') + ' visa, if done please contact us at ' + (object.company_id.phone or 'our local branch') + '. Auto MSG. do not reply'
        id = env['mail.message'].create(sysm)
        object.write({'datemal_gn' : datetime.datetime.now()})
        sendEmail(user_email, sysm['body'], id)

        
    #Ticket Cleared
    if user_email and not object.datemal_ct and object.dateticketissueclear and not object.flightdetails:
        sysm = {}
        sysm['model'] = 'tapplicant'
        sysm['type'] = 'notification'
        sysm['subject'] = 'System EMAIL Sent: Cleared for Ticket'
        sysm['res_id'] = object.id
        sysm['body'] = 'Hi ' + object.name + ', your ticket to ' + (object.trip_id.job_country_id.name or 'Client job location') + ' was requested, be prepared for travelling soon once issued. Auto MSG. do not reply'
        id = env['mail.message'].create(sysm)
        object.write({'datemal_ct' : datetime.datetime.now()})
        sendEmail(user_email, sysm['body'], id)

        
    #Ticket Issued
    if user_email and not object.datemal_ti and object.flightdetails:
        sysm = {}
        sysm['model'] = 'tapplicant'
        sysm['type'] = 'notification'
        sysm['subject'] = 'System EMAIL Sent: Ticket Issued'
        sysm['res_id'] = object.id
        sysm['body'] = 'Hi ' + object.name + ', ticket for ' + (object.partner_id.name or  'Your Employer') + ' to '  + (object.trip_id.job_country_id.name or 'their job location') + ' On ' + (object.datetravel or '[ask travel date]') + ' to ' + (object.trip_id.job_country_id.name or 'their job location') + ', contact us at ' + (object.company_id.phone or 'our local branch') + ' 4 details. Auto MSG. do not reply'
        id = env['mail.message'].create(sysm)
        object.write({'datemal_ti' : datetime.datetime.now()})
        sendEmail(user_email, sysm['body'], id)


    #Travel
    date_format = '%Y-%m-%d'
    joining_date = ((object.datetravel or current_date).split(' '))[0]
    d1 = datetime.datetime.strptime(joining_date, date_format).date()
    r = d2 - d1
    if user_email and not object.datemal_tt and object.datetravel and r.days == 2:
        sysm = {}
        sysm['model'] = 'tapplicant'
        sysm['type'] = 'notification'
        sysm['subject'] = 'System EMAIL Sent: Travelling within 24 HOURS'
        sysm['res_id'] = object.id
        sysm['body'] = 'Hi ' + object.name + ', Reminder of your travel on ' + (object.datetravel or '[ask travel date]') + ', be in the airport 3 hours before flight to have time for travel processing. Have a safe trip and wish you all the best.'
        id = env['mail.message'].create(sysm)
        object.write({'datemal_tt' : datetime.datetime.now()})
        sendEmail(user_email, sysm['body'], id)
       
        
        

#_____