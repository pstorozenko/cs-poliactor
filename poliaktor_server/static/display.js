window.browser = (function () {
  return window.msBrowser ||
    window.browser ||
    window.chrome;
})();

window.onload = function(){
	var video = document.getElementById("videoElement");
	var actor = document.getElementById("actor-img");
    var plot = document.getElementById("plot-img");
    var canvas=document.getElementById("canvasElement");
    var ctx=canvas.getContext("2d");
    var button = document.getElementById("dev_button");
    var input = document.getElementById("dev_input");
    var actor_name = document.getElementById("actor-name");

    var average = false;
    var frames = 1;
    var bbox = null;

	var namespace = '/test';
	var socket = io.connect(location.protocol + '//' + document.domain + ':' + location.port + namespace);
    var constraints={
			video:
                {
                    width: 640,
                    height: 480
                },
			audio:false
	};

    input.onchange = function () {
        if(input.value < 1)
            input.value = 1;
        frames = input.value;
    }

	if (navigator.mediaDevices.getUserMedia) {
        navigator.mediaDevices.getUserMedia(constraints)
        .then(function(stream) {
            video.srcObject = stream;
            video.play();
            setTimeout(function () {
                let dw = 1 * video.videoWidth;
                let dh = 1 * video.videoHeight;
                canvas.setAttribute('width', dw);
                canvas.setAttribute('height', dh);
                actor.setAttribute('width', dw);
                actor.setAttribute('height', dw);
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
	        ctx.strokeStyle = "#FF0000";
	        ctx.strokeRect(bbox.x, bbox.y, bbox.wdth, bbox.hght);
        }
	}

	function readCanvas(){
		let canvasData = canvas.toDataURL();
        socket.emit('image_sink', {
            data: canvasData,
            frames: frames
        })
	}

	button.onclick = function () {
        socket.emit('reset_plot', {
            reset: true
        })
    };

	socket.on('my_response', function(msg) {
	    actor_name.innerHTML = msg.actor;
	    actor.src = "data:image/png;base64," + msg.image;
	    plot.src = "data:image/png;base64," + msg.plot;

	    bbox = msg.coord;
	    readCanvas();
	});
};