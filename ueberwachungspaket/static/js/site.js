$(document).ready(function() {
	if($("#representatives").length) {
		$("#parties :checkbox").change(search);

		$("#teams :checkbox").change(search);
	}
});

function search(event) {
	$("#representatives").children(".representative").each(function() {
		if(($("#" + $(this).data("party")).prop("checked") || $("#parties").children(":checked").length == 0)
		&& ($("#" + $(this).data("team")).prop("checked") || $("#teams").children(":checked").length == 0)) {
			$(this).removeClass("invisible");
		} else {
			$(this).addClass("invisible");
		}
	});
}
