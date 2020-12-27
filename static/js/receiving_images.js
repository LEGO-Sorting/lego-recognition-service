function arrayBufferToString(buffer){
    var arr = new Uint8Array(buffer);
    var str = String.fromCharCode.apply(String, arr);
    if(/[\u0080-\uffff]/.test(str)){
        throw new Error("this string seems to contain (still encoded) multibytes");
    }
    return str;
}

$(document).ready(function(){
    //connect to the socket server.
    var socket = io.connect('http://' + document.domain + ':' + location.port + '/test');
    var pictures_received = [];

    //receive details from server
    socket.on('new_picture', function(msg) {
        //maintain a list of ten numbers
        // if (pictures_received.length >= 10){
        //     pictures_received.shift()
        // }
        pictures_received.unshift({
            category: msg.category,
            image: arrayBufferToString(msg.image),
            content_type: msg.content_type
        });

        // console.log(pictures_received);

        pictures_string = '';

        for (var i = 0; i < pictures_received.length; i++){
            pictures_string = pictures_string +
                '<div class="prediction_container">' +
                    '<div class="prediction_column"><img src="data:'+pictures_received[i].content_type+';base64, '+ pictures_received[i].image +'"></img></div>' +
                    '<div class="prediction_column"><p>'+pictures_received[i].category+'</p></div>' +
                '</div>'
        }
        $('#log').html(pictures_string);
    });

});