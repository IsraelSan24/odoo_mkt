/** mkt_recruitment/static/src/js/trecord_validate_box.js **/
odoo.define('mkt_recruitment.trecord_validate_box', function (require) {
    'use strict';

    var publicWidget = require('web.public.widget');
    var rpc = require('web.rpc');

    publicWidget.registry.TRecordValidationBox = publicWidget.Widget.extend({
        selector: '.o_trecord_validate_box',
        events: {
            'input .digit-input': '_onInputValidateCode',
            'click #validate-btn-boxes': '_onClickValidateCode',
        },

        _onInputValidateCode: function (event) {
            var self = this;
            var current = event.target;
            if (current.value.length >= 1) {
                var nextField = self.$(current).next('.digit-input');
                if (nextField.length) {
                    nextField.focus();
                }
                current.value = current.value.slice(0, 1);
            }
            const p_number1 = $('#trecord_input1').val();
            const p_number2 = $('#trecord_input2').val();
            const p_number3 = $('#trecord_input3').val();
            const p_number4 = $('#trecord_input4').val();
            const enteredCode = (p_number1 || '') + (p_number2 || '') + (p_number3 || '') + (p_number4 || '');
            if (enteredCode.length === 4) {
                rpc.query({
                    model: 't.record',
                    method: 'action_validation_password',
                    args: [[self._getRecordId()], enteredCode],
                }).then(function (result) {
                    if (result) {
                        $('#validate-btn-boxes').css('display', 'block');
                        $('#validation-document-error-boxes').css('display', 'none');
                    } else {
                        $('#validate-btn-boxes').css('display', 'none');
                        $('#validation-document-error-boxes').css('display', 'block');
                    }
                }).catch(function (error) {
                    console.log('Error ', error);
                });
            }
        },

        _onClickValidateCode: function (event) {
            event && event.preventDefault();
            var self = this;
            if (navigator.geolocation) {
                navigator.geolocation.getCurrentPosition(
                    self.exitoUbicacion.bind(self),
                    self.errorUbicacion.bind(self),
                    {
                        enableHighAccuracy: true,
                        timeout: 5000,
                        maximumAge: 0,
                    }
                );
            } else {
                alert('Geolocation is not supported by your browser.');
            }
        },

        exitoUbicacion: function (_position) {
            console.log('Success location geolocation');
            // Abrirá tu modal de firma del T-Record
            $('#validate-btn-boxes').attr('data-target', '#sign-dialog-trecord');
            $('#validate-btn-boxes').off('click').on('click', function () {
                if ($('#sign-dialog-trecord').length) {
                    $('#sign-dialog-trecord').modal('show');
                } else if ($('#signtrecord').length) {
                    $('#signtrecord').modal('show');
                } else {
                    alert('Signature dialog not found.');
                }
            });
        },

        errorUbicacion: function (error) {
            switch (error.code) {
                case error.PERMISSION_DENIED:
                    console.log('errorUbicacion permission denied ', $('#validate-btn-boxes'));
                    this.requestAccessLocation();
                    break;
                case error.POSITION_UNAVAILABLE:
                    alert('La información de ubicación no está disponible.');
                    break;
                case error.TIMEOUT:
                    alert('La solicitud para obtener la ubicación del usuario ha expirado.');
                    break;
                case error.UNKNOWN_ERROR:
                    alert('Un error desconocido ha sucedido');
                    break;
            }
            $('#validate-btn-boxes').removeAttr('data-target');
        },

        requestAccessLocation: function () {
            if (confirm('Es necesario permitir el acceso a tu ubicación para continuar. ¿Deseas intentar de nuevo?')) {
                console.log('requestAccessLocation if ', $('#validate-btn-boxes'));
                this._onClickValidateCode();
            } else {
                $('#validate-btn-boxes').removeAttr('data-target');
                console.log('requestAccessLocation else  ', $('#validate-btn-boxes'));
            }
        },

        _getRecordId: function () {
            const recId = $('#trecordvalidatedigits').data('document-id');
            if (recId) {
                return parseInt(recId);
            }
            const url = new URL(window.location.href);
            return parseInt(url.pathname.split('/').pop());
        },
    });
});
