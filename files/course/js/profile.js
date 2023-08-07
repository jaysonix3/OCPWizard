$(document).ready(function() {
	profile = JSON.parse(localStorage.getItem('profile'));

	$('.to-fill').each(function() {
		if(profile[this.id]=="")
			$("#"+this.id).html("NA").change();
		else
			$("#"+this.id).html(profile[this.id]).change();
	});

});

$("#dlpdf").click(function(event){
	window.print();
});