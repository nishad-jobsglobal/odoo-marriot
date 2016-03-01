SmsTrip = 16274,14708
trip_date = object.trip_id.trip_start or False
rs = True


prefix = {
    1:'971',
    17:'975',
    6:'86',
    4:'20',
    7:'91',
    8:'91',
    16:'254',
    11:'996',
    5:'373',
    13:'212',
    9:'95',
    14:'977',
    15:'63',
    12:'40',
    3:'94',
    10:'216'
}


def checkMobile(mobile, company_id):
    finalmob = ''
    if len(mobile) >= 11 and len(mobile) <= 16:
        finalmob = mobile
    elif company_id != 99 and prefix[company_id] and len(mobile) <= 9 and len(mobile) >= 8:
        finalmob = prefix[company_id] + mobile
    
    if finalmob != '' and finalmob[:1] != '1':
        return finalmob
    
    return ''

    
def sendSMS(mobile, msg):
    #thelink = "http://api.clickatell.com/http/sendmsg?password=YNZYHCMDTHaCDO&user=gagamba1&api_id=3502830&"
    thelink = "http://209.95.52.78/goip/en/dosend.php?USERNAME=root&PASSWORD=root&smsprovider=1&method=2&"
    ames={}
    ames['msg'] = msg
    ames['gateway_id'] = 2
    ames['mobile'] = mobile
    #ames['name'] = thelink + "to=" + mobile + "&" + 'text=' + msg
    ames['name'] = thelink + "smsnum=" + mobile + "&" + 'Memo=' + msg
    env['sms.smsclient.queue'].sudo().create(ames)
    

if trip_date:
    date_format = '%Y-%m-%d'
    t_date = (trip_date.split(' '))[0]
    e1 = datetime.datetime.strptime(t_date, date_format).date()
    if (e1.year < 2015 and e1.year > 2000):
        rs = False

    
#start Process
#if ((object.trip_id or False) and object.trip_id.id in SmsTrip) and rs:
chars_to_remove = [' ', '+', '(',')']
mobile = (object.mobile).strip() if object.mobile else ''
mobile = mobile.lstrip('0')
mobile = mobile.strip('+')
mobile = mobile.strip('-')
#mobile = mobile.translate(None, ''.join(chars_to_remove))
mobile = mobile.strip() if object.mobile else ''
mobile = checkMobile(mobile, (object.company_id.id or 99))
    
