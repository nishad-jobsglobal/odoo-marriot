openerp.testwidget = function(instance, local) {
    var _t = instance.web._t,
        _lt = instance.web._lt;
    var QWeb = instance.web.qweb;
    
    var TestClass = instance.web.Class.extend({
        testMethod: function() {
            return "hello";
        },
    });

    TestClass.include({
        testMethod: function() {
            return this._super() + " world";
        },
    });

    
    
    
    local.ConfirmWidget = instance.Widget.extend({
        events: {
            'click button.ok_button': function () {
                this.trigger('user_chose', true);
            },
            'click button.cancel_button': function () {
                this.trigger('user_chose', false);
            }
        },
        start: function() {
            this.$el.append("<div>Are you sure you want to perform this action?</div>" +
                "<button class='ok_button'>Ok</button>" +
                "<button class='cancel_button'>Cancel</button>");
        },
    });

    local.TestwidgetPage = instance.Widget.extend({
        template: "HomePageTemplate",
        init: function(parent) {
            this._super(parent);
            this.name = "Mordecai";
        },
        
        events: {
            "click .my_button": "button_clicked",
        },
        
        button_clicked: function() {
            console.log("test widget home page loaded");
        },
        
        
        start: function() {
            //this.$el.append("<div class='widgetcontainer'><iframe src='http://jobsglobal.dev' frameborder='0' scrolling='no' id='iframe' style='height: 800px; width: 350px;' );\"></iframe></div>");
            //this.$el.append( QWeb.render("HomePageTemplate", {name: "Klaus"}) );
            var widget = new local.ConfirmWidget(this);
            widget.on("user_chose", this, this.user_chose);
            widget.appendTo(this.$el);
            
            console.log(new TestClass().testMethod());
          
            
            
            
        },
        
        user_chose: function(confirm) {
            if (confirm) {
                console.log("The user agreed to continue");
            } else {
                console.log("The user refused to continue");
            }
        },
        
        
    });
    
    

    instance.web.client_actions.add('testwidget.homepage', 'instance.testwidget.TestwidgetPage');
}
