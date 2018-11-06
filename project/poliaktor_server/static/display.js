/**
 * 
 */
window.onload = function(){
	var video = document.querySelector('#videoElement');
	var canvas = document.querySelector('#canvasElement');
	// var img = document.querySelector('img');
	var context=canvas.getContext('2d');

	namespace = '/test';

	var socket = io.connect(location.protocol + '//' + document.domain + ':' + location.port + namespace);

    var constraints={
			video:true,
			audio:false
	};


	if (navigator.mediaDevices.getUserMedia) {
        navigator.mediaDevices.getUserMedia(constraints)
        .then(function(stream) {
            video.srcObject = stream;
        })
        .catch(function(err0r) {
            console.log("Something went wrong!");
        });
	}

	// video.style.width = video.videoWidth
    // video.style.height = video.videoHeight
	canvas.style.width = 500
    canvas.style.height = 500 / video.videoWidth * video.videoHeight

	// setInterval(drawCanvas,30);

	function drawCanvas(){
		context.drawImage(video, 0, 0, canvas.width, canvas.height);
	}

	function readCanvas(){
		var canvasData = canvas.toDataURL();
		// var decodeAstring = atob(canvasData.split(',')[1]);
        //
		// var charArray =[];
        //
		// for(var i=0; i<decodeAstring.length;i++){
        //
		// 	charArray.push(decodeAstring.charCodeAt(i));
		// }

		// socket.emit('image_sink', {data: new Blob([new Uint8Array(charArray)])})

        socket.emit('image_sink', {data: canvasData})
       // socket.send( new Blob([new Uint8Array(charArray)],{
    	//    tpye:'image/jpeg'
       // }));
       //
       //  socket.addEventListener('message',function(event){
       //  	img.src=window.URL.createObjectURL(event.data);
       //  });

	}

    function main(){
    	drawCanvas();
    	readCanvas();
    }

    setInterval(main ,30);
	
	// console.log(canvas.toDataURL('image/jpeg',1));

    // function readCanvas(){
	// 	var dataURL = canvas.toDataURL();
	// 	$.ajax({
    //           type: "POST",
    //           url: url,
    //           data:{
    //             imageBase64: dataURL
    //           }
    //         }).done(function() {
    //           console.log('sent');
    //         });
    //
	// }
};