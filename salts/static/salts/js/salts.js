function toHHMMSS(seconds) {
	var pad = function(num) {
		if (num < 10) {
			num = "0" + num;
		}
		return num;
	}
    var hh = Math.floor(seconds / 3600);
    var mm = Math.floor((seconds - (hh * 3600)) / 60);
    var ss = Math.floor(seconds - (hh * 3600) - (mm * 60));
    return pad(hh) + ':' + pad(mm) + ':' + pad(ss);
}
