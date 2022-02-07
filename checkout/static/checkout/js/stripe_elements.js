/*
    Core logic/payment flow for this comes from here:
    https://stripe.com/docs/payments/accept-a-payment
    CSS from here: 
    https://stripe.com/docs/stripe-js
*/
/* slice off the first and last character on each
since they'll have quotation marks which we don't want
*/
var stripePublicKey = $('#id_stripe_public_key').text().slice(1, -1);
var clientSecret = $('#id_client_secret').text().slice(1, -1);
var stripe = Stripe(stripePublicKey);
/* create instance of stripe elements */
var elements = stripe.elements();
/* make sure style elements appear before creating card  */
var style = {
    base: {
        color: '#000',
        fontFamily: '"Helvetica Neue", Helvetica, sans-serif',
        fontSmoothing: 'antialiased',
        fontSize: '16px',
        '::placeholder': {
            color: '#aab7c4'
        }
    },
    invalid: {
        color: '#dc3545',
        iconColor: '#dc3545'
    }
};
/* create card element */
var card = elements.create('card', {style: style});
/* mount the card element to the div we created in checkout.html */
card.mount('#card-element');

// Handle realtime validation errors on the card element
card.addEventListener('change', function (event) {
    var errorDiv = document.getElementById('card-errors');
    // if errors are present display them in the card error div created near the card element on chekout.html
    if (event.error) {
        var html = `
            <span class="icon" role="alert">
                <i class="fas fa-times"></i>
            </span>
            <span>${event.error.message}</span>
        `;
        $(errorDiv).html(html);
    } else {
        errorDiv.textContent = '';
    }
});

// Handle form submit on checkout.html
var form = document.getElementById('payment-form');

form.addEventListener('submit', function(ev) {
    // listener prevents the default action to post
    ev.preventDefault();
    // before sending info, the card element and submit button are disabled to prevent multiple submissions
    card.update({ 'disabled': true});
    $('#submit-button').attr('disabled', true);
    // This sends the card information securely to stripe
    // clientSecret is are python variable syntax used above  
    stripe.confirmCardPayment(clientSecret, {
        payment_method: {
            card: card,
        } // execute function on result 
    }).then(function(result) {
        if (result.error) {
            var errorDiv = document.getElementById('card-errors');
            var html = `
                <span class="icon" role="alert">
                <i class="fas fa-times"></i>
                </span>
                <span>${result.error.message}</span>`;
            // if there's an error we want to re-enable the card element and submit button to allow the user fix it. 
            $(errorDiv).html(html);
            card.update({ 'disabled': false});
            $('#submit-button').attr('disabled', false);
        } else {
            if (result.paymentIntent.status === 'succeeded') {
                form.submit();
            }
        }
    });
});

