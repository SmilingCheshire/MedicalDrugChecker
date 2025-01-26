$(document).ready(function () {
    const BASE_API_URL = "/med_checker";

    // Function to clear the search container
    function clearSearchContainer() {
        $("#drug_search_textbox").val("");
        $("#messages_container .alert").text("").parent().addClass("hidden");
    }

    // Function to search for a medicine
    function searchDrug() {
        const drugName = $("#drug_search_textbox").val().trim();
        if (!drugName) {
            $("#messages_container .alert").text("Please enter a drug name.").parent().removeClass("hidden");
            return;
        }

        $.get(`${BASE_API_URL}/search/${drugName}`)
            .done((data) => {
                $("#medicine_table_body").empty();
                const drugIds = Object.keys(data);
                if (drugIds.length > 0) {
                    for (const [id, details] of Object.entries(data)) {
                        const row = `
                            <tr data-id="${id}">
                                <td>${details.brand_name || "N/A"}</td>
                                <td>${details.generic_name || "N/A"}</td>
                                <td>${details.active_ingredient || "N/A"}</td>
                                <td>${details.purpose || "N/A"}</td>
                                <td>${details.manufacturer_name || "N/A"}</td>
                                <td>
                                    <button class="btn btn-sm btn-primary add-to-checker"><i class="bi bi-plus-circle"></i></button>
                                    <button class="btn btn-sm btn-secondary clear-entry"><i class="bi bi-trash"></i></button>
                                </td>
                            </tr>`;
                        $("#medicine_table_body").append(row);
                    }
                    $("#found_medicine_container").removeClass("hidden");
                    clearSearchContainer();
                }    
            })
            .fail(() => {
                $("#messages_container .alert").text("Failed to search for medicine.").parent().removeClass("hidden");
            });
    }

    // Function to clear the found medicine container
    function clearFoundContainer() {
        $("#medicine_table_body").empty();
    }

    // Function to add medicine to the checker list
    function addToChecker() {
        const selectedRow = $(this).closest("tr");
        const drugId = selectedRow.data("id");
        const brandName = selectedRow.find("td:nth-child(1)").text();
        const genericName = selectedRow.find("td:nth-child(2)").text();
        const activeIngredient = selectedRow.find("td:nth-child(3)").text();
        const purpose = selectedRow.find("td:nth-child(4)").text();
        const manufacturer = selectedRow.find("td:nth-child(5)").text();

        if (drugId) {
            const drugElement = `
                <tr data-id="${drugId}">
                    <td>${brandName}</td>
                    <td>${genericName}</td>
                    <td>${activeIngredient}</td>
                    <td>${purpose}</td>
                    <td>${manufacturer}</td>
                </tr>`;
            $("#drugs_checker_table_body").append(drugElement);
            selectedRow.remove();
            clearFoundContainer();
            $("#found_medicine_container").addClass("hidden");
        }
    }

    // Function to clear the drugs checker container
    function clearDrugsCheckerContainer() {
        $("#drugs_checker_table_body").empty();
        $("#checking_result_container .alert").html('');
        $("#checking_result_container").addClass("hidden");
        $("#check_button").prop("disabled", false);
    }

    // Function to check medication compatibility
    function checkMedications() {
        const medicineIds = $("#drugs_checker_table_body tr").map(function () {
            return $(this).data("id");
        }).get();

        if (medicineIds.length === 0) {
            $("#messages_container .alert").text("No medications to check.").parent().removeClass("hidden");
            return;
        }

        const checkButton = $("#check_button");
        const originalButtonContent = checkButton.html();

        // Show spinner on the button
        checkButton.html(`
            <span class="spinner-border spinner-border-sm" aria-hidden="true"></span>
            <span class="visually-hidden" role="status">Checking...</span>
        `).prop("disabled", true);

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
                $("#checking_result_container .alert").html(result).parent().removeClass("hidden");                
            },
            error: (xhr) => {
                const errorMsg = xhr.responseJSON?.error || "Failed to check medications.";
                $("#messages_container .alert").text(errorMsg).parent().removeClass("hidden");
                checkButton.html(originalButtonContent).prop("disabled", true);
            },
            complete: () => {
                // Restore the button after the request completes
                checkButton.html(originalButtonContent).prop("disabled", true);
            }
        });
    }

    // Event listeners
    $("#search_button").click(searchDrug);
    $("#clear_search_button").click(clearSearchContainer);
    $(document).on("click", ".add-to-checker", addToChecker);
    $("#clear_checker_button").click(clearDrugsCheckerContainer);
    $("#check_button").click(checkMedications);

    // Ensure drugs checker table is always visible but empty at start
    clearDrugsCheckerContainer();
});