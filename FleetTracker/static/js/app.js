
const flaskdata = $('#data').data();

if ( typeof flaskdata != 'undefined' ) {
  $('.title').html('Maintenance for ' + flaskdata.pump);
  $('.title-admin').html('Maintenance for ' + flaskdata.pump)
};

$('.flash').hide().slideDown(1000).delay(2000).slideUp(1000);

$('.col_2').hide();

$('.col_3').hide();

$('.col_4').hide();

$('.form').hide();

$('#maintenance-button').hide();

$('.grease').hide();

$('#maintenance_type').change(

  function () {
    if ( $('#maintenance_type').val() === 'other') {
      $('.form').fadeIn(1000);
      $('.col_2').hide();
      $('.col_3').hide();
      $('.col_4').hide();
      $('.grease').hide();
      $('#maintenance-button').hide();
    } else {
    $('.form').hide();
    $('.col_2').fadeIn(1000);

    $('.col_3').hide();

    $('.col_4').hide();

    $('#maintenance-button').hide();

    $('#Hole').val('select hole')

    $('.grease').hide();
  }
});

$('#Hole').change(function () {
    if ( $('#maintenance_type').val() === 'valves & seats')
    {$('.col_3').fadeIn(1000);
      $('.grease').fadeIn(1000);
    }
    else if ( $('#maintenance_type').val() === 'packing')
    {$('.col_4').fadeIn(1000);
    $('.grease').fadeIn(1000);}
});

$('#grease_psi').on('keypress', function (event) {
      $('#maintenance-button').fadeIn(1000);
    }
);
