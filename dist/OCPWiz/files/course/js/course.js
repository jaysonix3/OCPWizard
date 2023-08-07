$(document).ready(function() {
	profile = JSON.parse(localStorage.getItem('profile'));
	changeModule(profile['current_module']);

	var url = window.location.href;
	try{
		var quizAlpha = url.split('?')[1].split('=');
		quizAlpha.shift();
		quizAlpha = quizAlpha + "";

		if(quizAlpha){
			quizNum = quizAlpha.charCodeAt(0) - 96;
			changeModule(quizNum);
			changeQuiz(quizNum);
		}
	}catch(e){

	}
	
});

$(".list-unstyled li a").click(function(){
	if($(this).data("value") <= 11){
		profile['current_module'] = $(this).data("value");
		localStorage.setItem('profile', JSON.stringify(profile));
	}
	changeModule($(this).data("value"));
});

$("#module_questions button").click(function(){
	question = $("#module_questions textarea").val();
	saveQuestion(profile['current_module'], question);
});

$("#resources").click(function(){
	changeModule(-1);
});

$("#module_quiz").on("click", "strong a", function(){
	changeQuiz($(this).data("module"));
});

function changeModule(module){
	iframe_desc_sub = "Study the course module below. Alternatively, you can download it here: ";
	questions = JSON.parse(localStorage.getItem('questions'));
	switch(module){
		case -1:
		 	$('#currentframe').attr('src', 'resources.html');	
			iframe_desc_header = "";
			iframe_desc_sub = ""
			$("#module_quiz").addClass("invisible");
			$("#module_questions").addClass("invisible");
			break;
		case 0:
			$('#currentframe').attr('src', 'introduction.html');	
			iframe_desc_header = "";
			iframe_desc_sub = ""
			$("#module_quiz").addClass("invisible");
			$("#module_questions").addClass("invisible");
			break;
		case 2:
			if(checkTotal()){
				$('#currentframe').attr('src', 'quiz/final-exam.html');
				iframe_desc_header = "";
				iframe_desc_sub = ""
				$("#module_quiz").addClass("invisible");
				$("#module_questions").addClass("invisible");
			}else{
				window.alert("You need to get 100% in all of the quizzes to be able to take the final exam.")
			}
			break;
		default:
			$('#currentframe').attr('src', 'modules/Module'+ module +'.pdf');
			iframe_desc_header = "Topic " + module;
			iframe_desc_sub += "<a href='modules/Module" + module + ".pdf' download target='_blank'> Topic " + module + ".pdf</a><br>Best to take the quiz linked below every after each lesson.";
			$("#module_quiz").html("<strong><a href='#' data-module='"+ module +"'>Topic "+ module +" - Quiz</a></strong>");
			$("#module_questions textarea").val(questions[module]);
			$("#module_quiz").removeClass("invisible");
			$("#module_questions").removeClass("invisible");
	}
	$("#iframe_desc strong").text(iframe_desc_header);
	$("#iframe_desc #sub").html(iframe_desc_sub);
	$("#iframe_desc").removeClass("invisible");
}

function changeQuiz(module){
	quizzes = JSON.parse(localStorage.getItem('quizzes'));

	if(module == 1 || (module > 1 && quizzes[module-1] >= 100)){
		$('#currentframe').attr('src', 'quiz/quiz'+ module +'.html');
		$("#iframe_desc").addClass("invisible");
		$("#module_quiz").addClass("invisible");
		$("#module_questions").addClass("invisible");
	}else{
		window.alert("You need to get a perfect score on the previous quiz to proceed.");
	}
}

function saveQuestion(module, question){
	questions = JSON.parse(localStorage.getItem('questions'));
	questions[module] = question;

	localStorage.setItem('questions', JSON.stringify(questions));
}