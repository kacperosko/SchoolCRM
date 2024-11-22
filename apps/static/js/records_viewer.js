const records_table = $("#records_table tbody");
const records_table_headers = $("#records_table thead");
const prev_button = $("#prev-page");
const next_button = $("#next-page");
const page_info = $("#page-info");
const search_input = $("#search-input");
const search_button = $("#search-button");


// Funkcja do pobierania rekordów z serwera
function fetchRecords(page = 1, query = "") {
    $.ajax({
        url: '/crm_api/records/all',
        type: 'GET',
        data: {
            model_name: model_name,
            page: page,
            query: query,
            order_field: order_field,
        },
        dataType: 'json',
        success: function (data) {
            if (data.success) {
                if (is_related_list && !headers_loaded){
                    generateHeaders(data.fields);
                }
                updateTable(data.records);
                updatePagination(data);
                updateOrderIcons();
                renderPagination(data.num_pages, data.records_number);
                currentPage = data.records_number; // Aktualizuj bieżącą stronę
            } else {
                handleResponse(data); // Wyświetl wiadomość o błędzie
            }
        },
        error: function (error) {
            console.error('Error fetching records:', error);
        }
    });
}

function generateHeaders(fields) {
    console.log(fields);
    // fields.forEach(field => {
    // });
    for (const [field, label] of Object.entries(fields)) {
        const row = $(`<td id="${field}">${label}</td>`);
        records_table_headers.append(row);
    }
}

// Funkcja do aktualizacji tabeli z rekordami
function updateTable(records) {
    records_table.empty(); // Wyczyść tabelę

    if (records.length > 0) {
        records.forEach(record => {
            const row = $("<tr id=''></tr>");
            let isFirstField = true;

            Object.entries(record).forEach(([key, value]) => {
                if (key === 'id') {
                    return;
                }
                let displayValue;
                if (typeof value == "boolean") {
                    if (value){
                        displayValue = `
                            <div class="mx-auto text-center">
                            <svg xmlns="http://www.w3.org/2000/svg" fill="none" class="text-success" viewBox="0 0 24 24" stroke-width="3" stroke="currentColor" width="18">
                              <path stroke-linecap="round" stroke-linejoin="round" d="m4.5 12.75 6 6 9-13.5" />
                            </svg>
                            </div>
                        `
                    } else {
                        displayValue = `
                            <div class="mx-auto text-center">
                           <svg xmlns="http://www.w3.org/2000/svg" fill="none" class="text-danger" viewBox="0 0 24 24" stroke-width="3" stroke="currentColor" width="18">
                              <path stroke-linecap="round" stroke-linejoin="round" d="M6 18 18 6M6 6l12 12" />
                            </svg>
                            </div>
                        `
                    }
                } else {
                    displayValue = value ? value : "-";
                }



                // Jeśli jest to pierwsze pole, ustaw link do szczegółów rekordu
                if (isFirstField) {
                    row.append(`
                    <td>
                        <a href="/${model_name}/${record.id}">${displayValue}</a>
                    </td>
                `);
                    isFirstField = false; // Ustaw isFirstField na false po dodaniu pierwszego pola
                } else {
                    // Dla pozostałych pól dodaj standardowe komórki
                    row.append(`<td>${displayValue}</td>`);
                }
            });

            records_table.append(row);
        });
    }else {
        const row = $("<tr></tr>");
        const colspan = $("#records_table th").length;
        row.append(`
                    <td colspan="${colspan}" class="text-center">
                        Brak rekordów
                    </td>
                `);
        records_table.append(row);
    }
}

// Funkcja do aktualizacji elementów paginacji
function updatePagination(data) {
    page_info.text(`Strona ${data.records_number} z ${data.num_pages}`);
    prev_button.prop("disabled", !data.has_previous);
    next_button.prop("disabled", !data.has_next);
}

// Obsługa błędów lub odpowiedzi
function handleResponse(data) {
    alert(data.message || "Wystąpił błąd podczas pobierania danych");
}

// Event listener dla przycisku "Poprzednia strona"
prev_button.on("click", function () {
    if (currentPage > 1) {
        fetchRecords(currentPage - 1, search_input.val());
    }
});

// Event listener dla przycisku "Następna strona"
next_button.on("click", function () {
    fetchRecords(currentPage + 1, search_input.val());
});

// Event listener dla przycisku wyszukiwania
const debounce = (func, delay) => {
    let timer;
    return function (...args) {
        clearTimeout(timer);
        timer = setTimeout(() => func.apply(this, args), delay);
    };
};

function isAllowedKey(keyCode) {
    // Klawisze 48-90 to cyfry i litery, a 32 to spacja
    return (
        (keyCode >= 48 && keyCode <= 90) || // Cyfry i litery
        keyCode === 32 ||                   // Spacja
        keyCode === 8                       // Backspace
    );
}

