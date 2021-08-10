(function () {
    'use strict';

    var instance = openerp;
    var website = openerp.website;
    var _t = openerp._t;
    var _lt = openerp._lt;
    var QWeb = openerp.qweb;

    website.Locator = openerp.Widget.extend({
        init: function (parent, db, action, id, view, attendee_data) {
            this._super(parent);

        },
        get_location: function () {
            var self = this.$el;

            self.find("div.address_stores")

            var pos;

            if (navigator.geolocation) {
                navigator.geolocation.getCurrentPosition(function (position) {
                    pos = {
                        ok: true,
                        lat: position.coords.latitude,
                        lng: position.coords.longitude
                    };

                    var s = new instance.Session();
                    s.rpc('/locate/store', {lat: pos.lat, lng: pos.lng}).then(function (result) {
                        self.html(result.location );
                        console.log("Latitud:" + pos.lat + " Longitud:" + pos.lng + " Tienda:" + result.location);

                    });

                });
            }


        }
    });

    website.ready().done(function () {
        $(document.body).on('click', 'div[data-action=get_location]', function () {
            var locator = new website.Locator(this);
            locator.setElement($('.address_store'));
            locator.get_location();
        });
    });

})();


function auto_location(){
    $(".auto_location").click();
};
window.onload = function(){
    setTimeout(function(){
        auto_location();
    }, 2000);
};
