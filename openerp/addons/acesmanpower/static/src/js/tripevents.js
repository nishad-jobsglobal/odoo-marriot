var visitorsData = {
        /*"EG": 1,
        "PH": 3,
        "IN": 2,
        "NP": 5*/
        }; 

var country_code1 = {
    1:"AD",2:"AE",3:"AF",4:"AG",5:"AI",6:"AL",7:"AM",8:"AN",9:"AO",10:"AQ",11:"AR",12:"AS",13:"AT",14:"AU",15:"AW",16:"AX",17:"AZ",18:"BA",19:"BB",20:"BD",21:"BE",22:"BF",23:"BG",24:"BH",25:"BI",26:"BJ",27:"BL",28:"BM",29:"BN",30:"BO",31:"BQ",32:"BR",33:"BS",34:"BT",35:"BV",36:"BW",37:"BY",38:"BZ",39:"CA",40:"CC",41:"CF",42:"CD",43:"CG",44:"CH",45:"CI",46:"CK",47:"CL",48:"CM",49:"CN",50:"CO",51:"CR",52:"CU",53:"CV",54:"CW",55:"CX",56:"CY",57:"CZ",58:"DE",59:"DJ",60:"DK",61:"DM",62:"DO",63:"DZ",64:"EC",65:"EE",66:"EG",67:"EH",68:"ER",69:"ES",70:"ET",71:"FI",72:"FJ",73:"FK",74:"FM",75:"FO",76:"FR",77:"GA",78:"GD",79:"GE",80:"GF",81:"GH",82:"GI",83:"GG",84:"GL",85:"GM",86:"GN",87:"GP",88:"GQ",89:"GR",90:"GS",91:"GT",92:"GU",93:"GW",94:"GY",95:"HK",96:"HM",97:"HN",98:"HR",99:"HT",100:"HU",101:"ID",102:"IE",103:"IL",104:"IM",105:"IN",106:"IO",107:"IQ",108:"IR",109:"IS",110:"IT",111:"JE",112:"JM",113:"JO",114:"JP",115:"KE",116:"KG",117:"KH",118:"KI",119:"KM",120:"KN",121:"KP",122:"KR",123:"KW",124:"KY",125:"KZ",126:"LA",127:"LB",128:"LC",129:"LI",130:"LK",131:"LR",132:"LS",133:"LT",134:"LU",135:"LV",136:"LY",137:"MA",138:"MC",139:"MD",140:"ME",141:"MF",142:"MG",143:"MH",144:"MK",145:"ML",146:"MM",147:"MN",148:"MO",149:"MP",150:"MQ",151:"MR",152:"MS",153:"MT",154:"MU",155:"MV",156:"MW",157:"MX",158:"MY",159:"MZ",160:"NA",161:"NC",162:"NE",163:"NF",164:"NG",165:"NI",166:"NL",167:"NO",168:"NP",169:"NR",170:"NT",171:"NU",172:"NZ",173:"OM",174:"PA",175:"PE",176:"PF",177:"PG",178:"PH",179:"PK",180:"PL",181:"PM",182:"PN",183:"PR",184:"PS",185:"PT",186:"PW",187:"PY",188:"QA",189:"RE",190:"RO",191:"RS",192:"RU",193:"RW",194:"SA",195:"SB",196:"SC",197:"SD",198:"SE",199:"SG",200:"SH",201:"SI",202:"SJ",203:"SK",204:"SL",205:"SM",206:"SN",207:"SO",208:"SR",209:"SS",210:"ST",211:"SV",212:"SX",213:"SY",214:"SZ",215:"TC",216:"TD",217:"TF",218:"TG",219:"TH",220:"TJ",221:"TK",222:"TM",223:"TN",224:"TO",225:"TP",226:"TR",227:"TT",228:"TV",229:"TW",230:"TZ",231:"UA",232:"UG",233:"GB",234:"UM",235:"US",236:"UY",237:"UZ",238:"VA",239:"VC",240:"VE",241:"VG",242:"VI",243:"VN",244:"VU",245:"WF",246:"WS",247:"YE",248:"YT",249:"YU",250:"ZA",251:"ZM",252:"ZR",253:"ZW"
    }

