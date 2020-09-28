var storage = window.sessionStorage;
var num_entries = storage.getItem('num_entries');
var entries_string = storage.getItem('entries');
var entries = [];

if (entries_string === null) {
    entries = [];
}
else {
    entries = JSON.parse(entries_string);
}
if (num_entries === null) {
    num_entries = 0;
}

var i;
for (i = 0; i < entries.length; i++) {
    $("#chatbox").append(entries[i]);
}

$(function () {
    var user_text_element = document.getElementById("usermsg");
    user_text_element.focus()

    console.log(storage.getItem('entries'));

    //when enter is pressed
    $("#usermsg").on('keydown', function(e) {
        // e.preventDefault();
        if (e.which == 13) {
            console.log('Enter pressed!');
            document.getElementById("submitmsg").click();
            return false;
        }
    });

    var add_text = function (entered_text) {
        var new_entry = '<div class="row"> <div class="col"><b>' + 'user' + ': </b>' + entered_text + '</div> </div>';
        num_entries++;
        storage.setItem('num_entries', num_entries);
        entries.push(new_entry);
        storage.setItem('entries', JSON.stringify(entries));
        $("#chatbox").append(new_entry)
        $("#usermsg").val("")
        //var objDiv = document.getElementById("wrapper");
        // objDiv.scrollTop = objDiv.scrollHeight;
    }

    $("#submitmsg").on('click', function(e) {
        console.log("submitmsg clicked");
        var entered_text = $("#usermsg").val()
        add_text(entered_text)
    })

})

