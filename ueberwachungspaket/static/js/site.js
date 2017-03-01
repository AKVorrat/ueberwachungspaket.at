// smooth scroll

$(document).ready(function () {
	$("a[href*='#']:not([href='#'])").click(function() {
		if (location.pathname.replace(/^\//,'') == this.pathname.replace(/^\//,'')  || location.hostname == this.hostname) {
			var target = $(this.hash);
			target = target.length ? target : $('[name=' + this.hash.slice(1) +']');
			if (target.length) {
				$('html,body').animate({
					scrollTop: target.offset().top
				}, 800);
				return false;
			}
		}
	});
});

// activate search filter

$(document).ready(function() {
	if($("#representatives").length) {
		$("#parties :checkbox").change(search);

		$("#teams :checkbox").change(search);

		$("#states :checkbox").change(search);
	}
});

function search(event) {
	$("#representatives").children(".representative").each(function() {
		if(($("#" + $(this).data("party")).prop("checked") || $("#parties").children(":checked").length == 0)
		&& ($("#" + $(this).data("team")).prop("checked") || $("#teams").children(":checked").length == 0)
		&& ($("#state-" + $(this).data("state")).prop("checked") || $("#states").children(":checked").length == 0)) {
			$(this).removeClass("invisible");
		} else {
			$(this).addClass("invisible");
		}
	});
}

//Progressbar

(function($) {
	//Main Method
	$.fn.reportprogress = function(val,maxVal) {
		var max=100;
		if(maxVal)
			max=maxVal;
		return this.each(
			function(){
				var div=$(this);
				var innerdiv=div.find(".progress");

				if(innerdiv.length!=1){
					innerdiv=$("<div class='progress'></div>");
					div.append("<div class='text'>&nbsp;</div>");
					$("<span class='text'>&nbsp;</span>").css("width",div.width()).css("height",div.height()).appendTo(innerdiv);
					div.append(innerdiv);
				}
				var width=Math.round(val/max*100);
				innerdiv.css("width",width+"%");
				div.find(".text").html(width+" %");
			}
		);
	};
})(jQuery);
/*
 * Convert a string into a date.
 */
function convertStringToDate(stringdate)
{
	// Internet Explorer does not like dashes in dates when converting,
	// so lets use a regular expression to get the year, month, and day
	var DateRegex = /([^-]*)\/([^-]*)\/([^-]*)/;
	var DateRegexResult = stringdate.match(DateRegex);
	var DateResult;
	var StringDateResult = "";

	// try creating a new date in a format that both Firefox and Internet Explorer understand
	try
	{
		DateResult = new Date(DateRegexResult[1]+"/"+DateRegexResult[2]+"/"+DateRegexResult[3]);
	}
		// if there is an error, catch it and try to set the date result using a simple conversion
	catch(err)
	{
		DateResult = new Date(stringdate);
	}

	// Date formating
	StringDateResult = (DateResult.getMonth()+1)+"/"+(DateResult.getDate())+"/"+(DateResult.getFullYear());

	return StringDateResult;
}

/*
 * Convert a date into a string.
 */
function convertDateToString(date)
{
	// Add "0" ahead the month & day if needed
	var month = date.getMonth()+1;
	var day = date.getDate();

	if (month < 10) {
		month = "0"+month;
	}
	if (day < 10) {
		day = "0"+day;
	}
	// Date formating
	StringDateResult = month+"/"+day+"/"+(date.getFullYear());

	return StringDateResult;
}

