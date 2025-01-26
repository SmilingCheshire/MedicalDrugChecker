$(document).ready(function () {
    const BASE_API_URL = "/med_checker"; // Assuming the backend is running in the same container

    // Function to clear the search container
    function clearSearchContainer() {
        $("#drug_search_textbox").val("");
        $("#messages_container").addClass("hidden").text("");
    }

    // Function to search for a medicine
    function searchDrug() {
        const drugName = $("#drug_search_textbox").val().trim();
        if (!drugName) {
            $("#messages_container").removeClass("hidden").text("Please enter a drug name.");
            return;
        }

        // API call to search medicine
        $.get(`${BASE_API_URL}/search/${drugName}`)
            .done((data) => {
                const drugIds = Object.keys(data);
                if (drugIds.length > 0) {
                    const drugId = drugIds[0];
                    const drugName = data[drugId][0];

                    $("#found_medicine_name").text(drugName);
                    $("#found_medicine_id").val(drugId);
                    $("#found_medicine_container").removeClass("hidden");
                    clearSearchContainer();
                } else {
                    $("#messages_container").removeClass("hidden").text("No medicine found.");
                }
            })
            .fail(() => {
                $("#messages_container").removeClass("hidden").text("Failed to search for medicine.");
            });
    }

    // Function to add medicine to the checker list
    function addToChecker() {
        const drugName = $("#found_medicine_name").text();
        const drugId = $("#found_medicine_id").val();

        if (drugId) {
            const drugElement = `
                <div class="drug-item">
                    <div>${drugName}</div>
                    <div class="hidden">${drugId}</div>
                </div>
            `;
            $("#drugs_list").append(drugElement);
            clearFoundContainer();
        }
    }

    // Function to clear the found medicine container
    function clearFoundContainer() {
        $("#found_medicine_name").text("");
        $("#found_medicine_id").val("");
        $("#found_medicine_container").addClass("hidden");
    }

    // Function to clear drugs checker container
    function clearDrugsCheckerContainer() {
        $("#drugs_list").empty();
        $("#checking_result_container").addClass("hidden").text("");
    }

    // Function to check medication compatibility
    function checkMedications() {
        const medicineIds = $(".drug-item .hidden").map(function () {
            return $(this).text();
        }).get();

        if (medicineIds.length === 0) {
            $("#messages_container").removeClass("hidden").text("No medications to check.");
            return;
        }

        $.ajax({
            url: `${BASE_API_URL}/check`,
            method: "POST",
            contentType: "application/json",
            data: JSON.stringify({ medicine_id: medicineIds }),
            success: (data) => {
                const result = `
                    <strong>Severity:</strong> ${data.severity}<br>
                    <strong>Short Description:</strong> ${data.short_description}<br>
                    <strong>Description:</strong> ${data.description}
                `;
                $("#checking_result_container").removeClass("hidden").html(result);
            },
            error: (xhr) => {
                const errorMsg = xhr.responseJSON?.error || "Failed to check medications.";
                $("#messages_container").removeClass("hidden").text(errorMsg);
            },
        });
    }

    // Event listeners
    $("#search_button").click(searchDrug);
    $("#clear_search_button").click(clearSearchContainer);
    $("#add_to_checker_button").click(addToChecker);
    $("#clear_found_button").click(clearFoundContainer);
    $("#check_button").click(checkMedications);
    $("#clear_checker_button").click(clearDrugsCheckerContainer);
});