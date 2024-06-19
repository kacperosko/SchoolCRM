
const lessons_tbody = $("#lessons_tbody");
var tableContainer = document.getElementById('table-container');

function get_lessons(student_id) {

    $.ajax({
        url: '/crm_api/get-lessons/' + student_id,
        type: 'POST',
        data: {
            csrfmiddlewaretoken: $(csrf_token).val(),
        },
        dataType: 'json',
        success: function (response) {
            if (response.status) {
                response.message = "Pobrano lekcje pomyslne";
                handleResponse(response);
                console.log("Pobrano lekcje pomyslne");
                console.log(response.lessons);
                tableContainer.appendChild(generateTable(response.lessons));
            }else {
                handleResponse(response);
            }
        },
        error: function (error) {
            console.error('Error creating note:', error);
            alert('Failed to create note.');
        }
    });
}


function generateTable(data) {
    var table = document.createElement('table');
    table.classList.add('table', 'table-bordered', 'table-striped');

    var thead = document.createElement('thead');
    var headerRow = document.createElement('tr');

    var headers = ['Miesiąc', 'Zaplanowane', 'Odwołane'];
    headers.forEach(function(headerText) {
        var th = document.createElement('th');
        th.textContent = headerText;
        th.classList.add('text-center');
        headerRow.appendChild(th);
    });

    thead.appendChild(headerRow);
    table.appendChild(thead);

    var tbody = document.createElement('tbody');
    tbody.setAttribute('id', 'lessons_tbody');

    Object.entries(data).forEach(function([month_number, statutes]) {
        var row = document.createElement('tr');

        var monthCell = document.createElement('th');
        monthCell.setAttribute('scope', 'row');
        monthCell.classList.add('text-center');
        monthCell.addEventListener('click', function() {
            toggleDetails(this);
        });

        var monthLink = document.createElement('a');
        monthLink.setAttribute('type', 'button');
        monthLink.setAttribute('href', '');
        monthLink.classList.add('collapsed');
        monthLink.setAttribute('data-toggle', 'collapse');
        monthLink.setAttribute('onclick', 'refreshOpenedMonths()');
        monthLink.setAttribute('id', 'collapser_' + month_number);
        monthLink.setAttribute('data-target', '#collaps_' + month_number);
        monthLink.textContent = getMonthName(month_number);
        monthCell.appendChild(monthLink);

        row.appendChild(monthCell);

        var zaplanowaneCell = document.createElement('td');
        zaplanowaneCell.classList.add('text-center');
        zaplanowaneCell.textContent = statutes['Zaplanowana'];
        row.appendChild(zaplanowaneCell);

        var odwolaneCell = document.createElement('td');
        odwolaneCell.classList.add('text-warning', 'text-center');
        odwolaneCell.textContent = statutes['Canceled'];
        row.appendChild(odwolaneCell);

        tbody.appendChild(row);

        // Dodanie szczegółów
        var detailsRow = document.createElement('tr');
        var detailsCell = document.createElement('td');
        detailsCell.setAttribute('colspan', '3');
        detailsCell.classList.add("p-0");

        var detailsCollapse = document.createElement('div');
        detailsCollapse.classList.add('collapse');
        detailsCollapse.classList.add('in');
        detailsCollapse.setAttribute('id', 'collaps_' + month_number);

        var innerTable = document.createElement('table');
        innerTable.classList.add('table');

        var innerTbody = document.createElement('tbody');

        // Generowanie lekcji
        if (statutes['Lessons']) {
            Object.entries(statutes['Lessons']).forEach(function([key, lesson]) {
                var lessonRow = document.createElement('tr');

                var lessonDateCell = document.createElement('td');
                lessonDateCell.textContent = lesson['start_date'] + ' (' + lesson['weekday'] + ')';
                if (lesson['original_date']) {
                    lessonDateCell.textContent += ' (przeniesione z ' + lesson['original_date'] + ')';
                }
                lessonRow.appendChild(lessonDateCell);

                var lessonTimeCell = document.createElement('td');
                lessonTimeCell.textContent = lesson['start_time'] + ' - ' + lesson['end_time'];
                lessonRow.appendChild(lessonTimeCell);

                var lessonDescriptionCell = document.createElement('td');
                lessonDescriptionCell.textContent = lesson['description'];
                lessonRow.appendChild(lessonDescriptionCell);

                var teacherCell = document.createElement('td');
                var teacherSvg = document.createElement('svg');
                // Dodaj SVG ikony i inne elementy
                teacherCell.appendChild(teacherSvg);
                teacherCell.textContent = lesson['teacher'];
                lessonRow.appendChild(teacherCell);

                var editCell = document.createElement('td');
                var editLink = document.createElement('a');
                // Dodaj link do edycji i inne elementy
                editCell.appendChild(editLink);
                lessonRow.appendChild(editCell);

                innerTbody.appendChild(lessonRow);
            });
        } else {
            // Brak lekcji
            var noLessonsRow = document.createElement('tr');
            noLessonsRow.classList.add('bg-light', 'text-center');

            var noLessonsCell = document.createElement('td');
            noLessonsCell.setAttribute('colspan', '3');
            noLessonsCell.textContent = 'Brak lekcji';

            noLessonsRow.appendChild(noLessonsCell);
            innerTbody.appendChild(noLessonsRow);
        }

        innerTable.appendChild(innerTbody);
        detailsCollapse.appendChild(innerTable);
        detailsCell.appendChild(detailsCollapse);
        detailsRow.appendChild(detailsCell);
        tbody.appendChild(detailsRow);
    });

    table.appendChild(tbody);

    return table;
}

// Funkcja pomocnicza do zmiany numeru miesiąca na jego nazwę
function getMonthName(monthNumber) {
    var months = [
        "Styczeń", "Luty", "Marzec", "Kwiecień", "Maj", "Czerwiec",
        "Lipiec", "Sierpień", "Wrzesień", "Październik", "Listopad", "Grudzień"
    ];
    return months[monthNumber - 1];
}

// Funkcja do zmiany widoczności szczegółów miesiąca
function toggleDetails(element) {
    var targetId = element.children[0].getAttribute('data-target');
    var target = document.querySelector(targetId);
    target.classList.toggle('show');
}

// Generowanie tabeli i dodanie jej do elementu o id "table-container"
