odoo.define('mkt_recruitment.validation_digits_trecord', function (require) {
    'use strict';

    const publicWidget = require('web.public.widget');
    const rpc = require('web.rpc');
    const core = require('web.core');
    const session = require('web.session');
    const _t = core._t;

    // Logger helpers
    const TAG = '[TREC/validation]';
    const log = (...a) => console.log(TAG, ...a);
    const info = (...a) => console.info(TAG, ...a);
    const warn = (...a) => console.warn(TAG, ...a);
    const error = (...a) => console.error(TAG, ...a);

    function _concatDigits() {
        const d1 = ($('#trecord_input1').val() || '').trim();
        const d2 = ($('#trecord_input2').val() || '').trim();
        const d3 = ($('#trecord_input3').val() || '').trim();
        const d4 = ($('#trecord_input4').val() || '').trim();
        const code = (d1 + d2 + d3 + d4).replace(/\D/g, '').slice(0, 4);
        log('concatDigits ->', { d1, d2, d3, d4, code });
        return code;
    }

    function _watchDigits() {
        const code = _concatDigits();
        if (code.length === 4) {
            $('#validation-document-error-boxes').hide();
            $('#validate-document-btn-boxes').show().prop('disabled', false).html('<i class="fa fa-check"/> Validate Code');
            info('4 digits entered -> show validate button (not validated yet)', code);
        } else {
            $('#validate-document-btn-boxes').hide();
            $('#trecord_digits_holder').val('');
            log('digits incomplete -> hide validate button', code);
        }
    }

    publicWidget.registry.ValidationDigitsTRecord = publicWidget.Widget.extend({
        selector: '.o_trecord_signature_t',

        events: {
            'click #o_open_sign_options_trecord': '_onOpenSignOptions',
        },

        start() {
            info('widget start');
            $(document)
                .on('click.trecord', '#send-trecord-via-sms', this._onSendVia.bind(this, 'sms'))
                .on('click.trecord', '#send-trecord-via-email', this._onSendVia.bind(this, 'email'))
                .on('keyup.trecord change.trecord', '#trecord_input1,#trecord_input2,#trecord_input3,#trecord_input4', _watchDigits)
                .on('input.trecord', '#trecord_input1,#trecord_input2,#trecord_input3,#trecord_input4', this._onDigitInput.bind(this))
                .on('click.trecord', '#validate-document-btn-boxes', this._onValidCode.bind(this))
                .on('click.trecord', '#confirm-sign-trecord', this._onConfirmSign.bind(this));

            return this._super.apply(this, arguments);
        },

        destroy() {
            info('widget destroy -> off .trecord handlers');
            $(document).off('.trecord');
            this._super.apply(this, arguments);
        },

        _trecordId() {
            const id = parseInt(this.$el.data('document-id'));
            log('record id', id);
            return id;
        },

        _token() {
            const tok = this.$el.data('token') || null;
            log('access token present?', !!tok);
            return tok;
        },

        _onDigitInput(ev) {
            const $input = $(ev.target);
            let value = $input.val();

            if (value.length > 1) {
                value = value.charAt(0);
                $input.val(value);
            }

            if (value.length === 1) {
                const $next = $input.next('.digit-input');
                if ($next.length) {
                    $next.focus();
                    log('auto-advance to next input');
                }
            }

            _watchDigits();
        },

        _onOpenSignOptions(ev) {
            ev.preventDefault();
            info('open sign options clicked');
            $('#send-method-error').hide();
            $('#send-method-spinner').hide();
            $('#trecordSignOptionsModal').modal('show');
        },

        _updateVerificationMessage(method) {
            log('update verification message', method);
            if (method === 'email') {
                $('#verification-text').text(_t('We sent a verification code to your email:'));
                $('#email-info').show();
                $('#sms-info').hide();
            } else {
                $('#verification-text').text(_t('We sent a verification code to your mobile phone:'));
                $('#email-info').hide();
                $('#sms-info').show();
            }
        },

        _onSendVia(method, ev) {
            ev.preventDefault();
            const id = this._trecordId();
            if (!id) {
                warn('no record id, abort send via', method);
                return;
            }

            $('#send-method-error').hide();
            $('#send-method-spinner').show();
            $('#send-trecord-via-email, #send-trecord-via-sms').prop('disabled', true);

            info('request_code ->', { id, method, route: `/my/trecord/${id}/request_code` });
            rpc.query({
                route: `/my/trecord/${id}/request_code`,
                params: { method },
            }).then(res => {
                $('#send-method-spinner').hide();
                $('#send-trecord-via-email, #send-trecord-via-sms').prop('disabled', false);
                info('request_code response', res);

                if (res && res.success) {
                    this._updateVerificationMessage(method);
                    $('#trecordSignOptionsModal').modal('hide');
                    $('#trecordSignOptionsModal').one('hidden.bs.modal', function () {
                        $('#trecordvalidatedigits input[type=number]').val('');
                        $('#validate-document-btn-boxes').hide();
                        $('#trecord_digits_holder').val('');
                        $('#trecordvalidatebox').modal('show');
                        $('#trecordvalidatebox').one('shown.bs.modal', function () {
                            $('#trecord_input1').focus();
                        });
                    });
                } else {
                    const msg = (res && (res.error || res.message)) || _t('Error sending code');
                    warn('request_code server error', msg);
                    $('#send-method-error').text(msg).show();
                }
            }).catch((e) => {
                $('#send-method-spinner').hide();
                $('#send-trecord-via-email, #send-trecord-via-sms').prop('disabled', false);
                error('request_code rpc failed', e);
                $('#send-method-error').text(_t('Error sending code. Please try again.')).show();
            });
        },

        _onValidCode(ev) {
            ev.preventDefault();
            const code = _concatDigits();
            info('validate code button clicked', code);

            if (code.length !== 4) {
                $('#validation-document-error-boxes').text(_t('Enter 4 digits.')).show();
                warn('validate -> not 4 digits');
                return;
            }

            const id = this._trecordId();
            if (!id) {
                error('No record ID found');
                $('#validation-document-error-boxes').text(_t('Error: Document not found.')).show();
                return;
            }

            info('Validating code with server...', { id, code });

            $('#validate-document-btn-boxes').prop('disabled', true).html('<i class="fa fa-spinner fa-spin"></i> Validating...');
            $('#validation-document-error-boxes').hide();

            // 🌍 Ejecutar geolocalización en paralelo (no bloquea el flujo)
            this._captureGeolocation(id);

            rpc.query({
                model: 't.record',
                method: 'action_validation_password',
                args: [[id], code],
            }).then(isValid => {
                info('Validation response:', isValid);

                if (isValid === true) {
                    // ✅ Código correcto - guardar y abrir modal de firma
                    $('#trecord_digits_holder').val(code);
                    info('Code validated successfully, saved in holder:', code);

                    const $modalA = $('#sign-dialog-trecord');
                    const $modalB = $('#signtrecord');
                    const $target = $modalA.length ? $modalA : $modalB;

                    if (!$target.length) {
                        error('sign modal NOT found (#sign-dialog-trecord / #signtrecord)');
                        alert(_t('Signature dialog not found. Please reload the page or contact support.'));
                        $('#validate-document-btn-boxes').prop('disabled', false).html('<i class="fa fa-check"/> Validate Code');
                        return;
                    }

                    info('closing #trecordvalidatebox and opening', $target.attr('id'));

                    $('#trecordvalidatebox')
                        .one('hidden.bs.modal', function () {
                            info('#trecordvalidatebox hidden -> show', $target.attr('id'));
                            try {
                                $target.modal('show');

                                $target.one('shown.bs.modal', function () {
                                    info('sign modal shown -> initializing signature');

                                    $('#portal_signature_trecord button[type="submit"]').remove();
                                    $('#portal_signature_trecord .o_portal_sign_submit').remove();
                                    info('Removed auto-generated submit buttons');

                                    const $canvas = $('#portal_signature_trecord canvas');
                                    if ($canvas.length) {
                                        info('Canvas found, ready for signature');

                                        $canvas.on('mouseup touchend', function () {
                                            setTimeout(function () {
                                                const dataURL = $canvas[0].toDataURL('image/png');
                                                $('#portal_signature_trecord input[name="signature"]').val(dataURL);
                                                info('Signature updated in hidden input');
                                            }, 100);
                                        });
                                    } else {
                                        warn('Canvas NOT found!');
                                    }

                                    const $nameInput = $('#portal_signature_trecord input[name="name"]');
                                    if ($nameInput.length && !$nameInput.val().trim()) {
                                        $nameInput.focus();
                                    }
                                });
                            } catch (e) {
                                error('error showing sign modal:', e);
                                alert(_t('Could not open the signature dialog.'));
                            }
                        })
                        .modal('hide');

                } else {
                    // ❌ Código incorrecto
                    warn('Invalid code provided:', code);
                    $('#validation-document-error-boxes').text(_t('Invalid code. Please try again.')).show();
                    $('#validate-document-btn-boxes').prop('disabled', false).html('<i class="fa fa-check"/> Validate Code');

                    $('#trecord_input1, #trecord_input2, #trecord_input3, #trecord_input4').val('');
                    $('#trecord_input1').focus();
                }
            }).catch(err => {
                error('Validation RPC failed:', err);
                $('#validation-document-error-boxes').text(_t('Error validating code. Please try again.')).show();
                $('#validate-document-btn-boxes').prop('disabled', false).html('<i class="fa fa-check"/> Validate Code');
            });
        },

        // 🌍 NUEVO: Capturar geolocalización y enviar al servidor
        _captureGeolocation(trecordId) {
            const self = this;
            info('🌍 Capturing geolocation for t.record:', trecordId);

            // 1. Validar Contexto Seguro (HTTPS)
            if (!window.isSecureContext && window.location.hostname !== 'localhost') {
                const msg = '⚠️ La geolocalización requiere HTTPS. Por favor asegura que el sitio tenga certificado SSL.';
                warn(msg);
                alert(msg); // Alertar visualmente al usuario
                return;
            }

            if (!navigator.geolocation) {
                const msg = '❌ Tu navegador no soporta geolocalización.';
                warn(msg);
                alert(msg);
                return;
            }

            navigator.geolocation.getCurrentPosition(
                function (position) {
                    info('✅ Geolocation obtained:', {
                        lat: position.coords.latitude,
                        lon: position.coords.longitude,
                        accuracy: position.coords.accuracy
                    });

                    // Obtener IP pública
                    fetch('https://api.ipify.org?format=json')
                        .then(response => response.json())
                        .then(data => {
                            const userAgent = navigator.userAgent;
                            const ip = data.ip;

                            info('📍 Sending geolocation to server:', { trecordId, ip });

                            // Enviar al servidor
                            rpc.query({
                                model: 't.record',
                                method: 'geolocation',
                                args: [
                                    [trecordId],
                                    position.coords.latitude,
                                    position.coords.longitude,
                                    ip,
                                    userAgent
                                ],
                            }).then(function (result) {
                                info('✅ Geolocation saved successfully:', result);
                            }).catch(function (error) {
                                error('❌ Error saving geolocation:', error);
                            });
                        })
                        .catch(function (err) {
                            error('❌ Error fetching IP:', err);
                        });
                },
                // 2. Manejo de errores explícito (Popups)
                function (geoError) {
                    let errMsg = 'Error desconocido de ubicación.';
                    switch (geoError.code) {
                        case geoError.PERMISSION_DENIED:
                            errMsg = '🚫 Permiso denegado. Por favor permite el acceso a la ubicación en tu navegador e intenta de nuevo.';
                            break;
                        case geoError.POSITION_UNAVAILABLE:
                            errMsg = '⚠️ La ubicación no está disponible.';
                            break;
                        case geoError.TIMEOUT:
                            errMsg = '⏰ Tiempo de espera agotado al buscar ubicación.';
                            break;
                    }
                    warn('❌ Geolocation error:', geoError.message);
                    alert(errMsg); // IMPORTANTE: Avisar al usuario por qué falló
                },
                {
                    enableHighAccuracy: true,
                    timeout: 10000, // Aumentado a 10s
                    maximumAge: 0
                }
            );
        },

        _onConfirmSign(ev) {
            ev.preventDefault();
            info('=== CONFIRM SIGN START ===');

            const $btn = $(ev.currentTarget);
            $btn.prop('disabled', true);

            const id = this._trecordId();
            const token = this._token();

            const $sigWrap = $('#portal_signature_trecord');
            let name = '';

            if ($sigWrap.length) {
                name = $sigWrap.find('input[name="name"]').val() || '';
            }
            if (!name) {
                name = $('div.modal:visible').find('input[name="name"]').val() || '';
            }
            if (!name) {
                name = $('input[name="name"]').val() || '';
            }
            name = name.trim();

            info('Name found:', name);

            let signature = '';
            const $canvas = $sigWrap.find('canvas');

            if ($canvas.length && $canvas[0].toDataURL) {
                try {
                    const dataURL = $canvas[0].toDataURL('image/png');
                    if (dataURL && dataURL.length > 100) {
                        signature = dataURL;
                        $sigWrap.find('input[name="signature"]').val(dataURL);
                        info('Signature captured from canvas:', `${signature.substring(0, 50)}... (${signature.length} chars)`);
                    } else {
                        warn('Canvas is empty or too small');
                    }
                } catch (e) {
                    error('Canvas toDataURL failed:', e);
                }
            }

            if (!signature) {
                warn('No signature from canvas, trying hidden input...');
                signature = $sigWrap.find('input[name="signature"]').val() || '';
                info('Signature from hidden input:', signature ? `${signature.substring(0, 50)}... (${signature.length} chars)` : 'EMPTY');
            }

            let digits = ($('#trecord_digits_holder').val() || '').trim();
            info('Digits from holder:', digits);

            if (digits.length !== 4) {
                warn('Digits not in holder, concatenating from inputs...');
                digits = _concatDigits();
                info('Digits from inputs:', digits);

                if (digits.length === 4) {
                    $('#trecord_digits_holder').val(digits);
                }
            }

            info('=== PRE-SEND VALIDATION ===');
            info('Record ID:', id);
            info('Token present:', !!token);
            info('Name:', name || 'EMPTY');
            info('Signature length:', signature ? signature.length : 0);
            info('Digits:', digits);

            if (!signature) {
                error('VALIDATION FAILED: No signature');
                alert(_t('Please draw your signature before confirming.'));
                $btn.prop('disabled', false);
                return;
            }

            if (digits.length !== 4) {
                error('VALIDATION FAILED: Digits invalid', digits);
                alert(_t('Please enter a valid 4-digit code.'));
                $btn.prop('disabled', false);
                return;
            }

            info('=== SENDING TO SERVER ===');
            const payload = {
                access_token: token || undefined,
                name: name,
                signature: signature,
                digits: digits,
            };

            info('RPC payload:', {
                route: `/my/trecord/${id}/sign`,
                access_token: !!payload.access_token,
                name: payload.name,
                signature_preview: payload.signature.substring(0, 100) + '...',
                signature_length: payload.signature.length,
                digits: payload.digits
            });

            rpc.query({
                route: `/my/trecord/${id}/sign`,
                params: payload,
            }).then(res => {
                info('=== SERVER RESPONSE ===', res);
                if (res && res.error) {
                    error('Server returned error:', res.error);
                    alert(res.error);
                    $btn.prop('disabled', false);
                    return;
                }
                info('Success! Redirecting to:', (res && res.redirect_url) || '/my/trecord');
                window.location = (res && res.redirect_url) || '/my/trecord';
            }).catch(err => {
                error('=== RPC ERROR ===', err);
                alert(_t('Error processing signature. Please try again.'));
                $btn.prop('disabled', false);
            });
        },
    });

    return publicWidget.registry.ValidationDigitsTRecord;
});