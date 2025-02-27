$(function () {


	// testing with Ajax, this will not be used
	/* $('button').click(function(){
		var user = $('#id_url').val();
		var pass = $('#id_title').val();
		$.ajax({
			url: '/signUpUser',
			data: $('form').serialize(),
			type: 'POST',
			success: function(response){
				console.log(response);
			},
			error: function(error){
				console.log(error);
			}
		});
	});
	*/



	// for testing - simple calculator
	/*
	$('a#calculate').bind('click', function () {
		$.getJSON($SCRIPT_ROOT + '/_add_numbers', {
			a: $('input[name="a"]').val(),
			b: $('input[name="b"]').val()
		}, function (data) {
			$("#result").text(data.result);
		});
		return false;
	});
	*/



	// for pdf creator
	/*
	$('button').click(function () {
		$.getJSON($SCRIPT_ROOT + '/pdf_creator', {
			url: $('input[name="url"]').val(),
			title: $('input[name="title"]').val(),
		}, function (data) {
			$("#result").text(data.result);
		});
		return false;
	});
	*/


	// for pdf creator
	/*$(document).ready(function () {
		$("button").click(function () {
			$.post($SCRIPT_ROOT + "/pdf_export_2",
				{
					url: $('input[name="url"]').val(),
					title: $('input[name="title"]').val()
				},
				function (data) {
					$("#result").text(data.result);
				});
		});
	});
	*/

	$(document).ready(function () {
		$("#add_device_submit").click(function () {
			$.ajax({
				'async': true,
				'type': "POST",
				'global': false,
				'dataType': 'html',
				'url': $SCRIPT_ROOT + "/add_device",
				'data': {
					client_name: $('input[name="client_name"]').val(),
					//username: $('input[name="username"]').val(),
					//password: $('input[name="password"]').val(),
					//title: $('input[name="title"]').val(),
					//customer: $('input[name="customer"]').val(),
					//version: $('input[name="version"]').val()
				},
				'success': function (data) {
					$("#result").html(data);
					$("#wait").css("display", "none");
				},

				'beforeSend': function (x) {
					$("#wait").css("display", "inline");
					$("#result").html('Waiting for the result...');
				},

			});
		});
	});


});



