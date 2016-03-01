/*
 *    Copyright (C) 2013 Michael Telahun Makonnen <mmakonnen@gmail.com>.
 *    All Rights Reserved.
 *
 *   This program is free software: you can redistribute it and/or modify
 *   it under the terms of the GNU Affero General Public License as published by
 *   the Free Software Foundation, either version 3 of the License, or
 *   (at your option) any later version.
 *
 *   This program is distributed in the hope that it will be useful,
 *   but WITHOUT ANY WARRANTY; without even the implied warranty of
 *   MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
 *   GNU Affero General Public License for more details.
 *
 *   You should have received a copy of the GNU Affero General Public License
 *   along with this program.  If not, see <http://www.gnu.org/licenses/>.
 */

openerp.tapplicant_webcam = function(instance) {
    
    // client action hook
    instance.web.client_actions.add("photo_tapplicant.action", "instance.tapplicant_webcam.action");
    instance.tapplicant_webcam.action = instance.web.Widget.extend({
            
        template: 'photo_tapplicant.action',
           
        events: {
            'click .oe_tapplicant_webcam_close a': 'window_close'
        },
            
        window_close: function() {
            var self = this;
            self.getParent().history_back();
            self.destroy();
        },
            
        init: function(parent, action) {
            this._super(parent, action);
            this.tapplicant_id = action.params.tapplicant_id;
        },
            
        start: function() {
            
            this._super();
                
            var pos = 0;
            var ctx = null;
            var cam = null;
            var image = null;
            var tapplicant_id = this.tapplicant_id;
            
            jQuery("#webcam_tapplicant").webcam({
                width: 480,
                height: 480,
                mode: "callback",
                swffile: "/tapplicant_webcam/static/jscam5.swf",
                onTick: function() {},
                    
                onSave: function(data) {
                    var col = data.split(";");
                    var canvas = document.getElementById("canvas");
                    var ctx = canvas.getContext("2d");
                    var img = image;
                    if (img == null && ctx) {
                        ctx.clearRect(0, 0, 480, 480);
                        img = ctx.getImageData(0, 0, 480, 480);
                    }
                    for(var i = 0; i < 480; i++) {
                        var tmp = parseInt(col[i]);
                        img.data[pos + 0] = (tmp >> 16) & 0xff;
                        img.data[pos + 1] = (tmp >> 8) & 0xff;
                        img.data[pos + 2] = tmp & 0xff;
                        img.data[pos + 3] = 0xff;
                        pos+= 4;
                    }
                    image = img
                    
                    if (pos >= 4 * 480 * 480) {
                        ctx.putImageData(img, 0, 0);
                        vals = {'image': canvas.toDataURL("image/png").replace(/^data:image\/(png|jpg);base64,/, "")};
                        model = new instance.web.Model("tapplicant")
                        if (tapplicant_id)
                            model.call('write', [tapplicant_id, vals]).then(null);
                        pos = 0;
                    }
                },
                
                onCapture: function() {
                    webcam.save();
                },
                
                debug: function (type, string) {
                    jQuery("#status").html(type + ": " + string);
                },
            
                onLoad: function () {
            
                    var cams = webcam.getCameraList();
                    for(var i in cams) {
                        jQuery("#cams").append("<li>" + cams[i] + "</li>");
                    }
                },
            });
        },
    });
};
