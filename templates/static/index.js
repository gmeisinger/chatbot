var username = 'user';

$(document).ready(function(){
    //connect to the socket server.
    var socket = io.connect('http://' + document.domain + ':' + location.port);
    var numbers_received = [];

    var chatbox = document.getElementById("chatbox");
    var user_input = document.getElementById("usermsg");

    user_input.focus();

    // adding elements to chat
    var add_text = function (uname, entered_text) {
        $("#chatbox").append(
            '<div class="row"> <div class="col"><b>' + uname + ': </b>' + entered_text + '</div> </div>')
        $("#usermsg").val("")
    }

    socket.on('connect', function () {
        console.log('Socket Connection Establised!')

        var form = $('form').on('submit', function(e) {
            e.preventDefault()
            var entered_text = $("#usermsg").val()
            add_text(username, entered_text)
            socket.emit('sendout', {
                'question': entered_text,
                'name': username,
                'code': '',
                'images': [],
                'relation': ''
            })
        })
        chatbox.scrollTop = chatbox.scrollHeight;
    });

    socket.on('response', function(utterance) {
        console.log('This is the response for user:', utterance)
        add_text(utterance.name, utterance.question)
        chatbox.scrollTop = chatbox.scrollHeight;
    })
})

