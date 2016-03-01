trip_date = object.trip_id.trip_start or False
rs = True


def invalid(emailaddress):
    if len(emailaddress) < 7:
        return True # Address too short.

    try:
        localpart, domainname = emailaddress.rsplit('@', 1)
        host, toplevel = domainname.rsplit('.', 1)
    except ValueError:
        return True # Address does not have enough parts.
        
    for i in '-_.%+.':
        localpart = localpart.replace(i, "")
    for i in '-_.':
        host = host.replace(i, "")

    if localpart.isalnum() and host.isalnum():
        return False # Email address is fine.
    else:
        return True # Email address has funny characters.


def sendEmail(email, msg, subject):
    ames={}
    ames['body_html'] = msg
    ames['subject'] = subject
    ames['state'] = 'outgoing'
    ames['email_to'] = email
    ames['email_from'] = 'JobsGlobal <no-reply@jobsglobal.com>'
    
    env['mail.mail'].sudo().create(ames)
    

if trip_date:
    date_format = '%Y-%m-%d'
    t_date = (trip_date.split(' '))[0]
    e1 = datetime.datetime.strptime(t_date, date_format).date()
    if (e1.year < 2015 and e1.year > 2000):
        rs = False

#start Process
email = (object.user_email).strip() if object.user_email else ''

