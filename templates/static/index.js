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
        chat.scrollTop = chat.scrollHeight;
    });

    //receive details from server
    socket.on('newnumber', function(msg) {
        console.log("Received number" + msg.number);
        //maintain a list of ten numbers
        if (numbers_received.length >= 10){
            numbers_received.shift()
        }            
        numbers_received.push(msg.number);
        numbers_string = '';
        for (var i = 0; i < numbers_received.length; i++){
            numbers_string = numbers_string + '<p>' + numbers_received[i].toString() + '</p>';
        }
        $('#log').html(numbers_string);
    });
})