openerp.acesmanpower = function(instance, local) {
	var _t = instance.web._t,
	    _lt = instance.web._lt;
	var QWeb = instance.web.qweb;
    
    	var manpowerUser;
	
	local.TripeventsPage = instance.Widget.extend({
		template: "DashBoarder",
		init: function(parent) {
			this._super(parent);
		},
		
		start: function() {
			var self = this;
		//self.$('.box').attr('data-id','2771');
            var cgnewmessages = new instance.web.Model("mail.notification");
            
		cgnewmessages.query(['id'])
                .filter([['partner_id', '=', 31],['is_read', '=', false]])
                .all()
                .then(function (results) {
                    $('#cgnewmessages').html( results.length );
            });

            var cUser = this.rpc("/web/session/get_session_info", {}).then(function(result) {
                
                if (!result.uid) return;
                
                var acesmanpoweruser = new instance.web.Model("acesmanpoweruser");
                acesmanpoweruser.query(['id','name','mobile','email'])
                    .filter([['user_id', '=', result.uid]])
                    .first()
                    .then(function (item) {
                        manpowerUser = item
                    });
            }); 
            
	    /* Count shortlisted candidates */
            var acesmanpowershortlist = new instance.web.Model("acesmanpowershortlist");
            acesmanpowershortlist.query(['id'])
                 .all()
                 .then(function (results) {
                    $('#acesmanpowershortlist').html( results.length );
            });
            
	    /* Count applied candidates */
            var acesjobseeker = new instance.web.Model("acesjobseeker");
            acesjobseeker.query(['id'])
		 .filter([['for_marriot', '=', 'True']])
                 .all()
                 .then(function (results) {
                    $('#acesjobseeker').html( results.length );
            });
            
	    /* Count total trips/events */
            var acesmanpowerevent = new instance.web.Model("acesmanpowerevent");
            acesmanpowerevent.query(['id'])
		 .filter([['stage_id', '!=', 'disapproved']])
                 .all()
                 .then(function (results) {
                    $('#acesmanpowerevent').html( results.length );
            });
            
            //Build Trip List
            var cgtrips = new instance.web.Model("acesmanpowerevent");
            var cgtriphtml = "";
            cgtrips.query(['id', 'name', 'can_country_id'])
                 .group_by(['can_country_id'])
                 .then(function (groups) {
                    _(groups).each(function (group) {
                        cgtriphtml += "<tr><td><a href='#' data-cid='" + group.attributes.value[0] + "' >" + group.attributes.value[1] + "</a></td><td class='cgright'>" + group.attributes.length + "</td></tr>";
                        $('table#generalpurpose').append(cgtriphtml);
                        if (group.attributes.value[0] != 'undefined') visitorsData[country_code1[group.attributes.value[0]]] = group.attributes.length
                    });
                    
                    $('table#generalpurpose').html(
                        "<tr><th>Destination</th><th>Trips </th></tr>" + cgtriphtml
                    );
                    
                });
            
            //Build Job List
            var cgtripjobs = new instance.web.Model("acesmanpowerjob");
            var cgtripjobshtml = "";
            cgtripjobs.query(['id', 'name', 'quantity'])
                 .filter([['quantity', '>', 0]])
                 .all()
                 .then(function (items) {
                    $('table#gpjobs').html(
                        "<tr><th>Position</th><th>Required</th></tr>"
                    );
                    
                    _(items).each(function (item) {
                        cgtripjobshtml = "<tr><td><a href='#' data-rid='" + item.id + "' >" + item.name + "</a></td><td class='cgright'>" + item.quantity + "</td></tr>";
                        $('table#gpjobs').append(cgtripjobshtml);
                    });
                });
            
            //Build Property List
            var cgtripprop = new instance.web.Model("acesmanpowerproperty");
            var cgtripprophtml = "";
            var cgmessaging = "";
            var cgmanager = "";
            cgtripprop.query(['id', 'acesmanpoweruser_id', 'name', 'mobile', 'email'])
                 .all()
                 .then(function (items) {
                    _(items).each(function (item) {
                        if (item.acesmanpoweruser_id) {
                            cgmanager = item.acesmanpoweruser_id[1];
                            cgmessaging = "<a href='#' class='fa fa-envelope' data-mobile='" + item.mobile + "' data-module='acesmanpower.wizardsms' title='Message " + item.name + "'></a>";
                        } else {
                            cgmanager = "";
                            cgmessaging = "";
                        }
                        cgtripprophtml = "<tr><td class='cgpropitem'><a href='#' data-pid='" + item.id + "' >" + item.name + "</a></td><td class='cgright'>" + cgmanager + "</td><td class='cgaction'>" + cgmessaging + "</td></tr>";
                        $('table#gprecruitproperties').append(cgtripprophtml);
                    });
                });
		},
        
        events: {
            'click table#generalpurpose a': 'selected_item1', 			/* Upcoming Trips */
            'click table#gpjobs a': 'selected_jobss1',				/* Open Positions */
            'click table#gprecruitproperties td.cgpropitem a': 'selected_prop1',/* Recruiting Properties */
             /* Start Buttons   */
            'click div#generalpurposewrap p a.btn.btn-info': 'showalllist',     /* View All */
            'click div#generalpurposewrap p a.btn.btn-primary': 'createitem',   /* Propose a Trip,Add Position,Add Property */
            /* End Buttons   */
            'click div.small-box.bg-green a.small-box-footer': 'showalllist',   /* View All - Candidates on Process*/
	    'click div.small-box.bg-yellow a.small-box-footer': 'showalllist',  /* View All - Total Applications*/
	    'click div.small-box.bg-red a.small-box-footer': 'showalllist',     /* View All - Recruitment Trips*/
            
            'click td.cgaction a': 'openwizard',				/* Send SMS Wizard */
            'dblclick div.jvectormap-container path': 'mapcountrysel',		/* Upcoming Recruitment Events Locations */
            
        },
        
	/* Upcoming Recruitment Events Locations */
        mapcountrysel: function (event) {
            var cid = 0
            for (var key in country_code1) {
                if (country_code1.hasOwnProperty(key))
                    if ( country_code1[key] == $(event.currentTarget).attr('data-code') ){
                        cid = key;
                        break;
                    }
            }
            if (cid == 0) return;
            var self = this;
            this.rpc('/web/action/run', {
                action_id: 2771,
                context: {'cid':cid}
            }).done(function (action) {
                self.do_action(action, {res_model: 'acesmanpowerevent'});
            });
        },
        
        /* Upcoming Trips  */
        selected_item1: function (event) {
            var $thiselement = $(event.currentTarget);
            var cid = $thiselement.attr('data-cid');
            
            var self = this;
            this.rpc('/web/action/run', {
                action_id: 2771,
                context: {'cid':cid}
            }).done(function (action) {
                self.do_action(action, {res_model: 'acesmanpowerevent'});
            });
        },
        
	/* Open Positions   */
        selected_jobss1: function (event) {
            this.do_action({
                type: 'ir.actions.act_window',
                res_model: 'acesmanpowerjob',
                res_id: $(event.currentTarget).data('rid'),
                views: [[false, 'form']],
                target: 'current',
                view_mode:'form',
                view_type:'form',
            });
        },
         
	/* Recruiting Properties   */
        selected_prop1: function (event) {
            this.do_action({
                type: 'ir.actions.act_window',
                res_model: 'acesmanpowerproperty',
                res_id: $(event.currentTarget).data('pid'),
                views: [[false, 'form']],
                target: 'current',
                view_mode:'form',
                view_type:'form',
            });
        },
        
	/* View All */
        showalllist: function (event) {
            var self = this;
            this.rpc('/web/action/run', {
		action_id: 2772,
                context: {'themodule':$(event.currentTarget).data('module')}
            }).done(function (action) {
                self.do_action(action, {res_model: $(event.currentTarget).data('module')});
            });
        },

	/* Propose a Trip,Add Position,Add Property */        
        createitem: function (event) {
            this.do_action({
                type: 'ir.actions.act_window',
                res_model: $(event.currentTarget).data('module'),
                views: [[false, 'form']],
                target: 'current',
                view_mode:'form',
                view_type:'form',
            });
        },
        
	/* Send SMS Wizard */
        openwizard: function (event) {
            this.do_action({
                type: 'ir.actions.act_window',
                res_model: $(event.currentTarget).data('module'),
                views: [[false, 'form']],
                target: 'new',
                view_mode:'form',
                view_type:'form',
                context:{'auser':manpowerUser.id,'sender':manpowerUser.name,'mobile':$(event.currentTarget).data('mobile')},
            });
        },
        
	});
	
	instance.web.client_actions.add('acesmanpower.homepage', 'instance.acesmanpower.TripeventsPage');
}




