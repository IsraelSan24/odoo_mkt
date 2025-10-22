odoo.define('mkt_blacklist.blacklist', function (require) {
    'use strict';

    var ajax = require('web.ajax');
    var publicWidget = require('web.public.widget');

    publicWidget.registry.BlacklistSearch = publicWidget.Widget.extend({
        selector: '.s_mkt_blacklist_section',
        events: {
            'click #btnSearch': '_onSearchClick',
            'keypress #searchInput': '_onKeyPress',
        },

        start: function () {
            this.$searchInput = this.$('#searchInput');
            this.$btnSearch = this.$('#btnSearch');
            this.$loadingSpinner = this.$('#loadingSpinner');
            this.$resultContainer = this.$('#resultContainer');
            this.$errorMessage = this.$('#errorMessage');
            return this._super.apply(this, arguments);
        },

        _onSearchClick: function (ev) {
            ev.preventDefault();
            this._performSearch();
        },

        _onKeyPress: function (ev) {
            if (ev.which === 13) {
                ev.preventDefault();
                this._performSearch();
            }
        },

        _performSearch: function () {
            var self = this;
            var searchTerm = this.$searchInput.val().trim();

            if (!searchTerm) {
                this._showError('Por favor, ingrese un término de búsqueda');
                return;
            }

            this.$resultContainer.hide();
            this.$errorMessage.hide();

            this.$loadingSpinner.show();
            this.$btnSearch.prop('disabled', true);

            ajax.jsonRpc('/blacklist/search', 'call', {
                search_term: searchTerm
            }).then(function (result) {
                self.$loadingSpinner.hide();
                self.$btnSearch.prop('disabled', false);

                if (result.success) {
                    self._displayResult(result);
                } else {
                    self._showError(result.message || 'No se encontraron resultados');
                }
            }).catch(function (error) {
                self.$loadingSpinner.hide();
                self.$btnSearch.prop('disabled', false);
                self._showError('Error al realizar la búsqueda. Por favor, intente nuevamente.');
                console.error('Error AJAX /blacklist/search:', error);
            });
        },

        _displayResult: function (result) {
            var partner = result.partner || {};
            var isBlacklisted = (typeof partner.is_blacklisted !== 'undefined') ? partner.is_blacklisted : result.is_blacklisted;

            if (result.field_exists === false) {
                this.$('#alertMessage').removeClass('alert-success alert-danger').addClass('alert-warning');
                this.$('#alertIcon').removeClass('fa-check-circle fa-exclamation-triangle').addClass('fa-exclamation-circle');
                this.$('#alertText').text(result.message || 'El campo "blacklist" no está disponible en este sistema.');
                var $statusBadge = this.$('#statusBadge');
                $statusBadge.removeClass('badge-success badge-danger').addClass('badge-secondary')
                    .css('background-color', '#6c757d')
                    .html('<i class="fa fa-info-circle me-2"></i>CAMPO NO DISPONIBLE');
            } else {
                var $alertMessage = this.$('#alertMessage');
                var $alertIcon = this.$('#alertIcon');
                var $alertText = this.$('#alertText');

                $alertMessage.removeClass('alert-success alert-danger alert-warning');

                if (isBlacklisted) {
                    $alertMessage.addClass('alert-danger');
                    $alertIcon.removeClass('fa-check-circle').addClass('fa-exclamation-triangle');
                    $alertText.text(result.message);
                } else {
                    $alertMessage.addClass('alert-success');
                    $alertIcon.removeClass('fa-exclamation-triangle').addClass('fa-check-circle');
                    $alertText.text(result.message);
                }

                var $statusBadge = this.$('#statusBadge');
                if (isBlacklisted) {
                    $statusBadge.removeClass('badge-success').addClass('badge-danger')
                        .css('background-color', '#dc3545')
                        .html('<i class="fa fa-ban me-2"></i>EN LISTA NEGRA');
                } else {
                    $statusBadge.removeClass('badge-danger').addClass('badge-success')
                        .css('background-color', '#28a745')
                        .html('<i class="fa fa-check-circle me-2"></i>CONTACTO VÁLIDO');
                }
            }

            this.$('#contactName').text(partner.name || '—');
            this.$('#contactVat').text(partner.vat || '—');
            this.$('#contactEmail').text(partner.email || '—');
            this.$('#contactPhone').text(partner.phone || '—');
            this.$('#contactReason').text(partner.blacklist_reason || '—');
            this.$('#contactDate').text(partner.blacklist_date || '—');

            this.$resultContainer.hide().slideDown(400);
        },

        _showError: function (message) {
            this.$('#errorText').text(message);
            this.$errorMessage.hide().slideDown(400);
            setTimeout(() => {
                this.$errorMessage.slideUp(400);
            }, 5000);
        },
    });

    return publicWidget.registry.BlacklistSearch;
});