// show mobile share links

if (!navigator.userAgent.match(/iPhone|iPad|Android/i)) {
	$('.share-mobile').css("cssText", "display: none !important;");
}

// Make SMS links compatible cross devices

document.addEventListener('DOMContentLoaded', (function () {
    var link = new SMSLink.link();
    link.replaceAll();
}), false);

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

/* Load call video */
$(document).ready(function() {
	$("#call-video").html('<a href="#" onclick="loadvideo(); return false;"><img src="static/img/video.jpg" width="560" height="315" alt="Anrufvideo"></a>') 
});
var loadvideo = function() {
	$("#call-video").html('<iframe width="560" height="315" src="https://www.youtube.com/embed/-iXMesM0txo?autoplay=1" frameborder="0" allowfullscreen></iframe>')
}


/*
 * Consultation
 */

$(document).ready(function() {

	/* at least one issue must be checked */
	var switchConsBt = function() {
		var l  = $('#consultation-issues input:checked').length;
		var la = $('#consultation-issues input').length;
		if (l === 0) {
			$('#start-consultation').prop('disabled', true);
		} else {
			$('#start-consultation').prop('disabled', false);
		}

		if (l === la) {
			$('#start-consultation').addClass('all-issues-checked');
			$('#issues-check-all').addClass('hide');
		} else {
			$('#start-consultation').removeClass('all-issues-checked');
			$('#issues-check-all').removeClass('hide');
		}


	}
	switchConsBt();

	var highlightActiveIssues = function() {
		$("#consultation-issues :checkbox").is( function(){
			if ($(this).is(':checked')) {
				$(this).parent().addClass("issue-checked");
			} else {
				$(this).parent().removeClass("issue-checked");
			}
		});
	}
	highlightActiveIssues();

	$('#consultation-issues input').change( function () {
		switchConsBt();
		highlightActiveIssues();
	});


	/* check all issues */
	$('#issues-check-all').click( function(){
		$('.issue-cb').prop('checked', true);
		switchConsBt();
		highlightActiveIssues();
	});

	/* resize textarea to its content*/
	$('.floating-textarea').each(function () {
		this.setAttribute('style', 'height:' + (this.scrollHeight) + 'px;overflow-y:hidden;');
	}).on('input', function () {
		this.style.height = 'auto';
		this.style.height = (this.scrollHeight) + 'px';
	});

	/* update signature */
	var typeSignature = function() {
		var signature = "";
		$('.typeaware').each(function() {
			signature += " " + $(this).val();
		});
		$('.consultation-signature').each( function() {
			$(this).html(signature);
		});
	}
	typeSignature();
	$('.typeaware').each(function() {
		$(this).on('input', typeSignature);
	});


});

