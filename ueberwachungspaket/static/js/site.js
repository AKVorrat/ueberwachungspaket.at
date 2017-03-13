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

// search filter

$(document).ready(function() {
	if($("#representatives").length) {
		$("#importance :radio").change(search);

		$("#parties :checkbox").change(search);

		$("#teams :checkbox").change(search);

		$("#states :checkbox").change(search);

		$("#name input").on('keyup change', search);
	}
});

function search(event) {
	$("#representatives").children(".representative").each(function() {
		var name = ($(this).data("firstname") + " " + $(this).data("lastname") + " " + $(this).data("firstname")).toLowerCase();
		if((!$("#reps-important").prop("checked") || $(this).data("important") === "True")
		&& ($("#" + $(this).data("party")).prop("checked") || $("#parties").children(":checked").length == 0)
		&& ($("#" + $(this).data("team")).prop("checked") || $("#teams").children(":checked").length == 0)
		&& ($("#state-" + $(this).data("state")).prop("checked") || $("#states").children(":checked").length == 0)
		&& ($("#name input").val() === '' || name.indexOf($("#name input").val().trim().toLowerCase()) > -1)) {
			$(this).removeClass("invisible");
		} else {
			$(this).addClass("invisible");
		}
	});
}

// mail text filter

$(document).ready(function() {
	if($("#mail").length) {
		mailReps = $("#mail .textarea").text();
		updateText();
		$("#mail-firstname").keyup(updateText);
		$("#mail-lastname").keyup(updateText);
	}
})

function updateText(event) {
	var lines = mailReps.split("\n");
	var MailNameFrom = $("#mail-firstname").val() + " " + $("#mail-lastname").val();
	if(!$.trim(MailNameFrom).length) {
		MailNameFrom = "Dein Name";
	}
	$("#mail .textarea").empty();
	$.each(lines, function() {
		if(this.length) {
			str = this.replace("{salutation}", MailSalutation).replace("{name_rep}", MailNameTo).replace("{name_user}", MailNameFrom);
			$("#mail .textarea").append("<p>" + str + "</p>");
		}
	});
}

// Progressbar

$(document).ready(function() {
	var startDate = '01/30/2017';
	var endDate = '06/30/2017';

	if (startDate != "" && endDate != "") {
		var minDate = new Date(convertStringToDate(startDate));
		var today = new Date();
		var maxDate = new Date(convertStringToDate(endDate));

		var nbTotalDays = Math.floor((maxDate.getTime() - minDate.getTime()) / 86400000);
		var nbPastDays = Math.floor((today.getTime() - minDate.getTime()) / 86400000);

		var percent = nbPastDays / nbTotalDays * 100;

		// Extreme cases
		if (percent < 0) {
			percent = 0;
		} else if (percent > 100) {
			percent = 100;
		}

		$(".progressbar").reportprogress(percent);
	}
});

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