// Zaktualizowana funkcja, która używa debounce
const handleSearch = debounce(function () {
    fetchRecords(1, search_input.val());
}, 400); // 300 ms opóźnienia


function updateOrderIcons() {
    document.querySelectorAll("th svg").forEach(icon => {
        icon.style.opacity = 0.5; // Reset opacity dla wszystkich ikon
    });

    if (order_field) {
        const iconId = `${order_field}_order_icon`;
        const activeIcon = document.getElementById(iconId);
        if (activeIcon) activeIcon.style.opacity = 1;
    }
}


search_input.on("keyup", function (event) {
    if (isAllowedKey(event.keyCode)) {
        handleSearch();
    }
});
// Początkowe pobranie rekordów
document.addEventListener('DOMContentLoaded', function () {
    updateOrderIcons();
    fetchRecords();

    // Event listener dla kliknięć na nagłówki
    document.querySelectorAll("th").forEach(th => {
        th.addEventListener("click", function () {
            const field = th.id;
            order_field = (order_field === field) ? `-${field}` : field;
            fetchRecords(currentPage, search_input.val());
        });
    });

});


function getPaginationRange(totalPages, currentPage) {
    const maxVisiblePages = 7;
    const paginationRange = [];

    paginationRange.push(1);

    if (totalPages > maxVisiblePages) {
        if (currentPage < 5){
            for (let i = 2; i <= 5; i++) {
                paginationRange.push(i);
            }
            paginationRange.push("...");
        }else if(currentPage > totalPages - 4){
            paginationRange.push("...");
            for (let i = totalPages - 4; i < totalPages; i++) {
                paginationRange.push(i);
            }
        } else {
            paginationRange.push("...");
            for (let i = currentPage - 1; i <= currentPage + 1; i++) {
                paginationRange.push(i);
            }
            paginationRange.push("...");
        }
    } else {
        for (let i = 2; i < totalPages; i++) {
            paginationRange.push(i);
        }
    }
    if (totalPages > 1){
        paginationRange.push(totalPages);
    }

    return paginationRange;
}


function renderPagination(numPages, currentPage) {
    const paginationContainer = document.getElementById("pagination");
    paginationContainer.innerHTML = ''; // Czyszczenie kontenera paginacji

    const pages = getPaginationRange(numPages, currentPage);

    // Dodanie przycisku "Poprzednia"
    const prevButton = document.createElement("a");
    prevButton.textContent = "Poprzednia";
    prevButton.className = "btn btn-outline-primary";
    prevButton.style.border = "1px #3378ff solid";
    prevButton.style.borderRadius = "8px 0 0 8px";
    prevButton.href = "#";
    prevButton.onclick = (e) => {
        e.preventDefault();
        if (currentPage > 1) fetchRecords(currentPage - 1);
    };
    if (currentPage === 1) {
        prevButton.style.opacity = "0.5";
        prevButton.style.pointerEvents = "none";
    }
    paginationContainer.appendChild(prevButton);

    // Generowanie przycisków numerów stron
    pages.forEach((page) => {
        if (page === "...") {
            const dots = document.createElement("span");
            dots.textContent = "...";
            dots.className = "px-3 py-2";
            dots.style.border = "1px #3378ff solid";
            dots.style.borderRadius = "0";
            dots.style.opacity = 0.5;
            paginationContainer.appendChild(dots);
        } else {
            const pageButton = document.createElement("a");
            pageButton.textContent = page;
            pageButton.className = "text-center px-3 text-center py-2";
            pageButton.style.border = "1px #3378ff solid";
            pageButton.style.borderRadius = "0";
            pageButton.href = "#";
            if (page === currentPage) {
                pageButton.classList.add("bg-primary");
            }
            pageButton.onclick = (e) => {
                e.preventDefault();
                if (page !== currentPage) fetchRecords(page);
            };
            paginationContainer.appendChild(pageButton);
        }
    });

    // Dodanie przycisku "Następna"
    const nextButton = document.createElement("a");
    nextButton.textContent = "Następna";
    nextButton.className = "btn btn-outline-primary";
    nextButton.style.border = "1px #3378ff solid";
    nextButton.style.borderRadius = "0 8px 8px 0";
    nextButton.href = "#";
    nextButton.onclick = (e) => {
        e.preventDefault();
        if (currentPage < numPages) fetchRecords(currentPage + 1);
    };
    if (currentPage === numPages) {
        nextButton.style.opacity = "0.5";
        nextButton.style.pointerEvents = "none";
    }
    paginationContainer.appendChild(nextButton);
}