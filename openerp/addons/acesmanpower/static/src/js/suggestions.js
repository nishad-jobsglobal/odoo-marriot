openerp.acesmanpowerrtrips = function(session) {
    var _t = session.web._t;
    var QWeb = session.web.qweb;

    var suggestions = session.suggestions;
    
    suggestions.Rtrips = session.web.Widget.extend({
    
        init: function () {
            this._super(this, arguments);
            this.acesmanpowerevent = new session.web.DataSetSearch(this, 'acesmanpowerevent');
            this.rtrips = [];
        },
        
        start: function () {
            this._super.apply(this, arguments);
            return this.fetch_rtrips();
        },
    
    });
    
    session.mail.WallSidebar.include({
        start: function () {
            this._super.apply(this, arguments);
            var sug_rtrips = new suggestions.Rtrips(this);
            return sug_rtrips.appendTo(this.$('.oe_suggestions_rtrips'));
        },
    });

};