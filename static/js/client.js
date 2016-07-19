(function($) {
    $(document).ready(function(){
        var args            = window.location.href.split("?"),
            key             = '64e58e32af23464eb35e09821f6b0098',
            channel         = "",
            videoChecked    = true,
            audioChecked    = true,
            username        = 'admin',
            members         = 0,
            videoDpi        = '720p_1',
            videoDevice     = '56ce055cb0efcbe2cf8137c7e914d06e49b52a44dc0e0b911f5f045a84b2e56b',
            audioDevice     = 'default',
            uid             = 1,
            disableAudio    = false,
            disableVideo    = false,
            viewSwitch      = false,
            remoteStremList = {},
            client, localStream;

        /************************* Initialize begins **************************/
        (function decodeArgumentsFromURL() {
            if(args.length > 1){
                args = args[1].split("&");
                var data = {};
                for(var i = 0; i < args.length; i ++){
                    var temp = args[i].split("=");
                    data[temp[0]] = temp[1];
                }
                channel = decodeURI(data["channel"]);
                $("#channelSpan").html(channel);
                $(".menu_content .color").first().html(username);
            }
        }());

        /* initialzed, join channel */
        (function initAgoraRTC(){
            //document.getElementById("video").disabled = true;
            console.log('Joining channel ' + key + ' : ' + channel);
            client = AgoraRTC.createClient();

            // reference for dynamic key, comment out
            /*var dynamic_key;
            console.log("Try to get dynamic key");
            var use_https = ('https:' == document.location.protocol ? true : false);
            if (use_https) {
              var url_str = "https://ip:port/dynamic_key?channelName=" + channel.value;
            } else {
              var url_str = "http://ip:port/dynamic_key?channelName=" + channel.value;
            }
            $.ajax({
              url: url_str,
              error: function() {
                console.log("Failed to get dynamic key");
              },
              success: function(response) {
                console.log(response.key);
                dynamic_key = response.key;
              }
            });*/


            client.init(key,function () {
                console.log("AgoraRTC client initialized");
                var token = undefined;
                client.join(channel, undefined, function(uid){
                    console.log("User " + uid + " join channel successfully");
                    localStream = initLocalStream(1);
                },
                function(err) {
                    console.log("Join channel failed", err);
                });
            }, function(err){
                console.log("AgoraRTC client init failed", err);
                alert(err);
                window.location.href = ".";
            });
        }());

        subscribeSdkEvents();
        subscribeDomEvents();

        (function updateChannelList() {
            /* get history channel */
            var channelList = localStorage.getItem("channelList");
            channelList = channelList? channelList.split(","): [];
            if(channelList.indexOf(channel) == -1){
                channelList.push(channel);
            }
            channelList.forEach(function(e, index){
                var $li = '<li data-channel="' + e + '"><img src="images/voice_index_three.png" /><label>' + e;
                if(e === channel){
                    $li += '<span class="color">(In Conferencing)</span>';
                }
                $li += '</label></li>'
                $(".menu_content ul").append($li);
            });
            localStorage.setItem("channelList", channelList.join(","))
        }());
        /* Initialize end */

        /********************* Utility functions begins *************************/
        function subscribeSdkEvents() {
            client.on('stream-added', function (evt) {
                var stream = evt.stream;
                console.log("New stream added: " + stream.getId());
                console.log("Subscribe ", stream);
                client.subscribe(stream, function (err) {
                    console.log("Subscribe stream failed", err);
                });
            });

            client.on('peer-leave', function(evt){
                var stream = evt.stream;
                var $p = $('<p id="infoStream' + evt.uid + '">' + evt.uid + ' quit from room</p>');
                $(".info").append($p);
                setTimeout(function(){$p.remove();}, 10*1000);
                delete remoteStremList[evt.uid];
                stream.stop();
                console.log($("#agora_remote" + evt.uid).length);
                if($("#agora_remote" + evt.uid).length > 0){
                    $("#agora_remote" + evt.uid).parent().remove();
                }
            });

            client.on('stream-removed', function(evt){
                var stream = evt.stream;
                var $p = $('<p id="infoStream' + stream.getId() + '">' + stream.getId() + ' quit from room</p>');
                $(".info").append($p);
                setTimeout(function(){$p.remove();}, 10*1000);
                delete remoteStremList[stream.getId()];
                stream.stop();
                if($("#agora_remote" + stream.getId()).length > 0){
                    $("#agora_remote" + stream.getId()).parent().remove();
                }
            });

            client.on('stream-subscribed', function (evt) {
                var stream = evt.stream;
                console.log("Catch stream-subscribed event");
                console.log("Subscribe remote stream successfully: " + stream.getId());
                console.log(evt);
                displayInfo(stream);
                remoteStremList[stream.getId()] = stream;
                members = 0;
                for(var key in remoteStremList){
                    members += 1 ;
                }
                $(".content").hide();
                members == 1? timedCount(): null;
                var $container = viewSwitch? $(".left ul"):$(".right ul");
                if(!videoChecked){
                    $(".screen").removeClass("wait").addClass("audio");
                    $container.append('<li class="remoteAudio"><div id="agora_remote' + stream.getId() + '"></div><p>'+ stream.getId() + '</p></li>')
                    stream.play('agora_remote'+stream.getId());
                    $("#agora_remote" + stream.getId() + " div").hide();
                    return;
                }
                if(members == 1){
                    $(".screen").removeClass("wait").addClass("video single");
                }
                else{
                    $(".screen").removeClass("wait single").addClass("video");
                    viewSwitch? null:$(".screen").addClass("multi");
                }
                if(stream.video){
                    $container.append('<li class="remoteVideo"><div id="agora_remote'+stream.getId()+ '"></div></li>');
                }
                else{
                    $container.append('<li class="remoteAudio"><div class="audioImg" id="agora_remote'+stream.getId()+ '"></div><p>'+ stream.getId() + '</p></li>');
                    $("#agora_remote" + stream.getId() + " div").hide();
                }
                stream.play('agora_remote'+stream.getId());
            });
        }

        function initLocalStream(id, callback){
            uid = 1;
            if(localStream){
                console.log("localStream exists");
                client.unpublish(localStream, function(err){
                    console.log("unpublish localStream fail.", err);
                });
                localStream.close();
            }

            localStream = AgoraRTC.createStream({
                streamID     : uid,
                audio        : true,
                video        : videoChecked,
                screen       : false,
                cameraId     : videoDevice,
                microphoneId : audioDevice
            });
            if(videoChecked){
                localStream.setVideoProfile(videoDpi);
            }

            localStream.init(function() {
                console.log("getUserMedia successfully");
                console.log(localStream);
                if(!videoChecked){
                    $(".screen .left div").addClass("waitAudio");
                    $("#local div").hide();
                    localStream.play('local');
                }
                else{
                    if(viewSwitch){
                        $(".right ul").html('');
                        $(".right ul").append('<li class="remoteVideo"><div id="agora_remote'+localStream.getId()+ '"></div></li>');
                        localStream.play('agora_remote'+ localStream.getId());
                    }
                    else{
                        $(".left").html('<div class="" id="local"></div>');
                        localStream.play("local");
                    }
                }

                client.publish(localStream, function (err) {
                    console.log("Publish local stream error: " + err);
                });
                //client.on('stream-published', function (evt) {
                //console.log("Publish local stream successfully");
                //});
            },
            function (err){
                console.log("getUserMedia failed", err);
            });
            return localStream;
        }

        function displayInfo(stream) {
            var $p = $('<p id="infoStream' + stream.getId() + '">' + stream.getId() + ' joined the room</p>');
            $(".info").append($p);
            setTimeout(function(){$p.remove();}, 10*1000);
        }

        function timedCount() {
            var c = 0;
            var t;
            setInterval(function(){
                hour = parseInt(c / 3600);// hours
                min = parseInt(c / 60);// minutes
                if(min>=60){
                    min=min%60
                }
                lastsecs = c % 60;
                $(".telephone").html( hour + ":" + min + ":" + lastsecs )
                c=c+1;
            },1000);
        }

        function subscribeDomEvents() {
            $(".leave").on('click', function(){
                client.leave();
                window.location.href = "/admin/chat";
            });

            /* click the right video and switch view */
            $(".right  ul").delegate('.remoteVideo', 'click', function(e){
                if(viewSwitch){
                    return false;
                }
                var id = $(this).find('div').attr("id").substring(12);
                var stream = remoteStremList[id] || localStream;
                console.log($(this), id, stream);
                if(stream){
                    var leftStream = remoteStremList[$("#local").data("id")] || localStream;
                    $(this).html('<div id="agora_remote'+leftStream.getId()+ '"></div>');
                    $("#local").html('');
                    stream.play("local");
                    $("#local").data("id", stream.getId());
                    leftStream.play('agora_remote'+ leftStream.getId());
                }
            });

            /* zoom in/out after view swtich */
            $(".left").delegate('ul .remoteVideo', 'click', function(e){
                if(!viewSwitch){
                    return false;
                }
                var id = $(this).find('div').attr("id").substring(12);
                var container = $(this);
                var stream = remoteStremList[id];
                console.log($(this), id, stream);
                if(stream){
                    //stream.play("local");
                    //localStream.play('agora_remote'+ localStream.getId());
                    $(this).html('');
                    $(".big_images .bigVideo").attr('id', "agora_remote" + stream.getId())
                    $(".big_images").show();
                    stream.play("agora_remote" + stream.getId());
                    $(".big_images .cancel").on('click', function(e){
                        console.log('cancel');
                        $(container).html('<div id="agora_remote'+ stream.getId()+ '"></div>');
                        $(".big_images .bigVideo").attr("id", '').html("");
                        stream.play("agora_remote" + stream.getId());
                        $(this).unbind('click');
                        $(".big_images").hide();
                    });
                }
            });

            /* mute/unmute audio */
            $(".audioSwitch").on("click", function(e){
                disableAudio = !disableAudio;
                if(disableAudio){
                    localStream.disableAudio();
                    $(".audioSwitch div").removeClass("on").addClass("off");
                    $(".audioSwitch p").html("Enabled audio");
                }
                else{
                    localStream.enableAudio();
                    $(".audioSwitch div").removeClass("off").addClass("on");
                    $(".audioSwitch p").html("Mute");
                }
            });

            /* Camera on/off */
            $(".videoSwitch").on("click", function(e){
                disableVideo = !disableVideo;
                if(disableVideo){
                    localStream.disableVideo();
                    $(".videoSwitch div").removeClass("on").addClass("off");
                    $(".videoSwitch p").html("Unmute camera");
                }
                else{
                    localStream.enableVideo();
                    $(".videoSwitch div").removeClass("off").addClass("on");
                    $(".videoSwitch p").html("Camera Off");
                }
            });

            /* Switch View */
            $(".viewSwitch").on('click', function(e){
                viewSwitch = !viewSwitch;
                var $container = null;
                $(".big_images .cancel").trigger("click");
                if(viewSwitch){
                    $(".viewSwitch div").removeClass("on").addClass("off");
                    $(".screen").attr("class", "screen video switch");
                    $(".screen .left").html('<ul></ul>');
                    $container = $(".left ul");
                    $(".right ul").html("");
                    console.log('localStream', localStream);
                    if(localStream.video){
                        $(".right ul").append('<li class="remoteVideo"><div id="agora_remote'+ localStream.getId()+ '"></div></li>');
                    }
                    else{
                        $(".right ul").append('<li class="remoteAudio"><div class="audioImg" id="agora_remote'+ localStream.getId()+ '"></div><p>'+ stream.getId() + '</p></li>');
                    }
                    localStream.play('agora_remote'+ localStream.getId());
                }
                else{
                    $(".viewSwitch div").removeClass("off").addClass("on");
                    $(".screen").removeClass("switch");
                    $(".screen").addClass(members > 1? "multi": "single");
                    $container = $(".right ul");
                    $(".left").html('<div class="" id="local"></div>');
                    localStream.play("local");
                }
                $container.html("");
                for(var key in remoteStremList){
                    var stream = remoteStremList[key];
                    if(stream.video){
                        $container.append('<li class="remoteVideo"><div id="agora_remote'+stream.getId()+ '"></div></li>');
                    }
                    else{
                        $container.append('<li class="remoteAudio"><div class="audioImg" id="agora_remote'+stream.getId()+ '"></div><p>'+ stream.getId() + '</p></li>');
                    }
                    stream.play('agora_remote'+stream.getId());
                }
            });
        }
        /* Utility functions end */
    });
}(jQuery));
