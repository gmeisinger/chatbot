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

    var add_images = function (uname, images) {
        if (images === [])
            return
        for (i = 0; i < images.length; i++) {
            $("#chatbox").append(
                '<div class="row"> <div class="col"><img src=' + '"' + images[i] + '"' + '></div> </div>')
        }
    }

    socket.on('connect', function () {
        console.log('Socket Connection Established!')

        socket.on('init_convo', function(conversation) {
            console.log(conversation)
            for (ind = 0; ind < conversation.length; ind++) {
                add_text(conversation[ind].name, conversation[ind].question)
                //add_code(conversation[ind].name, conversation[ind].code)
                add_images(conversation[ind].name, conversation[ind].images);
            }
            document.getElementById("chatbox").scrollTop = document.getElementById("chatbox").scrollHeight;
        })

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
        add_images(utterance.name, utterance.images)
        chatbox.scrollTop = chatbox.scrollHeight;
        console.log(chatbox.scrollTop);
        console.log(chatbox.scrollHeight);
    })
})

