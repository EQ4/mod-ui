/*
 * Copyright 2012-2013 AGR Audio, Industria e Comercio LTDA. <contato@moddevices.com>
 *
 * This program is free software: you can redistribute it and/or modify
 * it under the terms of the GNU General Public License as published by
 * the Free Software Foundation, either version 3 of the License, or
 * (at your option) any later version.
 *
 * This program is distributed in the hope that it will be useful,
 * but WITHOUT ANY WARRANTY; without even the implied warranty of
 * MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
 * GNU General Public License for more details.
 *
 * You should have received a copy of the GNU General Public License
 * along with this program.  If not, see <http://www.gnu.org/licenses/>.
 */

/* The method below is already implemented in modgui.js.
 * The reason it's there and not here is because  modgui.js is a standalone implementation
 * of modgui LV2 standards and should not depend of anything from this package (it's also used in modsdk)
 * We kept it commented here because this is where it used to belong, and it's weird to have this so core
 * function being declared only in modgui.js.
 */
/*
function JqueryClass(name, methods) {
    (function($) {
	$.fn[name] = function(method) {
	    if (methods[method]) {
		return methods[method].apply(this, Array.prototype.slice.call(arguments, 1));
	    } else if (typeof method === 'object' || !method) {
		return methods.init.apply(this, arguments);
	    } else {
		$.error( 'Method ' +  method + ' does not exist on jQuery.' + name );
	    }
	}
    })(jQuery);
}
*/

(function ($) {
    $.fn.cleanableInput = function (options) {
        var self = $(this)
        var remove = $('<span class="input-clean">x</span>')
        remove.insertAfter(self)

        var position = function () {
            remove.show()
            remove.css('left', self.position().left + self.width() - 3)
            remove.css('top', self.position().top + self.height() - 22)
        }

        remove.click(function () {
            self.val('')
            remove.hide()
            self.trigger('keyup')
        })

        if (self.val().length == 0)
            remove.hide()
        else
            position()

        self.keyup(function () {
            if (self.val().length > 0)
                position()
            else
                remove.hide()
        })

    }
})(jQuery);

(function ($) {
    $.extend($.expr[":"], {
        scrollable: function (element) {
            var vertically_scrollable, horizontally_scrollable;
            if ($(element).css('overflow') == 'scroll' || $(element).css('overflowX') == 'scroll' || $(element).css('overflowY') == 'scroll') return true;

            vertically_scrollable = (element.clientHeight < element.scrollHeight) && (
                $.inArray($(element).css('overflowY'), ['scroll', 'auto']) != -1 || $.inArray($(element).css('overflow'), ['scroll', 'auto']) != -1);

            if (vertically_scrollable) return true;

            horizontally_scrollable = (element.clientWidth < element.scrollWidth) && (
                $.inArray($(element).css('overflowX'), ['scroll', 'auto']) != -1 || $.inArray($(element).css('overflow'), ['scroll', 'auto']) != -1);
            return horizontally_scrollable;
        }
    });
})(jQuery)

function setCookie(name, value, days) {
    if (days) {
        var date = new Date();
        date.setTime(date.getTime() + (days * 24 * 60 * 60 * 1000));
        var expires = "; expires=" + date.toGMTString();
    } else var expires = "";
    document.cookie = name + "=" + value + expires + "; path=/";
}

function getCookie(c_name, defaultValue) {
    if (document.cookie.length > 0) {
        c_start = document.cookie.indexOf(c_name + "=");
        if (c_start != -1) {
            c_start = c_start + c_name.length + 1;
            c_end = document.cookie.indexOf(";", c_start);
            if (c_end == -1) {
                c_end = document.cookie.length;
            }
            return unescape(document.cookie.substring(c_start, c_end));
        }
    }
    if (defaultValue)
        return defaultValue
    return "";
}

function renderTime(time) {
    var months = ['Jan',
        'Feb',
        'Mar',
        'Apr',
        'May',
        'Jun',
        'Jul',
        'Aug',
        'Sep',
        'Oct',
        'Nov',
        'Dec'
    ]
    return sprintf('%s %02d %02d:%02d',
        months[time.getMonth()],
        time.getDate(),
        time.getHours(),
        time.getMinutes())
}

function remove_from_array(array, element) {
    var index = array.indexOf(element)
    if (index > -1)
        array.splice(index, 1)
}
