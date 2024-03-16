document.addEventListener("DOMContentLoaded", function() {
    // sidenav initialization
    // Courtesy of Code Institute walkthrough project
    let sidenav = document.querySelectorAll(".sidenav");
    M.Sidenav.init(sidenav);


    // Datepicker initialization
    // Courtesy of Code Institute walkthrough project
    let datepicker = document.querySelectorAll('.datepicker');
    M.Datepicker.init(datepicker, {
        format: "dd mmmm, yyyy",
        i18n: {done: "Select"}
    });


    // Open modal window. Courtesy of MaterializeCSS
    let openModal = document.querySelectorAll('.modal');
    M.Modal.init(openModal);


    // Select Initialization for form dropdowns
    // Courtesy of Code Institute walkthrough project/MaterializeCSS
    let selects = document.querySelectorAll('select');
    M.FormSelect.init(selects);


    // Function to allow cancelation of forms with 'required' attribute on input
    // This is to enable compatibility with database schema
    // Get the cancel button element
    // Refined by Chat GPT
    let cancelButton = document.getElementById('cancelButton');

    // Add an event listener to the cancel button
    cancelButton.addEventListener('click', function() {
        // Finds all input fields with the 'required' attribute
        let requiredInputs = document.querySelectorAll('input[required]');

        // Loops through each 'required' input to remove the 'required' attribute
        requiredInputs.forEach(function(input) {
            input.removeAttribute('required');
        });

        // Submits the form
        document.getElementById('workoutForm').submit();
    });
});


// Courtesy of Chat GPT
document.addEventListener("DOMContentLoaded", function() {
    // Close Flash alerts
    // Get all close buttons
    let closeButtons = document.querySelectorAll(".close-alert");

    // Loop through each close button and attach click event listener
    closeButtons.forEach(function(closeButton) {
        closeButton.addEventListener("click", function() {
            // Hide the parent flash message when the close button is clicked
            let flashMessage = this.closest(".flash");
            flashMessage.style.display = "none";
        });
    });
});


// Function to auto update the year at the bottom of the page
// Courtesy of Code Institute walkthrough project
$("#copyright").text(new Date().getFullYear());