$(document).ready(function(){
    /* enter the room */
    $(".enter_room").on("click", function(e){
        var key = $("#key").val();
        var channel = $("#channel").val();
        document.cookie="key=" + key + ";path=/";
        document.cookie="channel=" + channel + ";path=/";
        if(key && channel){
            window.location.href = "interface_Waiting.html";
        }
    });

    function disableVideo(){
        $(".video_choose img").attr("src", "images/ic_login_checkbox.png");
        $(".video_img img").attr("src", "images/ic_login_cell_video_grey.png");
        $("#video").val("false");
    }

    function enableVideo(){
        $("#video").val("true");
        $(".video_choose img").attr("src", "images/ic_login_checkbox_celected.png");
        $(".video_img img").attr("src", "images/ic_login_cell_video.png");
    }

    function disableAudio(){
        $(".audio_choose img").attr("src", "images/ic_login_checkbox.png");
        $(".audio_img img").attr("src", "images/ic_login_cell_voice.png");
        $("#audio").val("false");
    }

    function enableAudio(){
        $("#audio").val("true");
        $(".audio_choose img").attr("src", "images/ic_login_checkbox_celected.png");
        $(".audio_img img").attr("src", "images/ic_login_cell_voice_blue.png");
    }

    $(".video_choose img").on("click", function(e){
        var $e = $(e.target);
        var value = $("#video").val();
        console.log(value);
        disableAudio();
        if(value === "true"){
            disableVideo();
            enableAudio();
        }
        else{
            enableVideo();
        }
    });

    $(".audio_choose img").on("click", function(e){
        var $e = $(e.target);
        var value = $("#audio").val();
        console.log(value);
        disableVideo();
        if(value === "true"){
            disableAudio();
            enableVideo();
        }
        else{
            enableAudio();
        }
    });

    $("#video_profile").select2({
        placeholder: "Select video profile",
        minimumResultsForSearch: Infinity,
        data: [{
            id: '120p_1',
            text: '160 x 120, 15fps, 80kbps'
        }, {
            id: "240p_1",
            text: "320 x 240, 15fps, 200kbps"
        }, {
            id: "480p_1",
            text: "640 x 480, 15fps, 500kbps"
        }, {
            id: '120p_2',
            text: '640 x 480, 30fps, 1Mbps'
        }, {
            id: "720p_1",
            text: "1280 x 720, 15fps, 1Mbps"
        }, {
            id: "720p_2",
            text: "1280 x 720, 30fps, 2Mbps"
        }, {
            id: "1080p_1",
            text: "1920 x 1080, 15fps, 1.5Mbps"
        }, {
            id: "1080p_2",
            text: "1920 x 1080, 30fps, 3Mbps"
        }]
    });

    retrieveInputDevices();


    function retrieveInputDevices() {
        AgoraRTC.getDevices(function(devices) {
            var index, length;
            var videoInputDevices = [],
                audioInputDevices = [];

            for (index = 0, length = devices.length; index < length; index += 1) {
                var d = devices[index];
                if (d['kind'] === 'audioinput') {
                    audioInputDevices.push({id: d['deviceId'], text: d['label']});
                }

                if (d['kind'] === 'videoinput') {
                    videoInputDevices.push({id: d['deviceId'], text: d['label']});
                }
            }

            $("#select_video_device").select2({
                data: videoInputDevices,
                placeholder: "Select video device",
                minimumResultsForSearch: Infinity
            });

            $("#select_audio_device").select2({
                data: audioInputDevices,
                placeholder: "Select audio device",
                minimumResultsForSearch: Infinity
            });
        });
    }
});
