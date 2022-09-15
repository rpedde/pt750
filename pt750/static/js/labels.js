var active_label = 'text'

function onload() {
    update_config()
    set_label('text')
}

function set_label(what) {
    var elements = {
        text: {
            lines: true,
            label: false,
            qrtext: false,
            length: false,
        },
        qr: {
            lines: true,
            label: false,
            qrtext: true,
            length: false,
        },
        wrap: {
            lines: false,
            label: true,
            qrtext: false,
            length: true,
        },
        flag: {
            lines: false,
            label: true,
            qrtext: false,
            length: false,
        }
    }

    for (let [k, v] of Object.entries(elements[what])) {
        // show/hide the appropriate elements
        let divname = '#' + k + "_div"

        if(v) {
            $(divname).show()
        } else {
            $(divname).hide()
        }

    }

    keys = Object.keys(elements)
    for(index = 0; index < keys.length; index++) {
        if (keys[index] != what) {
            $('#' + keys[index] + "_nav").removeClass('active')
        } else {
            $('#' + keys[index] + "_nav").addClass('active')
        }
    }

    active_label = what
    update_preview()
}

function update_config() {
    $.ajax({
        type: "GET",
        dataType: "json",
        url: "/config",
        async: false
    }).done(function(data) {
        tapes = data["tapes"]

        for(index = 0; index < tapes.length; index++) {
            $('#tape').append('<option value="' + tapes[index] + '">' + tapes[index] + '</option>')
        }

        printers = data["printers"]
        for(index = 0; index < printers.length; index++) {
            $('#printer').append('<option value="' + printers[index] + '">' + printers[index] + '</option>')
        }

        fonts = data["fonts"]
        for(index = 0; index < fonts.length; index++) {
            opt = '<option value="' + fonts[index] + '">' + fonts[index] + '</option>'
            $('#fontname').append(opt)
        }
    }).fail(function(jqXHR) {
        $('#warning_div').removeClass('alert-success')
        $('#warning_div').addClass('alert-danger')
        $('#warning_div').html('Failure: ' + jqXHR.responseText)
    })
}

function get_request_json() {
    var fields = {
        text: ['printer', 'tape', 'fontname', 'size', 'align', 'lines'],
        qr: ['printer', 'tape', 'fontname', 'size', 'align', 'qrtext', 'lines'],
        wrap: ['printer', 'tape', 'fontname', 'label', 'length'],
        flag: ['printer', 'tape', 'fontname', 'size', 'label']
    }

    var request = {
        'label_type': active_label
    }

    flist = fields[active_label]
    for(index = 0; index < flist.length; index++) {
        if (flist[index] == 'align') {
            checked = $('input[name=align]:checked', '#text-form').val()
            request['align'] = checked
        } else if (flist[index] == 'lines') {
            linearray = $('#lines').val().split('\n')
            request['lines'] = linearray

        } else {
            request[flist[index]] = $('#' + flist[index]).val()
            if(flist[index] == 'length') {
                request['length'] = 128 * Number(request['length'])
            }
        }
    }

    request['label_type'] = active_label

    request = {'label': request,
               'count': 1}

    request = JSON.stringify(request)

    console.log(request)

    return request
}

function print() {
    request = get_request_json()

    $.ajax({
        type: "PUT",
        dataType: "json",
        url: "/print",
        contentType: "application/json",
        data: request
    }).done(function(data) {
        $('#warning_div').removeClass('alert-danger')
        $('#warning_div').addClass('alert-success')
        $('#warning_div').html('Printed')
    }).fail(function(jqXHR) {
        $('#warning_div').removeClass('alert-success')
        $('#warning_div').addClass('alert-danger')
        $('#warning_div').html('Failure: ' + jqXHR.responseText)
    })
}

function update_preview() {
    request = get_request_json()

    max_size = Math.trunc($('#preview_div').width())

    $.ajax({
        type: "PUT",
        dataType: "json",
        url: "/preview?max_width="+max_size,
        contentType: "application/json",
        data: request
    }).done(function(data) {
        new_label = data["height"] + " in X " + data["width"] + " in"
        $('#preview_label').html(new_label)
        $('#preview').attr('src', 'data:image/png;base64,' + data["preview"])
        $('#warning_div').removeClass('alert-danger')
        $('#warning_div').addClass('alert-success')
        $('#warning_div').html('Ok')
    }).fail(function(jqXHR) {
        $('#warning_div').removeClass('alert-success')
        $('#warning_div').addClass('alert-danger')
        $('#warning_div').html('Failure: ' + jqXHR.responseText)
    })

}
