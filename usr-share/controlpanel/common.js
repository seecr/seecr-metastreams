/* begin license *
 *
 * "Seecr Metastreams" is a fork of Meresco Harvester that demonstrates
 * the translation of traditional metadata into modern events streams.
 *
 * Copyright (C) 2021 Seecr (Seek You Too B.V.) https://seecr.nl
 *
 * This file is part of "Seecr Metastreams"
 *
 * "Seecr Metastreams" is free software; you can redistribute it and/or modify
 * it under the terms of the GNU General Public License as published by
 * the Free Software Foundation; either version 2 of the License, or
 * (at your option) any later version.
 *
 * "Seecr Metastreams" is distributed in the hope that it will be useful,
 * but WITHOUT ANY WARRANTY; without even the implied warranty of
 * MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
 * GNU General Public License for more details.
 *
 * You should have received a copy of the GNU General Public License
 * along with "Seecr Metastreams"; if not, write to the Free Software
 * Foundation, Inc., 51 Franklin St, Fifth Floor, Boston, MA  02110-1301  USA
 *
 * end license */

function errorMessage(txt) {
    var _box = $("#message-box");
    if (_box != undefined) {
        _box.find("strong").html(txt);
        _box.show();
    }
}

function resetErrorMessage(txt) {
    var _box = $("#message-box");
    if (_box != undefined) {
        _box.hide();
    }
}

function _createElement(tag, attrs, text) {
    var _elem = document.createElement(tag);
    for(var key in attrs) {
        _elem.setAttribute(key, attrs[key]);
    }
    _elem.textContent = text;
    return _elem;
}

function msg_create(placeholder, alertClass, icon, text) {
    var _box = _createElement("div", {
        "class": 'alert alert-dismissible ' + alertClass,
        "role": "alert"
    });
    _box.append(_createElement("i", {"class": icon}));
    _box.append(_createElement("span", {"class": 'ps-2'}, text));
    _box.append(_createElement("button", {
        "type":"button",
        "class":"btn-close",
        "data-bs-dismiss": "alert",
        "aria-label": "Close"
    }));

    placeholder.prepend($(_box));
}


function msg_Error(placeholder=undefined, id=undefined, text="") {
    msg_create(placeholder, "alert-danger", "bi-emoji-frown", text);
}
function msg_Success(placeholder=undefined, id=undefined, text="") {
    msg_create(placeholder, "alert-success", "bi-emoji-smile", text);
}

function form_setBordersAndDisabled(form, button) {
	form.find("input").keyup(function(e) {
        var _input = $(this);
        if (!_input.hasClass("border-warning")) {
            _input.addClass("border-warning");
        }
        if (button.prop('disabled') == true) {
            button.prop('disabled', false);
        }
	});
	form.find("select").change(function(e) {
        var _input = $(this);
        if (!_input.hasClass("border-warning")) {
            _input.addClass("border-warning");
        }
        if (button.prop('disabled') == true) {
            button.prop('disabled', false);
        }
	});
	form.find("textarea").change(function(e) {
        var _input = $(this);
        if (!_input.hasClass("border-warning")) {
            _input.addClass("border-warning");
        }
        if (button.prop('disabled') == true) {
            button.prop('disabled', false);
        }
	});
	form.find("input[type=checkbox]").change(function(e) {
        var _input = $(this);
        if (!_input.hasClass("border-warning")) {
            _input.addClass("border-warning");
        }
        if (button.prop('disabled') == true) {
            button.prop('disabled', false);
        }
	});
	form.find("input[type=number]").change(function(e) {
        var _input = $(this);
        if (!_input.hasClass("border-warning")) {
            _input.addClass("border-warning");
        }
        if (button.prop('disabled') == true) {
            button.prop('disabled', false);
        }
	});
}

function form_resetBordersAndDisabled(form, button, reset) {
    button.prop('disabled', true);
    form.find('.border-warning').each(function() {
        $(this).removeClass('border-warning');
    });
    if (reset) {
        form.trigger('reset');
    }
}

function init_login_dialog(placeholder) {
    var _form = placeholder.find("#FrmLogin");
    placeholder.find("#BtnDoLogin")
        .unbind("click")
        .click(function(e) {
            e.preventDefault();
            $.ajax({
                type: "POST",
                url: "/login.action",
                data: JSON.stringify(_form.serializeArray()),
                dataType: "json",
                success: function(loginResponse) {
                    if (loginResponse['success'] == true) {
                        window.location = loginResponse['url'] || "/";
                    } else {
                        var _box = placeholder.find("#login-message-box");
                        _box.find("strong").html(loginResponse.message);
                        _box.show();
                    }
                }
            });
        });
}


function init_login_button() {
    var _btn = $("#BtnLogin");
    if (_btn != undefined) {
        _btn
            .unbind("click")
            .click(function(e) {
                $.get("/login/dialog/show")
                    .done(function(data) {
                        var _modal = $("#modal");
                        var _body_placeholder = _modal.find("#placeholder_modal-body");
                        _modal.find("#placeholder_modal-title").html("Inloggen");
                        _body_placeholder
                            .empty()
                            .append(data);
                        init_login_dialog(_body_placeholder);
                        _modal.modal('show');
                   })
            })
    }
}

$(document).ready(function () {
    init_login_button();

    $(document).ajaxStart(function () {
        $("html").addClass("wait");
    });
    $(document).ajaxStop(function () {
        $("html").removeClass("wait");
    });
});
