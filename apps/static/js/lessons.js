const lessons_tbody = $("#lessons_tbody");
let openedMonths = [];
LESSONS_STATUTES = {
    ZAPLANOWANA: 'zaplanowana',
    NIEOBECNOSC: 'nieobecnosc',
    ODWOLANA_NAUCZYCIEL: 'odwolana_nauczyciel',
    ODWOLANA_24H_PRZED: 'odwolana_24h_przed',
}
function isGroupPage() {
    const pathSegments = window.location.pathname.split('/').filter(Boolean);  // Podziel URL na fragmenty
    return pathSegments[0] === 'group';  // Sprawdź, czy pierwszy fragment to 'group'
}

function get_lessons(record_id) {
    $.ajax({
        url: '/crm_api/get-lessons/' + record_id,
        type: 'GET',
        data: {
            selected_year: $('#selected-year').text(),
        },
        dataType: 'json',
        success: function (response) {
            if (response.status) {

                const tableContainer = $('#table-container');
                tableContainer.empty();
                tableContainer.html(generateTable(response.lessons));

                open_months_url();

                if (isGroupPage()) {
                    modifyTable();
                }
            } else {
                handleResponse(response);
            }
            return 0;
        },
        error: function (error) {
            console.error('B\u0142\u0105d pobierania lekcji', error);
            return 0;

        }
    });
    return 0;
}


