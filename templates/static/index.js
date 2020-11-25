var username = 'user';

// feedback stuff
function showFeedback() {
    document.getElementById("feedback").hidden = false;
    document.getElementById("show-feedback").hidden = true;
}

$(document).ready(function(){
    //connect to the socket server.
    var socket = io.connect('http://' + document.domain + ':' + location.port);
    var numbers_received = [];

    var chatbox = document.getElementById("chatbox");
    var user_input = document.getElementById("usermsg");

    user_input.focus();

    

    // adding elements to chat
    var add_text = function (uname, entered_text) {
        if(uname === 'SCITalk') {
            $("#chatbox").append('<div class="row"> <div class="col"><b style="color:#FF0000">' + uname + ': </b>' + entered_text + '</div> </div>')
        }
        else {
            $("#chatbox").append('<div class="row"> <div class="col"><b>' + uname + ': </b>' + entered_text + '</div> </div>')
        }
        
        $("#usermsg").val("")
    }

    var add_images = function (uname, images) {
        if (images === [])
            return;
        for (i = 0; i < images.length; i++) {
            var d = new Date();
            $("#chatbox").append('<div class="row"> <div class="col"><img class="chat-img" src=' + images[i] + '?ver=' + d.getTime() + '></div> </div>');
        }
    }

    var clear_chat = function () {
        console.log("clearing chat...");
        $("#chatbox").html('');
    }

    var save_conversation = function() {
        // for now lets just save the html
        return chatbox.innerHTML
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
            chatbox.scrollTop = chatbox.scrollHeight;
        })

        var form = $('#msg-form').on('submit', function(e) {
            e.preventDefault()
            var entered_text = $("#usermsg").val()
            if(entered_text !== "") {
                add_text(username, entered_text)
                socket.emit('sendout', {
                    'question': entered_text,
                    'name': username,
                    'code': '',
                    'images': [],
                    'relation': ''
                })
                chatbox.scrollTop = chatbox.scrollHeight;
            }
        })

        var feedback = $('#feedback-form').on('submit', function(e) {
            e.preventDefault()
            // get comments
            var comments = $("#comments").val()
            // did it answer correctly?
            var correct = $("#f-yes").checked
            // date
            var date = Date(Date.now());
            // save conversation
            var conversation = save_conversation();
            // send it to flask
            socket.emit('feedback', {
                'comments': comments,
                'corrent': correct,
                'conversation': conversation,
                'date': date.toString()
            })
            
        })
    });

    socket.on('response', function(utterance) {
        console.log('This is the response for user:', utterance)
        add_text(utterance.name, utterance.question)
        add_images(utterance.name, utterance.images)
        chatbox.scrollTop = chatbox.scrollHeight;
    })

    socket.on('command', function(utterance) {
        console.log('Command received:', utterance);
        console.log("1");
        if(utterance === "clear") {
            console.log("2");
            clear_chat();
        }
        //add_text(utterance.name, utterance.question)
        chatbox.scrollTop = chatbox.scrollHeight;
    })

    socket.on('feedback_confirm', function() {
        document.getElementById("feedback").innerHTML = "Thank you for your feedback!";
    })
})

