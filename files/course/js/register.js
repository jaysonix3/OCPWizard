$(".btn-block").click(function(event){
	event.preventDefault();
	var d = new Date();
	var currentDate = d.toLocaleString('default', {dateStyle: 'long'});

	fields = { };
	missing = [];
	$.each($('form').serializeArray(), function() {
    	if(this.name != 'middlename')
    		if(this.value=="")
    			missing.push(this.name);

   		fields[this.name] = this.value;
	});

   fields["current_module"] = 0;
   fields["date_started"] = currentDate;

	if(missing.length){
		$(".alert-danger").removeClass("d-none");
		$.each(missing, function() {
		  $("input[name="+ this +"]").css("border", "1px solid #d17775");
		  $("textarea[name="+ this +"]").css("border", "1px solid #d17775");
		});

		return;
	}

	module_quiz = {};
	module_questions = {};
	for (var i = 1; i <= 1 ; i++) {
		module_quiz[i] = -1;
		module_questions[i] = "";
	}
	module_quiz['final'] = -1;

	localStorage.setItem('profile', JSON.stringify(fields));
	localStorage.setItem('quizzes', JSON.stringify(module_quiz));
	localStorage.setItem('questions', JSON.stringify(module_questions));

	$(".form-input").css("display", "none");
	$(".full-name").html(fields['firstname'] + " " + fields['lastname']);
	$(".success-message").css("display", "block");

});