function generateTable(data) {
    // Creating table
    var table = document.createElement('table');
    table.classList.add('table', 'table-bordered', 'table-striped');
    table.id = "lesson_table";

    var thead = document.createElement('thead');
    var headerRow = document.createElement('tr');

    // Creating header
    var headers = ['Miesi\u0105c', 'Zaplanowane', 'Odwo\u0142ane - nauczyciel', 'Odwo\u0142ane - 24h przed', 'Nieobecne'];
    headers.forEach(function (headerText) {
        var th = document.createElement('th');
        th.textContent = headerText;
        th.classList.add('text-center');
        headerRow.appendChild(th);
    });

    thead.appendChild(headerRow);
    table.appendChild(thead);

    var tbody = document.createElement('tbody');
    tbody.setAttribute('id', 'lessons_tbody');

    // Iterating all months and statutes (e.g. 1: {Cancelled: 1, Planned: 0}, 2: : {Cancelled: 0, Planned: 0} 3: ....)
    Object.entries(data).forEach(function ([month_number, statutes]) {
        var row = document.createElement('tr');

        var monthCell = document.createElement('th');
        monthCell.setAttribute('scope', 'row');
        monthCell.classList.add('text-center');
        monthCell.addEventListener('click', function () {
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
        zaplanowaneCell.textContent = statutes[LESSONS_STATUTES.ZAPLANOWANA];
        row.appendChild(zaplanowaneCell);


        var odwolaneTeacherCell = document.createElement('td');
        odwolaneTeacherCell.classList.add('text-center');
        odwolaneTeacherCell.textContent = statutes[LESSONS_STATUTES.ODWOLANA_NAUCZYCIEL];
        row.appendChild(odwolaneTeacherCell);

        var odwolane24hCell = document.createElement('td');
        odwolane24hCell.classList.add('text-center', 'cancelled-24h-cells');
        odwolane24hCell.textContent = statutes[LESSONS_STATUTES.ODWOLANA_24H_PRZED];
        row.appendChild(odwolane24hCell);

        var canceledeCell = document.createElement('td');
        canceledeCell.classList.add('text-warning', 'text-center', 'cancelled-cell');
        canceledeCell.textContent = statutes[LESSONS_STATUTES.NIEOBECNOSC];
        row.appendChild(canceledeCell);

        tbody.appendChild(row);

        var detailsRow = document.createElement('tr');
        var detailsCell = document.createElement('td');
        detailsCell.setAttribute('colspan', '7');
        detailsCell.classList.add("p-0");

        var detailsCollapse = document.createElement('div');
        detailsCollapse.classList.add('collapse');
        detailsCollapse.classList.add('in');
        detailsCollapse.setAttribute('id', 'collaps_' + month_number);

        var innerTable = document.createElement('table');
        innerTable.classList.add('table');

        var innerTbody = document.createElement('tbody');

        if (!jQuery.isEmptyObject(statutes['Lessons'])) {
            Object.entries(statutes['Lessons']).forEach(function ([key, lesson]) {
                const lessonRow = document.createElement('tr');

                const lessonDateCell = document.createElement('td');
                lessonDateCell.textContent = lesson['start_date'] + ' (' + lesson['weekday'] + ')';

                if (lesson['original_date'] !== lesson['start_date']) {
                    lessonDateCell.textContent += ' (przeniesione z ' + lesson['original_date'] + ' ' + lesson['original_time'] + ')';
                } else if (lesson['original_time'] !== lesson['start_time']) {
                    lessonDateCell.textContent += ' (przeniesione z ' + lesson['original_time'] + ')';
                }

                if (lesson.status === "zaplanowana") {
                    lessonRow.classList.add("bg-primary-light");
                } else {
                    if (lesson.status === 'nieobecnosc') {
                        lessonRow.classList.add("bg-danger-light");
                    } else {
                        lessonRow.classList.add("bg-orange-light");
                    }
                }

                lessonRow.appendChild(lessonDateCell);

                var lessonTimeCell = document.createElement('td');
                lessonTimeCell.textContent = lesson['start_time'] + ' - ' + lesson['end_time'];
                lessonRow.appendChild(lessonTimeCell);

                var lessonDescriptionCell = document.createElement('td');
                lessonDescriptionCell.textContent = lesson['description'];
                lessonRow.appendChild(lessonDescriptionCell);

                const teacherCell = document.createElement('td');
                // teacherCell.classList.add('d-flex');
                const teacherSvg = document.createElementNS('http://www.w3.org/2000/svg', 'svg');
                const teacherPath = document.createElementNS(
                    'http://www.w3.org/2000/svg',
                    'path'
                );
                teacherSvg.setAttribute('fill', 'none');
                teacherSvg.setAttribute('viewBox', '0 0 24 24');
                teacherSvg.setAttribute('stroke', 'currentColor');
                teacherSvg.setAttribute('stroke-width', '1.5');
                teacherSvg.classList.add('mr-1');
                teacherSvg.setAttribute('width', '18px');

                teacherPath.setAttribute(
                    'd',
                    'M17.982 18.725A7.488 7.488 0 0 0 12 15.75a7.488 7.488 0 0 0-5.982 2.975m11.963 0a9 9 0 1 0-11.963 0m11.963 0A8.966 8.966 0 0 1 12 21a8.966 8.966 0 0 1-5.982-2.275M15 9.75a3 3 0 1 1-6 0 3 3 0 0 1 6 0Z'
                );
                teacherPath.setAttribute('stroke-linecap', 'round');
                teacherPath.setAttribute('stroke-linejoin', 'round');

                teacherSvg.appendChild(teacherPath);

                // Add SVG and teacher name
                teacherCell.appendChild(teacherSvg);
                teacherCell.append(lesson['teacher']);
                lessonRow.appendChild(teacherCell);

                const locationCell = document.createElement('td');

                const locationSvg = document.createElementNS('http://www.w3.org/2000/svg', 'svg');
                const locationPath1 = document.createElementNS('http://www.w3.org/2000/svg', 'path');
                const locationPath2 = document.createElementNS('http://www.w3.org/2000/svg', 'path');

                locationSvg.setAttribute('width', '20px');
                locationSvg.classList.add('svg-icon');
                locationSvg.setAttribute('xmlns', 'http://www.w3.org/2000/svg');
                locationSvg.setAttribute('fill', 'none');
                locationSvg.setAttribute('viewBox', '0 0 24 24');
                locationSvg.setAttribute('stroke', 'currentColor');

                locationPath1.setAttribute('stroke-linecap', 'round');
                locationPath1.setAttribute('stroke-linejoin', 'round');
                locationPath1.setAttribute('d', 'M15 10.5a3 3 0 1 1-6 0 3 3 0 0 1 6 0Z');

                locationPath2.setAttribute('stroke-linecap', 'round');
                locationPath2.setAttribute('stroke-linejoin', 'round');
                locationPath2.setAttribute('d', 'M19.5 10.5c0 7.142-7.5 11.25-7.5 11.25S4.5 17.642 4.5 10.5a7.5 7.5 0 1 1 15 0Z');

                locationSvg.appendChild(locationPath1);
                locationSvg.appendChild(locationPath2);

                locationSvg.setAttribute('data-content', lesson['location']);
                locationSvg.setAttribute('data-placement', 'bottom');
                locationSvg.setAttribute('data-trigger', 'hover');
                locationSvg.setAttribute('data-toggle', 'popover');
                locationSvg.setAttribute('data-html', 'true');
                $(locationSvg).popover();

                locationCell.append(locationSvg)
                lessonRow.appendChild(locationCell);

                var lessonStatusCell = document.createElement('td');
                lessonStatusCell.textContent = lesson['status'];
                lessonRow.appendChild(lessonStatusCell);

                const editCell = document.createElement('td');
                const editLink = document.createElement('a');
                editLink.text = 'Edytuj'
                editLink.className = 'bg-blue text-white p-1 rounded-sm font-size-12 menu-button text-center';
                editLink.type = 'button';
                editLink.setAttribute('data-toggle', 'modal');
                editLink.setAttribute('data-target', '#editEventModalCenter');
                editLink.setAttribute("onclick", `modifyEvent(lesson_schedule_id='${lesson.lesson_id}', startTime='${lesson.start_time}', endTime='${lesson.end_time}', lessonDate='${lesson.start_date}', studentName='', status='${lesson.status}');`);


                editCell.appendChild(editLink);
                lessonRow.appendChild(editCell);


                innerTbody.appendChild(lessonRow);
            });
        } else {
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

function getMonthName(monthNumber) {
    var months = [
        "Stycze\u0144", "Luty", "Marzec", "Kwiecie\u0144", "Maj", "Czerwiec",
        "Lipiec", "Sierpie\u0144", "Wrzesie\u0144", "Pa\u017Adziernik", "Listopad", "Grudzie\u0144"
    ];
    return months[monthNumber - 1];
}

function toggleDetails(element) {
    var targetId = element.children[0].getAttribute('data-target');
    var target = document.querySelector(targetId);
    target.classList.toggle('show');
}

function open_months_url() {
    let urlParams = new URLSearchParams(window.location.search);
    openedMonths = urlParams.get('opened_months');
    if (openedMonths) {
        openedMonths = openedMonths.split(',');
        openedMonths.forEach(function (monthNumber) {
            let collapsibleDiv = document.getElementById('collaps_' + monthNumber);
            if (collapsibleDiv) {
                collapsibleDiv.classList.add('show');
            }
        });
    } else {
        openedMonths = [];
    }
}