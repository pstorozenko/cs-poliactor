window.browser = (function () {
  return window.msBrowser ||
    window.browser ||
    window.chrome;
})();

window.onload = function(){
	var video = document.querySelector('#videoElement');
	var img = document.querySelector('img');
    var canvas=document.getElementById("canvasElement");
    var ctx=canvas.getContext("2d");

	var bbox = null;

	namespace = '/test';

	var socket = io.connect(location.protocol + '//' + document.domain + ':' + location.port + namespace);

    var constraints={
			video:
                {
                    width: 640,
                    height: 480
                },
			audio:false
	};

	if (navigator.mediaDevices.getUserMedia) {
        navigator.mediaDevices.getUserMedia(constraints)
        .then(function(stream) {
            video.srcObject = stream;
            video.play();
            setTimeout(function () {
                let dw = video.videoWidth + 'px';
                let dh = video.videoHeight + 'px';
                canvas.setAttribute('width', dw);
                canvas.setAttribute('height', dh);
                img.setAttribute('width', dw);
                img.setAttribute('height', dh);
                setInterval(drawCanvas, 100);
                readCanvas();
            }, 1000);
        })
        .catch(function(err0r) {
            console.log("Something went wrong!");
        });
	}

	function drawCanvas(){
        ctx.drawImage(video, 0, 0, canvas.width, canvas.height);
	    if (bbox) {
	        ctx.strokeRect(bbox.x, bbox.y, bbox.wdth, bbox.hght);
        }
	}
	function readCanvas(){
		let canvasData = canvas.toDataURL();
        socket.emit('image_sink', {data: canvasData})
	}

	socket.on('my_response', function(msg) {
                img.src = "data:image/png;base64," + msg.data;
                bbox = msg.coord;
                readCanvas();
            });
};