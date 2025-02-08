var active_label = 'text'
var printer_ready = false

function onload() {
    update_config()
    update_status()
    set_label('text')
}

function set_label(what) {
    var elements = {
        text: {
            lines: true,
            label: false,
            qrtext: false,
            length: false,
            id: false,
            dictionary: false,
        },
        qr: {
            lines: true,
            label: false,
            qrtext: true,
            length: false,
            id: false,
            dictionary: false,
        },
        wrap: {
            lines: false,
            label: true,
            qrtext: false,
            length: true,
            id: false,
            dictionary: false,
        },
        flag: {
            lines: false,
            label: true,
            qrtext: false,
            length: false,
            id: false,
            dictionary: false,
        },
        aruco: {
            lines: true,
            label: false,
            qrtext: false,
            length: false,
            id: true,
            dictionary: true,

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

function update_status(async=false) {
    $.ajax({
        type: "GET",
        dataType: "json",
        url: "/status",
        async: async
    }).done(function(data) {
        printer = $('#printer').val()
        tape = data[printer]["media"]
        ready = data[printer]["ready"]

        if(!ready) {
            $('#warning_div').removeClass('alert-success')
            $('#warning_div').addClass('alert-danger')
            $('#warning_div').html('printer not ready')
        } else {
            if (!printer_ready) {
                $('#warning_div').removeClass('alert-danger')
                $('#warning_div').addClass('alert-success')
                $('#warning_div').html('Ok')
            }
        }

        printer_ready = ready
        $('#tape').val(tape)
    }).fail(function(jqXHR) {
        $('#warning_div').removeClass('alert-success')
        $('#warning_div').addClass('alert-danger')
        $('#warning_div').html('Failure: ' + jqXHR.responseText)
    })
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

	dictionaries = data["dictionaries"]
        for(index = 0; index < dictionaries.length; index++) {
            opt = '<option value="' + dictionaries[index] + '">' + dictionaries[index] + '</option>'
            $('#dictionary').append(opt)
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
        flag: ['printer', 'tape', 'fontname', 'size', 'label'],
	aruco: ['printer', 'tape', 'fontname', 'size', 'align', 'lines', 'id', 'dictionary']
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

    $('#warning_div').removeClass('alert-danger')
    $('#warning_div').addClass('alert-success')
    $('#warning_div').html('Printing...')

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
    update_status()
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
