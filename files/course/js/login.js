$(document).ready(function() {
	if(localStorage){
		profile = JSON.parse(localStorage.getItem('profile'));
		$('input[name="username"]').attr('value',profile['username']);
	}
});

$('form').submit(function(e){
	e.preventDefault();
	if(localStorage){
		profile = JSON.parse(localStorage.getItem('profile'));
		if($('input[name="username"]').val()==profile['username'] && $('input[name="password"]').val()==profile['password'])
			window.location.replace("course.html");
		else
			window.alert("Invalid username and password. If this is your first time, please register.");
	}
	else
		window.alert("Please register first.");
})