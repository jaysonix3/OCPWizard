$(document).ready(function() {
	profile = JSON.parse(localStorage.getItem('profile'));
	$("#fullname").text(profile['lastname'].toUpperCase() + ", " + profile['firstname']);

	quizzes = JSON.parse(localStorage.getItem('quizzes'));
	questions = JSON.parse(localStorage.getItem('questions'));

	table_content = "";
	
	$.each(quizzes, function(modnum, score) {
		if(modnum!='final'){
	    	if(modnum){
		    	table_content += "<tr>"
			    if(score > -1)
		    		table_content += "<td>" + modnum + "</td>" + "<td><a href='#' data-module='" + modnum + "'>" + score + "%</a></td>"
			    else
		    		table_content += "<td>" + modnum + "</td>" + "<td><a href='#' data-module='" + modnum + "'>Not yet attempted</a></td>"
		    	table_content += "<td>" + questions[modnum] + "</td>";
		    	table_content += "</tr>"
			    }
			}
	});

	$("tbody").append(table_content);

	fscore = (quizzes['final'] != -1) ? quizzes['final'] + " %" : "Not yet attempted";
	$("#final_exam_score").html(fscore);

	if(checkTotal())
		$("#go_final").removeClass("disabled");


});

$("#dlpdf").click(function(event){
	window.print();
});

$("#go_final").click(function(event){
	profile['current_module'] = 11;
	localStorage.setItem('profile', JSON.stringify(profile));
	window.location.replace("course.html");
});

$(".table").on("click", "td a", function(){
	modalpha = ($(this).data("module") + 9).toString(36);
	if($(this).data("module") == 1 || ($(this).data("module") > 1 && quizzes[$(this).data("module")-1] >= 100)){
		profile['current_module'] = $(this).data("module");
		localStorage.setItem('profile', JSON.stringify(profile));
	    window.location = 'course.html?t=' + modalpha;
	}else{
		window.alert("You need to get a perfect score on the previous quiz to proceed.");
	}
});