odoo.define('autoreload', function (require){
    'use strict';

    var ListView = require('web.ListRenderer');
    var KanbanView = require('web.KanbanRenderer');
    var ListController = require('web.ListController');
    var KanbanController = require('web.KanbanController');

    var controller;
    var interval;

    function isBlockUI () {
        var tmp = $('body').hasClass('o_ui_blocked');
        return !!tmp;
    }

    ListController.include({
        init: function (parent, model, renderer, params) {
            this._super.apply(this, arguments);
            controller = this;
        },
        renderPager: function () {
            return this._super.apply(this, arguments);
        }
    });

    KanbanController.include({
        init: function (parent, model, renderer, params) {
            this._super.apply(this,arguments);
            controller = this;
        },
        renderPager: function () {
            controller = this;
            return this._super.apply(this, arguments);
        }
    });

    ListView.include({
        init: function (viewInfo, params) {
            controller = this;
            this._super.apply(this, arguments);
            if (interval) {
                clearInterval(interval);
            }
            var auto_class = this.arch.attrs.class;
            if (auto_class && auto_class.indexOf('auto_reload') >= 0) {
                var timeout = 5000;
                var re = /auto_reload_(\d+)/;
                var arr = re.exec(auto_class);
                if (arr) {
                    timeout = parseInt(arr[1]);
                }
                interval = setInterval(function () {
                    try {
                        if (!isBlockUI()) {
                            controller.reload();
                        }
                    } catch (e) {
                        console.log(e);
                        console.error(e);
                    }
                }, timeout);
            }
        },
    });

    KanbanView.include({
        init: function (viewInfo, params) {
            controller = this;
            this._super.apply(this, arguments);
            if (interval) {
                clearInterval(interval);
            }
            var auto_class = this.arch.attrs.class;
            if (auto_class && auto_class.indexOf('auto_reload') >= 0) {
                var timeout = 5000;
                var re = /auto_reload_(\d+)/;
                var arr = re.exec(auto_class);
                if (arr) {
                    timeout = parseInt(arr[1]);
                }
                interval = setInterval(function () {
                    try {
                        if (!isBlockUI()) {
                            controller.reload();
                        }
                    } catch (e) {
                        console.log(e);
                        console.error(e);
                    }
                }, timeout);
            }
        }
    });
});