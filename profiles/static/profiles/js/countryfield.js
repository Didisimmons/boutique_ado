// get the value of the country field when the page loads
let countrySelected = $('#id_default_country').val();
/* Remember that the value will be an empty string if the first option is selected.
/* to determine if that's selected we can use this as a boolean.
/* So if country selected is false.
Then we want the colour of this element to be that grey placeholder colour.
*/
if(!countrySelected) {
    $('#id_default_country').css('color', '#aab7c4');
};
$('#id_default_country').change(function() { // every time the box changes we'll get the value of it. And then determine the proper colour.
    countrySelected = $(this).val();
    if(!countrySelected) {
        $(this).css('color', '#aab7c4');
    } else {
        $(this).css('color', '#000');
    }
})