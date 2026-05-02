document.addEventListener("DOMContentLoaded", function () {

    const form = document.getElementById("naissanceForm");

    form.addEventListener("submit", function (e) {

        let valid = true;
        let inputs = form.querySelectorAll("input, select");

        inputs.forEach(input => {

            if (input.value.trim() === "") {
                valid = false;
                input.style.borderColor = "red";
            } else {
                input.style.borderColor = "#ccc";
            }

        });

        if (!valid) {
            e.preventDefault();
            alert("Veuillez remplir tous les champs !");
        }

    });

    // Animation focus
    const fields = document.querySelectorAll("input, select");

    fields.forEach(field => {
        field.addEventListener("focus", () => {
            field.style.transform = "scale(1.02)";
        });

        field.addEventListener("blur", () => {
            field.style.transform = "scale(1)";
        });
    });

});