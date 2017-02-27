function pad(num) {
	if (isNaN(num)) {
		throw "Incorrect input";
	}
	if (num < 10) {
		num = "0" + num;
	}
	return num;
}

function toHHMMSS(seconds) {
	try {
		var hh = Math.floor(seconds / 3600);
		var mm = Math.floor((seconds - (hh * 3600)) / 60);
		var ss = Math.floor(seconds - (hh * 3600) - (mm * 60));
    	return pad(hh) + ':' + pad(mm) + ':' + pad(ss);
	} catch(err) {
		return err;
	}
}


function fromHHMMSS(line) {
	var values = line.split(":");
	if (values.length != 3) {
		return "Incorrect input";
	}
	var str2int = function(str) {
		if (str.length != 2)
			throw "Incorrect input";
		var v = parseInt(str, 10);
		if (isNaN(v))
			throw "Incorrect input";
		return v;
	}
	try {
		return 3600*str2int(values[0]) +
			   60*str2int(values[1]) +
			   str2int(values[2]);
	} catch(err) {
		return err;
	}
}


function bin2jsonstr(binStr) {
  return decodeURIComponent(atob(binStr));
}


function jsonstr2bin(jsonStr) {
  return btoa(encodeURIComponent(jsonStr));
}


function ms2sec(ms) {
	return ms / 1000;
}


function sec2ms(sec) {
	return sec * 1000;
}

function valueFromObject(obj, key) {
	var objects = [];
	for (var i in obj) {
		if (!obj.hasOwnProperty(i))
			continue;
		if (i == key)
			return obj[key];
		if (typeof obj[i] == "object") {
			var v = valueFromObject(obj[i], key);
			if (v == null)
				continue;
			else
				return v
		}
	}
	return null;
}
