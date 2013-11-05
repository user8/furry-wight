// VK Audio Downloader Chrome Extension
// Downloads mp3s from vk.com
// Send any suggestions and comments to /dev/null

$('<style type="text/css"> .vkaudio {display:none; position:absolute; top:23px; left:34px; font-size:8px; color:#b4c3d3;} \
			   .vkaudio:hover {color:#5f809f; text-decoration:none;} \
			   #audio .current .vkaudio:hover, #pad_playlist .current .vkaudio:hover {color:white;} \
			   #audio .wall_module .current .vkaudio:hover {color:#5f809f;} \
			   .over .vkaudio {display:block;} \
			   .audio .title_wrap {padding:10px 0px 9px !important; } \
			   .audio .play_btn_wrap {padding:9px !important;} \
			   .audio .duration {padding:10px 9px 9px !important;} \
			   .audio .area {margin:0px !important;} \
			   div#adsframe, div#left_ads {display:none !important;} </style>').appendTo("head");

var vkAudio = function () {
    var audios = $(".audio:not(#audio_global)");

    if (audios.length) {
	for(var i = 0; i < audios.length; i++) {

	    var el = $(audios[i]);

	    if (!el[0].vkaudio) {
		var link = '<a href="' + el.find("input")[0].value.split("?")[0] + '" \
			       download="' + $.trim($(el.find("a[href]")[0]).text()) + ' - ' + $.trim($(el.find(".title")[0]).text()) + '.mp3" \
			       class="vkaudio" \
			       title="&quot;Give it to me!&quot;">mp3</a>';

		$(el).append(link);
		el[0].vkaudio = true;
	    }
	}

    }

    var to = window.setTimeout(vkAudio, 1500);
};

vkAudio();
