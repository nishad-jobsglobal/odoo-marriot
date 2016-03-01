
thelink = "http://api.clickatell.com/http/sendmsg?password=YNZYHCMDTHaCDO&user=gagamba1&api_id=3502830&"
#object.write({'stage_id':'done'})


prefix = ""

if object.hasoffersigned:
    themessage = 'asdfadsfadsfad'
    smob = object.mobile
    smobile = smob.strip()
    if smobile:
        totext = "to=" + smobile + "&"
        ames={}
        ames['msg'] = prefix + themessage
        ames['gateway_id'] = 1
        ames['mobile'] = smobile
        urlenccc =  'text=' + themessage
        ames['name'] = thelink + totext + urlenccc
        #env['sms.smsclient.queue'].sudo().create(ames)
    
    sysm = {}
    sysm['model'] = 'tapplicant'
    sysm['type'] = 'notification'
    sysm['subject'] = 'System SMS: Signed Offer'
    sysm['record_name'] = object.name or u''
    sysm['body'] = ("Congrat " + object.name + ", u r selected as " + object.trjob_id.name + " by " + object.partner_id.name + " in " + object.trip_id.job_country_id.name + ", contact our local branch. Keep offer details confidential.  Contact - Jobsglobal.com 2 sign now b4 deadlines, Auto Msg. Dont Reply") or u''

    sysm['res_id'] = object.id
    sysm['author_id'] =  user.id

    env['mail.message'].create(sysm)
     
    
    #object.write({'smslog' : ames['msg']})









#_____