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


// slick carousel

$(document).ready(function() {
	if ($("#quotes-carousel").length > 0) {
		var carousel = $("#quotes-carousel").slick({
			dots: true,
			infinite: true,
			slidesToShow: 1,
			slidesToScroll: 1,
			adaptiveHeight: true,
			autoplay: true,
			autoplaySpeed: 5000,
			responsive: [
				{
					breakpoint: 992,
					settings: {
						dots: false
					}
				}
			]
		});

		$(window).scroll(function() {
			var top_of_element = $("#quotes-carousel").offset().top;
			var bottom_of_element = $("#quotes-carousel").offset().top + $("#quotes-carousel").outerHeight();
			var top_of_screen = $(window).scrollTop();
			var bottom_of_screen = $(window).scrollTop() + $(window).height();

			if((bottom_of_screen > top_of_element) && (top_of_screen < bottom_of_element)){
				carousel.slick("slickPlay");
			} else {
				carousel.slick("slickPause");
			}
		});
	}

	if ($("#videos-carousel").length > 0) {
		var videocarousel = $("#videos-carousel").slick({
			dots: true,
			infinite: true,
			slidesToShow: 1,
			slidesToScroll: 1,
			adaptiveHeight: true,
			responsive: [
				{
					breakpoint: 992,
					settings: {
						dots: false
					}
				}
			]
		});

		videocarousel.on("beforeChange", function(event, slick, currentSlide, nextSlide) {
			var iframe = $("#videos-carousel .slick-current iframe");
			if (iframe.length > 0) {
				var iframeWindow = iframe.get(0).contentWindow;
				iframeWindow.postMessage('{"event":"command","func":"pauseVideo","args":""}', '*');
			}
		});
	}
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

// register video embeds

$(document).ready(function() {
	$("body").on("click", ".video-embed", function (e) {
		var vid = $(this).data("vid");
		$(this).replaceWith('<iframe width="480" height="360" src="https://www.youtube.com/embed/' + vid + '?autoplay=1&enablejsapi=1" frameborder="0" allowfullscreen="allowfullscreen"></iframe>');
	});
});

// bar chart

var indicatorPlugin = {
	beforeInit: function(chartInstance) {
		var layout = chartInstance.options.layout;
		if (!layout) {
			layout = {
				"padding": {
					"bottom": 20
				}
			}
			chartInstance.options.layout = layout;
		}
	},
	afterDraw: function(chartInstance) {
		var xScale = chartInstance.scales["x-axis-0"];
		var canvas = chartInstance.chart;
		var ctx = canvas.ctx;

		if (chartInstance.options.indicatorLine) {
			var line = chartInstance.options.indicatorLine;
			var style = line.color ? line.color : "#000000";
			var xValue = line.x ? xScale.getPixelForValue(line.x) : 0;

			ctx.lineWidth = 2;
			ctx.beginPath();

			ctx.moveTo(xValue, 0);
			ctx.lineTo(xValue, canvas.height - 25);
			ctx.strokeStyle = style;
			ctx.stroke();

			ctx.fillStyle = style;
			ctx.textAlign = "center";
			ctx.textBaseline = "bottom";
			ctx.fillText(line.text, xValue, canvas.height);

			ctx.closePath();
		}
	}
}
Chart.pluginService.register(indicatorPlugin)

$(document).ready(function () {
	var ctx = $("#barChart")

	if (ctx.length > 0) {
		$.getJSON("/konsultation/stats", function (data) {
			var data = {
				labels: [
					"Bundestrojaner",
					"Netzsperren",
					"Vorratsdatenspeicherung für Videoüberwachung",
					"Vollüberwachung auf Österreichs Straßen",
					"Quickfreeze",
					"Anonyme Simkarten",
					"IMSI-Catcher",
					"Lauschangriff im Auto"
				],
				datasets: [
					{
						data: [
							data.stats.addressesBundestrojaner,
							data.stats.addressesNetzsperren,
							data.stats.addressesVdsVideo,
							data.stats.addressesUeberwachungStrassen,
							data.stats.addressesVdsQuickfreeze,
							data.stats.addressesAnonymeSimkarten,
							data.stats.addressesImsiCatcher,
							data.stats.addressesLauschangriffAuto
						]
					}
				]
			};

			var options = {
				"legend": {
					"display": false
				},
				"elements": {
					"rectangle": {
						"backgroundColor": "#00466e"
					}
				},
				"scales": {
					"xAxes": [{
						"ticks": {
							"beginAtZero": true
						}
					}]
				},
				"indicatorLine": {
					"x": "1659",
					"text": "bisheriges Maximum an Stellungnahmen in einer Begutachtung in Österreich",
					"color": "#c80000"
				}
			}

			var barChart = new Chart(ctx, {
				type: "horizontalBar",
				data: data,
				options: options
			});
		});
	}
});

// consultation table

var loading = false;
var tableSettings = {
	"pageIndex": 1,
	"sortKey": "originality",
	"filterOrigin": "both",
	"filterName": "",
	"filterTopic": "all"
}

function buildNextPage(data) {
	opinions = data.opinions
	opinionsCount = data.count

	$("#opinionsCount").text(opinionsCount);

	$.each(opinions, function(i, item) {
		row = $("<tr />");
		row.append($("<td />", {text: item.name}));
		row.append($("<td />", {class: "center", text: item.date}));
		if (item.linkBmi) {
			row.append($("<td />", {class: "center", html: "<a href='" + item.linkBmi + "'<i class='fa fa-file-pdf-o' aria-hidden='true'></i></a>"}));
		} else {
			row.append($("<td />"));
		}
		if (item.linkBmj) {
			row.append($("<td />", {class: "center", html: "<a href='" + item.linkBmj + "'<i class='fa fa-file-pdf-o' aria-hidden='true'></i></a>"}));
		} else {
			row.append($("<td />"));
		}
		var indicators = "";
		indicators += "<img class='indicator' src='/static/img/icons/" + (item.addressesBundestrojaner ? "green" : "gray") + "/trojaner.png' title='Bundestrojaner' />&nbsp;";
		indicators += "<img class='indicator' src='/static/img/icons/" + (item.addressesNetzsperren ? "green" : "gray") + "/netzsperren.png' title='Netzsperren' />&nbsp;";
		indicators += "<img class='indicator' src='/static/img/icons/" + (item.addressesVdsVideo ? "green" : "gray") + "/totalevideoueberwachung.png' title='Vorratsdatenspeicherung für Videoüberwachung' />&nbsp;";
		indicators += "<img class='indicator' src='/static/img/icons/" + (item.addressesUeberwachungStrassen ? "green" : "gray") + "/verkehrsueberwachung.png' title='Vollüberwachung auf Österreichs Straßen' />&nbsp;";
		indicators += "<img class='indicator' src='/static/img/icons/" + (item.addressesVdsQuickfreeze ? "green" : "gray") + "/vorratsdaten.png' title='Quickfreeze' />&nbsp;";
		indicators += "<img class='indicator' src='/static/img/icons/" + (item.addressesAnonymeSimkarten ? "green" : "gray") + "/sim-id.png' title='Anonyme Simkarten' />&nbsp;";
		indicators += "<img class='indicator' src='/static/img/icons/" + (item.addressesImsiCatcher ? "green" : "gray") + "/imsicatcher.png' title='IMSI-Catcher' />&nbsp;";
		indicators += "<img class='indicator' src='/static/img/icons/" + (item.addressesLauschangriffAuto ? "green" : "gray") + "/lauschangriffauto.png' title='Lauschangriff im Auto' />";
		row.append($("<td />", {class: "center", html: indicators}));
		row.append($("<td />", {class: "center", html: item.originality + (item.comment ? "<i class='fa fa-chevron-circle-down commentOpener' data-comment='" + item.id + "' aria-hidden='true'></i>" : "")}));
		$("#consultationTable > tbody").append(row);

		if (item.comment) {
			row = "<tr class='comment' id='comment" + item.id + "'><td colspan='6'>" + item.comment + "</td></tr>"
			$("#consultationTable > tbody").append(row);
		}
	})

	if(opinions.length > 0) {
		loading = false;
	}

}

function clearTable() {
	$("#consultationTable > tbody").empty();
}

function loadNextPage() {
	loading = true;
	$.getJSON("/konsultation/load?" + $.param(tableSettings), buildNextPage);
	tableSettings.pageIndex++;
}

function refreshTable() {
	tableSettings.pageIndex = 0;
	clearTable();
	loadNextPage();
}

function setSortKey(sortKey) {
	if (tableSettings.sortKey == sortKey)
		tableSettings.sortKey = "-" + sortKey;
	else
		tableSettings.sortKey = sortKey;
	refreshTable();
}

$(document).ready(function() {
	$(window).scroll(function() {
		var bottomOfScreen = $(window).scrollTop() + $(window).height();
		var pageHeight = document.body.offsetHeight;

		if((pageHeight - bottomOfScreen < 100) && !loading){
			loadNextPage();
		}
	});

	$("input[name='filterOrigin']").change(function () {
		tableSettings.filterOrigin = $("input[name='filterOrigin']:checked").val();
		refreshTable();
	});

	$("#filterNameButton").click(function () {
		tableSettings.filterName = $("input[name='filterName']").val().trim();
		refreshTable();
	});

	$("input[name='filterName']").on("keyup", function (e) {
		if (e.keyCode == 13) {
			tableSettings.filterName = $("input[name='filterName']").val().trim();
			refreshTable();
		}
	});

	$("select[name='filterTopic']").change(function () {
		tableSettings.filterTopic = $("select[name='filterTopic']").val();
		refreshTable();
	});

	$("th.sortable").click(function () {
		var sortKey = $(this).data("sortKey");
		setSortKey(sortKey);
	});

	$("body").on("click", ".commentOpener", function () {
		var commentId = $(this).data("comment");
		var comment = $("#comment" + commentId);
		comment.toggle();

		if (comment.css("display") == "none") {
			// comment is now hidden
			$(this).removeClass("fa-chevron-circle-up").addClass("fa-chevron-circle-down");
		} else {
			// comment is now shown
			$(this).removeClass("fa-chevron-circle-down").addClass("fa-chevron-circle-up");
		}
	});
});