if rs and email != '' and not invalid(email) and not object.hastravelled and object.stage_id != 5 and not object.unfit:    
    #offer received
    if not object.datemal_ro and not object.hastravelled:
        sysm = {}
        sysm['model'] = 'tapplicant'
        sysm['type'] = 'notification'
        sysm['subject'] = 'Email Sent to ' + email + ' : Offer Received'
        sysm['res_id'] = object.id
        if object.company_id == 15:
            sysm['body'] = 'Hi ' + object.name + ', You are selected as ' + (object.trjob_id.name or 'employee') + ' by ' + (object.partner_id.name or 'YoYour Employer') + ' to ' + (object.trip_id.job_country_id.name or 'their job location') + ', contact us at ' + (object.company_id.phone or 'our local branch') + '. Keep offer details confidential. Contact ' + (object.company_id.company_registry or 'JobsGlobal.com') + ' to Sign contract ASAP. Auto MSG. do not reply'
        else:
            sysm['body'] = 'Hi ' + object.name + ', you are selected as ' + (object.trjob_id.name or 'employee') + ' by ' + (object.partner_id.name or 'YoYour Employer') + ' to ' + (object.trip_id.job_country_id.name or 'their job location') + ', contact us at ' + (object.company_id.phone or 'our local branch') + '. Keep offer details confidential. Contact ' + (object.company_id.company_registry or 'JobsGlobal.com') + ' to Sign contract ASAP. Auto MSG. do not reply'
        env['mail.message'].create(sysm)
        object.write({'datemal_ro' : datetime.datetime.now()})
        sendEmail(email, sysm['body'], 'Offer Received')

    #to sign offer
    date_format = '%Y-%m-%d'
    joining_date = (object.create_date.split(' '))[0]
    current_date = (datetime.datetime.today()).strftime(date_format)
    d1 = datetime.datetime.strptime(joining_date, date_format).date()
    d2 = datetime.datetime.strptime(current_date, date_format).date()
    r = d2 - d1
    if email and not object.hasoffersigned and not object.datemal_os and r.days > 7 and not object.hastravelled:
        sysm = {}
        sysm['model'] = 'tapplicant'
        sysm['type'] = 'notification'
        sysm['subject'] = 'Email Sent to ' + email + ' : Sign Offer'
        sysm['res_id'] = object.id
        if object.company_id == 15:
            sysm['body'] = 'Hi ' + object.name + ', Reminder your job offer signing deadline ending, please visit us now to sign, offers not signed for over a week may get invalid. Contact ' + (object.company_id.company_registry or 'JobsGlobal.com') + ', Auto MSG. do not reply'
        else:
            sysm['body'] = 'Hi ' + object.name + ', Reminder your job offer signing deadline ending, please visit us now to sign, offers not signed for over a week may get invalid. Auto MSG. do not reply. ' + (object.company_id.company_registry or 'JobsGlobal.com')
        env['mail.message'].create(sysm)
        object.write({'datemal_os' : datetime.datetime.now()})
        sendEmail(email, sysm['body'], 'Sign Offer')

    #medical exam
    if email and not object.datemal_am and object.clinic_id and not object.hastravelled:
        sysm = {}
        sysm['model'] = 'tapplicant'
        sysm['type'] = 'notification'
        sysm['subject'] = 'Email Sent to ' + email + ' : Medical Exam'
        sysm['res_id'] = object.id
        if object.company_id == 15:
            sysm['body'] = 'Hi ' + object.name + ', Reminder to do ur job abroad medical exam before deadlines, if done already please submit to us. Contact ' + (object.company_id.company_registry or 'JobsGlobal.com') + '. Auto MSG. do not reply'
        else:
            sysm['body'] = 'Hi ' + object.name + ', Reminder to do ur job abroad medical exam before deadlines, if done already please submit to us. Auto MSG. do not reply. ' + (object.company_id.company_registry or 'JobsGlobal.com')
        env['mail.message'].create(sysm)
        object.write({'datemal_am' : datetime.datetime.now()})
        sendEmail(email, sysm['body'], 'Medical Exam')

    #endorsed for visa
    if email and not object.datemal_ev and object.dateendorsedvisa and not object.hastravelled:
        sysm = {}
        sysm['model'] = 'tapplicant'
        sysm['type'] = 'notification'
        sysm['subject'] = 'Email Sent to ' + email + ' : Endorsed for Visa'
        sysm['res_id'] = object.id
        if object.company_id == 15:
            sysm['body'] = 'Hi ' + object.name + ', Your visa to ' + (object.partner_id.name or 'Your Employer') + ' sent for processing. Dont resign till visa issued, Never respond to any MONEY REQUEST by staff, deposit only to JobsGlobal official BDO account. Contact ' + (object.company_id.company_registry or 'JobsGlobal.com') + ', Auto MSG. do not reply'
        else:
            sysm['body'] = 'Hi ' + object.name + ', Your visa to ' + (object.partner_id.name or 'Your Employer') + ' sent for processing. Dont resign till visa issued. Auto MSG. do not reply. ' + (object.company_id.company_registry or 'JobsGlobal.com')
        env['mail.message'].create(sysm)
        object.write({'datemal_ev' : datetime.datetime.now()})
        sendEmail(email, sysm['body'], 'Endorsed for Visa')

    #endorsed for visa and 2 weeks passed
    date_format = '%Y-%m-%d'
    joining_date = ((object.datemal_ev or current_date).split(' '))[0]
    d1 = datetime.datetime.strptime(joining_date, date_format).date()
    r = d2 - d1
    if email and not object.datemal_ef and object.dateendorsedvisa and not object.datevisareceived and r.days > 14 and not object.hastravelled:
        sysm = {}
        sysm['model'] = 'tapplicant'
        sysm['type'] = 'notification'
        sysm['subject'] = 'Email Sent to ' + email + ' : Waiting for Visa'
        sysm['res_id'] = object.id
        if object.company_id == 15:
            sysm['body'] = 'Hi ' + object.name + ', Your visa still in process. May take a while, will update You if ready, dont resign till visa approved, Contact ' + (object.company_id.company_registry or 'JobsGlobal.com') + ', Auto MSG. do not reply'
        else:
            sysm['body'] = 'Hi ' + object.name + ', Your visa still in process. May take a while, will update You if ready, dont resign till visa approved, Auto MSG. do not reply. ' + (object.company_id.company_registry or 'JobsGlobal.com')
        env['mail.message'].create(sysm)
        object.write({'datemal_ef' : datetime.datetime.now()})
        sendEmail(email, sysm['body'], 'Waiting for Visa')

    #Visa Received
    if email and not object.datemal_vr and object.datevisareceived and not object.hastravelled:
        sysm = {}
        sysm['model'] = 'tapplicant'
        sysm['type'] = 'notification'
        sysm['subject'] = 'Email Sent to ' + email + ' : VISA Received'
        sysm['res_id'] = object.id
        if object.company_id == 15:
            sysm['body'] = 'Congrats ' + object.name + ', Visa for ' + (object.partner_id.name or 'Your Employer') + ' to ' + (object.trip_id.job_country_id.name or 'their job location') + ' is ready. Please contact ' + (object.company_id.phone or 'our local branch') + ' now. Remember, never respond to any money request except to official JobsGlobal BDO account. Auto MSG. do not reply'
        else:
            sysm['body'] = 'Congrats ' + object.name + ', Visa for ' + (object.partner_id.name or 'Your Employer') + ' to ' + (object.trip_id.job_country_id.name or 'their job location') + ' is ready. Please contact ' + (object.company_id.phone or 'our local branch') + ' now. Auto MSG. do not reply. ' + (object.company_id.company_registry or 'JobsGlobal.com')
        env['mail.message'].create(sysm)
        object.write({'datemal_vr' : datetime.datetime.now()})
        sendEmail(email, sysm['body'], 'Visa Received')

    #Gamca
    if email and not object.datemal_gn and not object.gamcanotneeded and object.gamcaclinic and not object.hastravelled:
        sysm = {}
        sysm['model'] = 'tapplicant'
        sysm['type'] = 'notification'
        sysm['subject'] = 'Email Sent to ' + email + ' : For Gamca'
        sysm['res_id'] = object.id
        sysm['body'] = 'Hi ' + object.name + ', please do GAMCA medical exam b4 deadlines for ' + (object.partner_id.name or 'Your Employer') + ' visa, if done pls contact ' + (object.company_id.company_registry or 'JobsGlobal.com') + ' at ' + (object.company_id.phone or 'our local branch') + '. Auto MSG. do not reply'
        env['mail.message'].create(sysm)
        object.write({'datemal_gn' : datetime.datetime.now()})
        sendEmail(email, sysm['body'], 'For Gamca')

        
    #Ticket Cleared
    if email and not object.datemal_ct and object.dateticketissueclear and not object.flightdetails and not object.hastravelled:
        sysm = {}
        sysm['model'] = 'tapplicant'
        sysm['type'] = 'notification'
        sysm['subject'] = 'Email Sent to ' + email + ' : Cleared for Ticket'
        sysm['res_id'] = object.id
        sysm['body'] = 'Hi ' + object.name + ', Your ticket to ' + (object.trip_id.job_country_id.name or 'Client job location') + ' was requested, be prepared for travelling soon once issued. Auto MSG. do not reply. ' + (object.company_id.company_registry or 'JobsGlobal.com')
        env['mail.message'].create(sysm)
        object.write({'datemal_ct' : datetime.datetime.now()})
        sendEmail(email, sysm['body'], 'Cleared for Ticket')

        
    date_format = '%Y-%m-%d'
    joining_date = ((object.datetravel or current_date).split(' '))[0]
    d1 = datetime.datetime.strptime(joining_date, date_format).date()
    r = d2 - d1
         
    #Ticket Issued
    if email and not object.datemal_ti and object.flightdetails and r.days > 1 and r.days < 180 and not object.hastravelled:
        sysm = {}
        sysm['model'] = 'tapplicant'
        sysm['type'] = 'notification'
        sysm['subject'] = 'Email Sent to ' + email + ' : Ticket Issued'
        sysm['res_id'] = object.id
        sysm['body'] = 'Hi ' + object.name + ', ticket for ' + (object.partner_id.name or 'Your Employer') + ' to '  + (object.trip_id.job_country_id.name or 'their job location') + ' On ' + (object.datetravel or '[ask travel date]') + ', contact us at ' + (object.company_id.phone or 'our local branch') + ' for details. Auto MSG. do not reply. ' + (object.company_id.company_registry or 'JobsGlobal.com') 
        env['mail.message'].create(sysm)
        object.write({'datemal_ti' : datetime.datetime.now()})
        sendEmail(email, sysm['body'], 'Ticket Issued')


    #Travel
    if email and not object.datemal_tt and object.datetravel and r.days < 3 and not object.hastravelled and r.days != 0 and r.days > 0 and not object.hastravelled:
        sysm = {}
        sysm['model'] = 'tapplicant'
        sysm['type'] = 'notification'
        sysm['subject'] = 'Email Sent to ' + email + ' : Travelling Last Reminder'
        sysm['res_id'] = object.id
        sysm['body'] = 'Hi ' + object.name + ', Reminder of Ur travel on ' + (object.datetravel or '[ask travel date]') + ', be in the airport 3 hours before flight to have time for travel processing. Have a safe trip and wish you all the best. ' + (object.company_id.company_registry or 'JobsGlobal.com')
        env['mail.message'].create(sysm)
        object.write({'datemal_tt' : datetime.datetime.now()})
        sendEmail(email, sysm['body'], 'Travelling Last Reminder')
       
        
        

#_____