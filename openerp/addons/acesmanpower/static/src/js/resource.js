openerp.acesmanpower = function (instance)
{   
    instance.web.form.widgets.add('test', 'instance.acesmanpower.Mywidget');
    instance.acesmanpower.Mywidget = instance.web.form.FieldChar.extend(
        {
        template : "test",
        init: function (view, code) {
            this._super(view, code);
            console.log('loading...');
        }
    });
}
