$(function() {

  $('#agenda li').click(agenda);

  $('#newsletter').submit(newsletter);

  $('#guestbook_form').submit(guestbook);

  $('#guestbook_link').click(function() {
    $('#guestbook_form').slideToggle();
    return false;
  });

});

$.hashListen('/', function() {
  window.location.hash = '#/home';
});

$.hashListen('/:action/?', function(action) {
  var url = '/'+action;
  $.getJSON(url, null, function(data) {
	fill(data);
  });
});

$.hashListen('/:action/([0-9]+)/?', function(action, id) {
  var top = 500;
  if (action == 'media') {
	top = 300;
  }
  var url = '/'+action+'/'+id;
  $.getJSON(url, null, function(data) {
	fill(data, top);
  });
});

function fill(data, top) {
  var html = Mustache.to_html(data.template, data.data);

  $('#page').fadeOut(top, function() {
	$('#page').html(html);
	$('#page').fadeIn(top);
  });
}

function agenda(evt) {
  $(this).children('.infos').toggle();
}

function newsletter() {
  var form = $('#newsletter');

  $.ajax({
	url: form.attr('action'),
	data: form.serialize(),
	type: 'GET',
	format: 'text',
	success: function(data) {
	  var conf = $('#confirm');
	  if (data.confirm == 0) {
		var mess = 'not submitted';
	  } else if(data.confirm == 2) {
		var mess = 'already subscribed';
	  } else {
		var mess = 'registered !';
	  }
	  conf.html(mess);
	}
  });

  return false;
}

function guestbook() {
  var form = $('#guestbook_form');

  $.ajax({
	url: form.attr('action'),
	data: form.serialize(),
	type: 'POST',
	format: 'text',
	success: function(data) {
	  window.location = '#/guestbook';
	}
  });

  return false;
}