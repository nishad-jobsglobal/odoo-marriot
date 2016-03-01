# Available locals:
#  - time, datetime, dateutil: Python libraries
#  - env: Odoo Environement
#  - model: Model of the record on which the action is triggered
#  - object: Record on which the action is triggered if there is one, otherwise None
#  - workflow: Workflow engine
#  - Warning: Warning Exception to use with raise
# To return an action, assign: action = {...}


st = {}

###########   PROFILING  ###############
if object.user_email and object.gender and object.date_birth and object.homeaddress and (object.salary_basic  or object.salary_gross):
	st['frprflng'] = 0
else:
	if object.frprflng == 0:
		st['frprflng'] = 1

###########  DOCUMENT COLLECTION  ###############
if object.hascv and object.hasinterviewsheet and object.haspassport and object.hasoffersigned and object.hasphoto and object.dateformscompleted and object.nationality and object.passportnumber and object.passportexpiry and object.medicalclinic:
	st['frdcmntcllctn'] = 0
else:
	if object.frdcmntcllctn== 0:
		st['frdcmntcllctn'] = 1

###########  FOR MEDICAL   ###############
if object.medicalclinic == False:
	st['frmdcltst'] = 0
else:
	if object.frmdcltst == 0 :
		st['frmdcltst'] = 1

if object.datemedicalstart :
	if object.mdclnprcss == 0:
		st['mdclnprcss'] = 1
		st['frmdcltst'] = 0
else:
	st['mdclnprcss'] = 0

if object.datemedicalfit:
	if object.fttwrk == 0:
		st['fttwrk'] = 1
		st['mdclnprcss'] = 0
else:
	st['fttwrk'] = 0

if object.datemedicalexpire:
	if object.frmdclpld == 0:
		st['frmdclpld'] = 1
		st['fttwrk'] = 0
else:
	st['frmdclpld'] = 0

if object.datemedicaluploaded:
	st['frmdcltst'] = 0
	st['mdclnprcss '] = 0
	st['fttwrk '] = 0
	st['frmdclpld'] = 0



###########  FOR GAMCA  ###############
if object.gamcaclinic == False:
	st['frgmctst'] = 0
else:
	if object.frgmctst== 0 :
		st['frgmctst'] = 1

if object.dategamcastart :
	if object.gmcnprcss== 0:
		st['gmcnprcss'] = 1
		st['frgmctst'] = 0
else:
	st['gmcnprcss'] = 0

if object.dategamcafit:
	if object.gmcfttwrk == 0:
		st['gmcfttwrk'] = 1
		st['gmcnprcss'] = 0
else:
	st['gmcfttwrk'] = 0

if object.dategamcaexpire:
	if object.frgmcpld== 0:
		st['frgmcpld'] = 1
		st['gmcfttwrk'] = 0
else:
	st['frgmcpld'] = 0

if object.dategamcauploaded:
	st['frgmctst'] = 0
	st['gmcnprcss'] = 0
	st['gmcfttwrk'] = 0
	st['frgmcpld'] = 0


#debug
#st['description'] = object.homeaddress + ' ' + str(object.date_birth)
self.write(cr, uid, object.id, st, context=context)


