###

sse = ->
  source = new EventSource('/notifications/{{user.id}}')
  out = document.getElementById('out')

  source.onmessage = (e) ->
    if e.data != '1'
      send_notification e.data
    return

  return

sse()

if typeof String::startsWith != 'function'
  # see below for better implementation!

  String::startsWith = (str) ->
    @indexOf(str) == 0

send_notification = (message) ->
    if message.startsWith 'b\'notify-print:'
        message = message.replace 'b\'notify-print:',''
        message = message.substring 0, message.length - 1
        message = message.split('#')[0]
        $.notify { message: message }, type: 'info'
    if message.startsWith 'b\'notify-print-link:'
        message = message.replace 'b\'notify-print-link:',''
        message = message.substring 0, message.length - 1
        link = message.split('#')[1]
        $.notify { message: message.split('#')[0], url: link }, type: 'info'
    return message
###