if rs and mobile != '':    
    #offer received
    if mobile and not object.datesms_ro and not object.datetravel:
        sysm = {}
        sysm['model'] = 'tapplicant'
        sysm['type'] = 'notification'
        sysm['subject'] = 'System SMS Sent to +' + mobile + ' : Offer Received'
        sysm['res_id'] = object.id
        if object.company_id == 15:
            sysm['body'] = 'Hi ' + object.name + ', u r selected as ' + (object.trjob_id.name or 'employee') + ' by ' + (object.partner_id.name or 'Ur Employer') + ' to ' + (object.trip_id.job_country_id.name or 'their job location') + ', contact us at ' + (object.company_id.phone or 'our local branch') + '. Keep offer details confidential. Contact ' + (object.company_id.company_registry or 'JobsGlobal.com') + ' to Sign contract ASAP. Auto MSG. do not reply'
        else:
            sysm['body'] = 'Hi ' + object.name + ', u r selected as ' + (object.trjob_id.name or 'employee') + ' by ' + (object.partner_id.name or 'Ur Employer') + ' to ' + (object.trip_id.job_country_id.name or 'their job location') + ', contact us at ' + (object.company_id.phone or 'our local branch') + '. Keep offer details confidential. Contact ' + (object.company_id.company_registry or 'JobsGlobal.com') + ' to Sign contract ASAP. Auto MSG. do not reply'
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
        sysm['subject'] = 'System SMS Sent to +' + mobile + ' : Sign Offer'
        sysm['res_id'] = object.id        
        if object.company_id == 15:
            sysm['body'] = 'Hi ' + object.name + ', Reminder yr job offer signing deadline ending, please visit us now to sign, offers not signed for over a week may get invalid. Contact ' + (object.company_id.company_registry or 'JobsGlobal.com') + ', Auto MSG. do not reply'
        else:
            sysm['body'] = 'Hi ' + object.name + ', Reminder yr job offer signing deadline ending, please visit us now to sign, offers not signed for over a week may get invalid. Auto MSG. do not reply. ' + (object.company_id.company_registry or 'JobsGlobal.com')
        env['mail.message'].create(sysm)
        object.write({'datesms_os' : datetime.datetime.now()})
        sendSMS(mobile, sysm['body'])

    #medical exam
    if mobile and not object.datesms_am and object.clinic_id and not object.datetravel:
        sysm = {}
        sysm['model'] = 'tapplicant'
        sysm['type'] = 'notification'
        sysm['subject'] = 'System SMS Sent to +' + mobile + ' : Medical Exam'
        sysm['res_id'] = object.id
        if object.company_id == 15:
            sysm['body'] = 'Hi ' + object.name + ', Reminder to do ur job abroad medical exam b4 deadlines, if done already pls submit to us. Contact ' + (object.company_id.company_registry or 'JobsGlobal.com') + '. Auto MSG. do not reply'
        else:
            sysm['body'] = 'Hi ' + object.name + ', Reminder to do ur job abroad medical exam b4 deadlines, if done already pls submit to us. Auto MSG. do not reply. ' + (object.company_id.company_registry or 'JobsGlobal.com')
        env['mail.message'].create(sysm)
        object.write({'datesms_am' : datetime.datetime.now()})
        sendSMS(mobile, sysm['body'])

    #endorsed for visa
    if mobile and not object.datesms_ev and object.dateendorsedvisa and not object.datetravel:
        sysm = {}
        sysm['model'] = 'tapplicant'
        sysm['type'] = 'notification'
        sysm['subject'] = 'System SMS Sent to +' + mobile + ' : Endorsed for Visa'
        sysm['res_id'] = object.id
        if object.company_id == 15:
            sysm['body'] = 'Hi ' + object.name + ', Ur visa to ' + (object.partner_id.name or 'Ur Employer') + ' sent for processing. Dont resign till visa issued, Never respond to any MONEY REQUEST by staff, deposit only to JobsGlobal official BDO account. Contact ' + (object.company_id.company_registry or 'JobsGlobal.com') + ', Auto MSG. do not reply'
        else:
            sysm['body'] = 'Hi ' + object.name + ', Ur visa to ' + (object.partner_id.name or 'Ur Employer') + ' sent for processing. Dont resign till visa issued. Auto MSG. do not reply. ' + (object.company_id.company_registry or 'JobsGlobal.com')
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
        sysm['subject'] = 'System SMS Sent to +' + mobile + ' : Waiting for Visa'
        sysm['res_id'] = object.id
        if object.company_id == 15:
            sysm['body'] = 'Hi ' + object.name + ', Ur visa still in process. May take a while, will update U if ready, dont resign till visa approved, Contact ' + (object.company_id.company_registry or 'JobsGlobal.com') + ', Auto MSG. do not reply'
        else:
            sysm['body'] = 'Hi ' + object.name + ', Ur visa still in process. May take a while, will update U if ready, dont resign till visa approved, Auto MSG. do not reply. ' + (object.company_id.company_registry or 'JobsGlobal.com')
        env['mail.message'].create(sysm)
        object.write({'datesms_ef' : datetime.datetime.now()})
        sendSMS(mobile, sysm['body'])

    #Visa Received
    if mobile and not object.datesms_vr and object.datevisareceived and not object.datetravel:
        sysm = {}
        sysm['model'] = 'tapplicant'
        sysm['type'] = 'notification'
        sysm['subject'] = 'System SMS Sent to +' + mobile + ' : VISA Received'
        sysm['res_id'] = object.id
        if object.company_id == 15:
            sysm['body'] = 'Congrats ' + object.name + ', Visa for ' + (object.partner_id.name or 'Ur Employer') + ' to ' + (object.trip_id.job_country_id.name or 'their job location') + ' is ready. Please contact ' + (object.company_id.phone or 'our local branch') + ' now. Remember, never respond to any money request except to official JobsGlobal BDO account. Auto MSG. do not reply'
        else:
            sysm['body'] = 'Congrats ' + object.name + ', Visa for ' + (object.partner_id.name or 'Ur Employer') + ' to ' + (object.trip_id.job_country_id.name or 'their job location') + ' is ready. Please contact ' + (object.company_id.phone or 'our local branch') + ' now. Auto MSG. do not reply. ' + (object.company_id.company_registry or 'JobsGlobal.com')
        env['mail.message'].create(sysm)
        object.write({'datesms_vr' : datetime.datetime.now()})
        sendSMS(mobile, sysm['body'])

    #Gamca
    if mobile and not object.datesms_gn and not object.gamcanotneeded and object.gamcaclinic and not object.datetravel:
        sysm = {}
        sysm['model'] = 'tapplicant'
        sysm['type'] = 'notification'
        sysm['subject'] = 'System SMS Sent to +' + mobile + ' : For Gamca'
        sysm['res_id'] = object.id
        sysm['body'] = 'Hi ' + object.name + ', pls do GAMCA medical exam b4 deadlines for ' + (object.partner_id.name or 'Ur Employer') + ' visa, if done pls contact ' + (object.company_id.company_registry or 'JobsGlobal.com') + ' at ' + (object.company_id.phone or 'our local branch') + '. Auto MSG. do not reply'
        env['mail.message'].create(sysm)
        object.write({'datesms_gn' : datetime.datetime.now()})
        sendSMS(mobile, sysm['body'])

        
    #Ticket Cleared
    if mobile and not object.datesms_ct and object.dateticketissueclear and not object.flightdetails:
        sysm = {}
        sysm['model'] = 'tapplicant'
        sysm['type'] = 'notification'
        sysm['subject'] = 'System SMS Sent to +' + mobile + ' : Cleared for Ticket'
        sysm['res_id'] = object.id
        sysm['body'] = 'Hi ' + object.name + ', Ur ticket to ' + (object.trip_id.job_country_id.name or 'Client job location') + ' was requested, be prepared for travelling soon once issued. Auto MSG. do not reply. ' + (object.company_id.company_registry or 'JobsGlobal.com')
        env['mail.message'].create(sysm)
        object.write({'datesms_ct' : datetime.datetime.now()})
        sendSMS(mobile, sysm['body'])

        
    date_format = '%Y-%m-%d'
    joining_date = ((object.datetravel or current_date).split(' '))[0]
    d1 = datetime.datetime.strptime(joining_date, date_format).date()
    r = d2 - d1
         
    #Ticket Issued
    if mobile and not object.datesms_ti and object.flightdetails and r.days > 1 and r.days < 180 and not object.hastravelled:
        sysm = {}
        sysm['model'] = 'tapplicant'
        sysm['type'] = 'notification'
        sysm['subject'] = 'System SMS Sent to +' + mobile + ' : Ticket Issued'
        sysm['res_id'] = object.id
        sysm['body'] = 'Hi ' + object.name + ', ticket for ' + (object.partner_id.name or 'Ur Employer') + ' to '  + (object.trip_id.job_country_id.name or 'their job location') + ' On ' + (object.datetravel or '[ask travel date]') + ', contact us at ' + (object.company_id.phone or 'our local branch') + ' 4 details. Auto MSG. do not reply. ' + (object.company_id.company_registry or 'JobsGlobal.com') 
        env['mail.message'].create(sysm)
        object.write({'datesms_ti' : datetime.datetime.now()})
        sendSMS(mobile, sysm['body'])


    #Travel
    if mobile and not object.datesms_tt and object.datetravel and r.days < 3 and not object.hastravelled and r.days != 0 and r.days > 0:
        sysm = {}
        sysm['model'] = 'tapplicant'
        sysm['type'] = 'notification'
        sysm['subject'] = 'System SMS Sent to +' + mobile + ' : Travelling Last Reminder'
        sysm['res_id'] = object.id
        sysm['body'] = 'Hi ' + object.name + ', Reminder of Ur travel on ' + (object.datetravel or '[ask travel date]') + ', be in the airport 3 hours before flight to have time for travel processing. Have a safe trip and wish you all the best. ' + (object.company_id.company_registry or 'JobsGlobal.com')
        env['mail.message'].create(sysm)
        object.write({'datesms_tt' : datetime.datetime.now()})
        sendSMS(mobile, sysm['body'])
       
        
        

#_____