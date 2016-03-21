
openerp.urlc_image  = function(instance) {
    var QWeb = instance.web.qweb;
    instance.urlc_image.UImage = instance.web.form.AbstractField.extend({
        placeholder: "/web/static/src/img/placeholder.png",

        render_value: function() {
            var self = this;
            var url = this.get('value');
            var $img = $(QWeb.render("UImage", { widget: this, url: url }));
            this.$el.find('> img').remove();
            this.$el.prepend($img);
            $img.load(function() {
                if (! self.options.size)
                    return;
                $img.css("max-width", "" + "128" + "px");
                $img.css("max-height", "" + "128" + "px");
            });
            $img.on('error', function() {
                $img.attr('src', self.placeholder);
                //instance.webclient.notification.warn(_t("Image"), _t("Could not display the selected image."));
            });
        },

    });

    instance.web.form.widgets.add('uimage', 'instance.urlc_image.UImage');
};
