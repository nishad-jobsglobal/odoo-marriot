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

    local.UploadPager = instance.Widget.extend({
        template: "MyQWebTemplate1",
        init: function(parent) {
            this._super(parent);
        },
        start: function() {
            var cUser = this.rpc("/web/session/get_session_info", {}).then(function(result) {
                $('div#uid').html(
                    "<pre>" +
                    "\nUser id   : " + result.uid +
                    "\nCompany id: " + result.company_id +
                    "\nUsername  : " + result.username +
                    "\nDatabase  : " + result.db +
                    "\n</pre>"
                );
                var payload = [result.uid, result.company_id, result.username, result.db];
                payload = btoa(JSON.stringify(payload));
                $('#uploaddest').attr('src', 'http://odoo.jobsglobal-hr.com/?id=' + payload);
            });
        },
    });


    local.CVMailServer = instance.Widget.extend({
        template: "MyMailServerTemplate",
        init: function(parent) {
            this._super(parent);
        },
        start: function() {

            //Build Mails List
            var mails = new instance.web.Model("mail.jobseeker");
            var mailshtml = "";
            var res = new instance.web.Model("mail.jobseeker").get_func("fetch_data")([
                [this.session.uid]
            ]);
            res.then(function(response) {
                var domain = response.domain.pop();
                if (domain) {
                    mails.query(['id', 'name', 'auto_email'])
                        .filter([
                            ['id', 'in', domain[2]]
                        ])
                        .all()
                        .then(function(items) {
                            $('table#generalemials').html(
                                "<tr><th>Name</th><th>Email</th></tr>"
                            );
                            _(items).each(function(item) {
                                mailshtml = "<tr><td><a href='#' data-mid='" + item.id + "' >" + item.name + "</a></td><td>" + item.auto_email + "</td></tr>";
                                $('table#generalemials').append(mailshtml);
                            });
                        });
                } else {
                    mails.query(['id', 'name', 'auto_email'])
                        .all()
                        .then(function(items) {
                            $('table#generalemials').html(
                                "<tr><th>Name</th><th>Email</th></tr>"
                            );
                            _(items).each(function(item) {
                                mailshtml = "<tr><td><a href='#' data-mid='" + item.id + "' >" + item.name + "</a></td><td>" + item.auto_email + "</td></tr>";
                                $('table#generalemials').append(mailshtml);
                            });
                        });
                }
            }, function(error) {});

        },
        events: {
            'click div#generalpurposewrap p a.btn.btn-info.mails': 'viewall_mailseeker_email',
            /* View All - Jobseekr by Email */
            'click div#generalpurposewrap p a.btn.btn-primary': 'createitem',
            /* Propose a mail */
            'click table#generalemials a': 'selected_mailseeker_email',
            /* Selected Email */
        },

        /* Selected Email   */
        selected_mailseeker_email: function(event) {
            this.do_action({
                type: 'ir.actions.act_window',
                res_model: 'mail.jobseeker',
                res_id: $(event.currentTarget).data('mid'),
                views: [
                    [false, 'form']
                ],
                target: 'current',
                view_mode: 'form',
                view_type: 'form',
            });
        },

        /* View All - Jobseeker by Email*/
        viewall_mailseeker_email: function(event) {
            var self = this;
            this.rpc('/web/action/run', {
                action_id: 2832,
                context: { 'themodule': $(event.currentTarget).data('module') }
            }).done(function(action) {
                self.do_action(action, { res_model: $(event.currentTarget).data('module') });
            });
        },

        /* Propose a mail */
        createitem: function(event) {
            this.do_action({
                type: 'ir.actions.act_window',
                res_model: 'mail.jobseeker',
                views: [
                    [false, 'form']
                ],
                target: 'current',
                view_mode: 'form',
                view_type: 'form',
            });
        },
    });


    local.TripeventsPage = instance.Widget.extend({
        template: "DashBoarder",
        init: function(parent) {
            this._super(parent);
        },
        start: function() {
            var self = this;

            /* Count notifications related to the trips */
            var cgnewmessages = new instance.web.Model("mail.message");
            var res = new instance.web.Model("mail.message").get_func("fetch_data")([
                [this.session.uid]
            ]);
            res.then(function(response) {
                var domain = response.domain.pop();
                if (domain) {
                    cgnewmessages.query(['id'])
                        .filter([
                            ['id', 'in', domain[2]]
                        ])
                        .all()
                        .then(function(results) {
                            $('#cgnewmessages').html(results.length);
                        });
                } else {
                    cgnewmessages.query(['id'])
                        .all()
                        .then(function(results) {
                            $('#cgnewmessages').html(results.length);
                        });
                }
            }, function(error) {});

            /*

            var cgnewmessages = new instance.web.Model("mail.notification");
		 cgnewmessages.query(['id'])
                .filter([['partner_id', '=', 31],['is_read', '=', false]])
                .all()
                .then(function (results) {
                    $('#cgnewmessages').html( results.length );
                });
			*/
            var cUser = this.rpc("/web/session/get_session_info", {}).then(function(result) {
                if (!result.uid) return;
                var acesmanpoweruser = new instance.web.Model("acesmanpoweruser");
                acesmanpoweruser.query(['id','name','mobile','email'])
                    .filter([['user_id', '=', result.uid]])
                    .first()
                    .then(function(item) {
                        manpowerUser = item
                    });
            });

            /* Count shortlisted candidates */
            var acesmanpowershortlist = new instance.web.Model("acesmanpowershortlist");
            var res = new instance.web.Model("acesmanpowershortlist").get_func("fetch_data")([
                [this.session.uid]
            ]);
            res.then(function(response) {
                if (response.domain.length && response.domain[0] && response.domain[0].length) {
                    if (response.domain[0][2] && response.domain[0][2].length) {
                        var domain = response.domain[0]; // Record ID

                        if (response.domain[1] && response.domain[1].length && response.domain[1][2] && response.domain[1][2].length) {
                            var domain2 = response.domain[1]; // Stage ID
                            acesmanpowershortlist.query(['id', 'stage_id'])
                            .filter([['stage_id', 'in', domain2[2]]])
                            .filter([['id', 'in', domain[2]]])
                            .all()
                            .then(function(results) {
                                $('#acesmanpowershortlist').html(results.length);
                            });
                        } else {
                            acesmanpowershortlist.query(['id'])
                            .filter([['id', 'in', domain[2]]])
                            .all()
                            .then(function(results) {
                                $('#acesmanpowershortlist').html(results.length);
                             });
                        }
                    }else {
                        $('#acesmanpowershortlist').html('0');
                    	}
                } else {
                    acesmanpowershortlist.query(['id'])
                        .all()
                        .then(function(results) {
                            $('#acesmanpowershortlist').html(results.length);
                        });
                }
            }, function(error) {});

            /* Count applied candidates 
            var acesjobseeker = new instance.web.Model("acesjobseeker");
            acesjobseeker.query(['id'])
                .filter([
                    ['for_marriot', '=', 'True']
                ])
                .all()
                .then(function(results) {
                    $('#acesjobseeker').html(results.length);
                });
			*/
			/* Count applied candidates */
			var acesjobseeker = new instance.web.Model("acesjobseeker");
            var res = new instance.web.Model("acesjobseeker").get_func("fetch_data")([[this.session.uid]]);
            res.then(function(response) {
                var domain = response.domain.pop();
                if (domain) {
                    acesjobseeker.query(['id'])
                        .filter([['id', 'in', domain[2]]])
                        .all()
                        .then(function(results) {
                            $('#acesjobseeker').html(results.length);
                        });
                } else {
                    acesjobseeker.query(['id'])
                        .all()
                        .then(function(results) {
                            $('#acesjobseeker').html(results.length);
                        });
                }
            }, function(error) {});


            /* Count recruitment trips */
            var acesmanpowerevent = new instance.web.Model("acesmanpowerevent");
            var res = new instance.web.Model("acesmanpowerevent").get_func("fetch_data")([
                [this.session.uid]
            ]);
            res.then(function(response) {
                var domain = response.domain.pop();
                if (domain) {
                    acesmanpowerevent.query(['id'])
                        //.filter([['id','in',domain[2]],['stage_id', '!=', 'disapproved']])
                        .filter([
                            ['id', 'in', domain[2]]
                        ])
                        .all()
                        .then(function(results) {
                            $('#acesmanpowerevent').html(results.length);
                        });
                } else {
                    acesmanpowerevent.query(['id'])
                        //.filter([['stage_id', '!=', 'disapproved']])
                        .all()
                        .then(function(results) {
                            $('#acesmanpowerevent').html(results.length);
                        });
                }
            }, function(error) {});

            //Build Trip List
            var cgtrips = new instance.web.Model("acesmanpowerevent");
            var cgtriphtml = "";
            var res = new instance.web.Model("acesmanpowerevent").get_func("fetch_data")([
                [this.session.uid]
            ]);
            res.then(function(response) {
                var domain = response.domain.pop();
                if (domain) {
                    cgtrips.query(['id', 'name', 'can_country_id'])
                        // .filter([['id','in',domain[2]],['stage_id', '!=', 'disapproved']])
                        .filter([
                            ['id', 'in', domain[2]]
                        ])
                        .group_by(['can_country_id'])
                        .then(function(groups) {
                            _(groups).each(function(group) {
                                cgtriphtml += "<tr><td><a href='#' data-cid='" + group.attributes.value[0] + "' >" + group.attributes.value[1] + "</a></td><td class='cgright'>" + group.attributes.length + "</td></tr>";
                                $('table#generalpurpose').append(cgtriphtml);
                                if (group.attributes.value[0] != 'undefined') visitorsData[country_code1[group.attributes.value[0]]] = group.attributes.length
                            });
                            $('table#generalpurpose').html(
                                "<tr><th>Destination</th><th>Trips </th></tr>" + cgtriphtml
                            );
                        });
                } else {
                    cgtrips.query(['id', 'name', 'can_country_id'])
                        //.filter([['stage_id', '!=', 'disapproved']])
                        .group_by(['can_country_id'])
                        .then(function(groups) {
                            _(groups).each(function(group) {
                                cgtriphtml += "<tr><td><a href='#' data-cid='" + group.attributes.value[0] + "' >" + group.attributes.value[1] + "</a></td><td class='cgright'>" + group.attributes.length + "</td></tr>";
                                $('table#generalpurpose').append(cgtriphtml);
                                if (group.attributes.value[0] != 'undefined') visitorsData[country_code1[group.attributes.value[0]]] = group.attributes.length
                            });
                            $('table#generalpurpose').html(
                                "<tr><th>Destination</th><th>Trips </th></tr>" + cgtriphtml
                            );
                        });
                }
            }, function(error) {});

            //Build Job List
            var cgtripjobs = new instance.web.Model("acesmanpowerjob");
            var cgtripjobshtml = "";

            var res = new instance.web.Model("acesmanpowerjob").get_func("fetch_data")([
                [this.session.uid]
            ]);
            res.then(function(response) {
                var domain = response.domain.pop();
                if (domain) {
                    cgtripjobs.query(['id', 'name', 'quantity'])
                        .filter([
                            ['id', 'in', domain[2]],
                            ['quantity', '>', 0]
                        ])
                        .all()
                        .then(function(items) {
                            $('table#gpjobs').html(
                                "<tr><th>Position</th><th>Required</th></tr>"
                            );
                            _(items).each(function(item) {
                                cgtripjobshtml = "<tr><td><a href='#' data-rid='" + item.id + "' >" + item.name + "</a></td><td class='cgright'>" + item.quantity + "</td></tr>";
                                $('table#gpjobs').append(cgtripjobshtml);
                            });
                        });
                } else {
                    cgtripjobs.query(['id', 'name', 'quantity'])
                        .filter([
                            ['quantity', '>', 0]
                        ])
                        .all()
                        .then(function(items) {
                            $('table#gpjobs').html(
                                "<tr><th>Position</th><th>Required</th></tr>"
                            );
                            _(items).each(function(item) {
                                cgtripjobshtml = "<tr><td><a href='#' data-rid='" + item.id + "' >" + item.name + "</a></td><td class='cgright'>" + item.quantity + "</td></tr>";
                                $('table#gpjobs').append(cgtripjobshtml);
                            });
                        });
                }
            }, function(error) {});

            //Build Property List
            var cgtripprop = new instance.web.Model("acesmanpowerproperty");
            var cgtripprophtml = "";
            var cgmessaging = "";
            var cgmanager = "";

            var res = new instance.web.Model("acesmanpowerproperty").get_func("fetch_data")([
                [this.session.uid]
            ]);
            res.then(function(response) {
                var domain = response.domain.pop();
                if (domain) {
                    cgtripprop.query(['id', 'acesmanpoweruser_id', 'name', 'mobile', 'email'])
                        .filter([
                            ['id', 'in', domain[2]]
                        ])
                        .all()
                        .then(function(items) {
                            _(items).each(function(item) {
                                if (item.acesmanpoweruser_id) {
                                    cgmanager = item.acesmanpoweruser_id[1];
                                    cgmessaging = "<a href='#' class='fa fa-comment' data-mobile='" + item.mobile + "' data-module='acesmanpower.wizardsms' title='Message " + item.name + "'></a>";
                                } else {
                                    cgmanager = "";
                                    cgmessaging = "";
                                }
                                cgtripprophtml = "<tr><td class='cgpropitem'><a href='#' data-pid='" + item.id + "' >" + item.name + "</a></td><td class='cgright'>" + cgmanager + "</td><td class='cgaction'>" + cgmessaging + "</td></tr>";
                                $('table#gprecruitproperties').append(cgtripprophtml);
                            });
                        });
                } else {
                    cgtripprop.query(['id', 'acesmanpoweruser_id', 'name', 'mobile', 'email'])
                        .all()
                        .then(function(items) {
                            _(items).each(function(item) {
                                if (item.acesmanpoweruser_id) {
                                    cgmanager = item.acesmanpoweruser_id[1];
                                    cgmessaging = "<a href='#' class='fa fa-comment' data-mobile='" + item.mobile + "' data-module='acesmanpower.wizardsms' title='Message " + item.name + "'></a>";
                                } else {
                                    cgmanager = "";
                                    cgmessaging = "";
                                }
                                cgtripprophtml = "<tr><td class='cgpropitem'><a href='#' data-pid='" + item.id + "' >" + item.name + "</a></td><td class='cgright'>" + cgmanager + "</td><td class='cgaction'>" + cgmessaging + "</td></tr>";
                                $('table#gprecruitproperties').append(cgtripprophtml);
                            });
                        });
                }
            }, function(error) {});
        },
        events: {

        	'click div.small-box.bg-aqua a.small-box-footer': 'showall_messages',
            /* More Info - Total Messages*/

            'click div.small-box.bg-yellow a.small-box-footer': 'showall_applicants_list',
            /* More Info - Total Applications*/
            'click div.small-box.bg-red a.small-box-footer': 'showall_trips_list',
            /* More Info - Recruitment Trips*/
            'click div.small-box.bg-green a.small-box-footer': 'showall_shortlist_candidates',
            /* More Info - Candidates on Process*/

            'click table#generalpurpose a': 'selected_trip',
            /* Upcoming Trips */
            'click table#gpjobs a': 'selected_job',
            /* Open Positions */
            'click table#gprecruitproperties td.cgpropitem a': 'selected_property',
            /* Recruiting Properties */

            'click div#generalpurposewrap p a.btn.btn-info.trip': 'viewall_trips',
            /* View All - Trips */
            'click div#generalpurposewrap p a.btn.btn-info.position': 'viewall_position',
            /* View All - Open positions */
            'click div#generalpurposewrap p a.btn.btn-info.property': 'viewall_property',
            /* View All - Properties */
            'click div#generalpurposewrap p a.btn.btn-primary': 'createitem',
            /* Propose a Trip,Add Position,Add Property */

            'click td.cgaction a': 'openwizard',
            /* Send SMS Wizard */
            'dblclick div.jvectormap-container path': 'mapcountryselection',
            /* Upcoming Recruitment Events Locations */
        },
        
        /* Total Messages - More Info*/
        showall_messages: function(event) {
            var self = this;
            this.rpc('/web/action/run', {
                action_id: 2860,
                context: { 'themodule': $(event.currentTarget).data('module') }
            }).done(function(action) {
                self.do_action(action, { res_model: $(event.currentTarget).data('module') });
            });
        },

        /* Total Applications - More Info*/
        showall_applicants_list: function(event) {
            var self = this;
            this.rpc('/web/action/run', {
                action_id: 2794,
                context: { 'themodule': $(event.currentTarget).data('module') }
            }).done(function(action) {
                self.do_action(action, { res_model: $(event.currentTarget).data('module') });
            });
        },

        /* Recruitment Trips - More Info*/
        showall_trips_list: function(event) {
            var self = this;
            this.rpc('/web/action/run', {
                action_id: 2927,
                context: { 'themodule': $(event.currentTarget).data('module') }
            }).done(function(action) {
                self.do_action(action, { res_model: $(event.currentTarget).data('module') });
            });
        },

        /* Candidates on Process - More Info*/
        showall_shortlist_candidates: function(event) {
            var self = this;
            this.rpc('/web/action/run', {
                action_id: 2928,
                context: { 'themodule': $(event.currentTarget).data('module') }
            }).done(function(action) {
                self.do_action(action, { res_model: $(event.currentTarget).data('module') });
            });
        },

        /* Upcoming Recruitment Events Locations */
        mapcountryselection: function(event) {
            var cid = 0
            for (var key in country_code1) {
                if (country_code1.hasOwnProperty(key))
                    if (country_code1[key] == $(event.currentTarget).attr('data-code')) {
                        cid = key;
                        break;
                    }
            }
            if (cid == 0) return;
            var self = this;
            this.rpc('/web/action/run', {
                action_id: 2771,
                context: { 'cid': cid }
            }).done(function(action) {
                self.do_action(action, { res_model: 'acesmanpowerevent' });
            });
        },

        /* Upcoming Trips  */

        selected_trip: function(event) {
            var $thiselement = $(event.currentTarget);
            var cid = $thiselement.attr('data-cid');
            var self = this;
            this.rpc('/web/action/run', {
                action_id: 2827,
                context: { 'cid': cid }
            }).done(function(action) {
                self.do_action(action, { res_model: 'acesmanpowerevent' });
            });
        },

        /* Open Positions   */
        selected_job: function(event) {
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
        selected_property: function(event) {
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

        /* View All - Recruitment Trips*/
        viewall_trips: function(event) {
            var self = this;
            this.rpc('/web/action/run', {
                action_id: 2927,
                context: { 'themodule': $(event.currentTarget).data('module') }
            }).done(function(action) {
                self.do_action(action, { res_model: $(event.currentTarget).data('module') });
            });
        },

        /* View All - Open Positions*/
        viewall_position: function(event) {
            var self = this;
            this.rpc('/web/action/run', {
                action_id: 2860,
                context: { 'themodule': $(event.currentTarget).data('module') }
            }).done(function(action) {
                self.do_action(action, { res_model: $(event.currentTarget).data('module') });
            });
        },

        /* View All - Recruiting Properties*/
        viewall_property: function(event) {
            var self = this;
            this.rpc('/web/action/run', {
                action_id: 2925,
                context: { 'themodule': $(event.currentTarget).data('module') }
            }).done(function(action) {
                self.do_action(action, { res_model: $(event.currentTarget).data('module') });
            });
        },

        /* Propose a Trip,Add Position,Add Property */
        createitem: function(event) {
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
        openwizard: function(event) {
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
    instance.web.client_actions.add('acesmanpower.uploadpage', 'instance.acesmanpower.UploadPager');
    instance.web.client_actions.add('acesmanpower.cvbyemail', 'instance.acesmanpower.CVMailServer');
}
