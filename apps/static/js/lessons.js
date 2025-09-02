const lessons_tbody = $("#lessons_tbody");
let openedMonths = [];
let lessons_data = new Map();

LESSONS_STATUTES = {
    ZAPLANOWANA: 'zaplanowana',
    NIEOBECNOSC: 'nieobecnosc',
    ODWOLANA_NAUCZYCIEL: 'odwolana_nauczyciel',
    ODWOLANA_24H_PRZED: 'odwolana_24h_przed',
}

function isGroupPage() {
    const pathSegments = window.location.pathname.split('/').filter(Boolean);  // Podziel URL na fragmenty
    return pathSegments[0] === 'group';  // Sprawdzenie, czy pierwszy aktualna strona to grupa
}

function expandOpenedMonths() {
    let urlParams = new URLSearchParams(window.location.search);
    openedMonths = urlParams.get('opened_months');
    if (!openedMonths) {
        openedMonths = [];
        return
    }
    console.log('listener openedMonths ' + openedMonths)
    openedMonths = openedMonths.split(',');
    openedMonths.forEach(function (monthNumber) {
        let collapsibleDiv = document.getElementById('collaps_' + monthNumber);
        console.log('listener collapsibleDiv ' + collapsibleDiv)
        if (collapsibleDiv) {
            collapsibleDiv.classList.add('show');
        }
    });
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
                tableContainer.html(generateTable(response.lessons, response.attendance_lists));

                open_months_url();
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


function generateTable(data, attendanceLists) {
    // Creating table
    lessons_data = new Map();

    var table = document.createElement('table');
    table.classList.add('table', 'table-bordered', 'table-striped');
    table.id = "lesson_table";

    var thead = document.createElement('thead');
    var headerRow = document.createElement('tr');

    // Creating header
    var headers = ['Miesi\u0105c', 'Zaplanowane', 'Odwo\u0142ane - nauczyciel'];
    if (!isGroupPage()) {
        headers.push('Odwo\u0142ane - 24h przed', 'Nieobecne')
    }
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

        if (!isGroupPage()) {
            var odwolane24hCell = document.createElement('td');
            odwolane24hCell.classList.add('text-center', 'cancelled-24h-cells');
            odwolane24hCell.textContent = statutes[LESSONS_STATUTES.ODWOLANA_24H_PRZED];
            row.appendChild(odwolane24hCell);

            var canceledeCell = document.createElement('td');
            canceledeCell.classList.add('text-warning', 'text-center', 'cancelled-cell');
            canceledeCell.textContent = statutes[LESSONS_STATUTES.NIEOBECNOSC];
            row.appendChild(canceledeCell);
        }

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

                lessons_data.set(lesson.lesson_id, lesson);

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
                lessonStatusCell.textContent = lesson.status_label;
                lessonRow.appendChild(lessonStatusCell);

                const editCell = document.createElement('td');
                // teacherCell.classList.add('d-flex');
                const editSvg = document.createElementNS('http://www.w3.org/2000/svg', 'svg');
                const editPath = document.createElementNS(
                    'http://www.w3.org/2000/svg',
                    'path'
                );
                editSvg.setAttribute('fill', 'none');
                editSvg.setAttribute('viewBox', '0 0 24 24');
                editSvg.setAttribute('stroke', 'currentColor');
                editSvg.setAttribute('stroke-width', '2');
                editSvg.classList.add('mr-1');
                editSvg.setAttribute('width', '18px');

                editPath.setAttribute('d', 'M15.232 5.232l3.536 3.536m-2.036-5.036a2.5 2.5 0 113.536 3.536L6.5 21.036H3v-3.572L16.732 3.732z');
                editPath.setAttribute('stroke-linecap', 'round');
                editPath.setAttribute('stroke-linejoin', 'round');

                editSvg.appendChild(editPath);

                const editLink = document.createElement('a');
                editLink.appendChild(editSvg);
                editLink.type = 'button';
                editLink.setAttribute("onclick", `openEditLessonModal(event_id='${lesson.lesson_id}', startTime='${lesson.start_time}', endTime='${lesson.end_time}', lessonDate='${lesson.start_date}', studentName='', status='${lesson.status}');`);


                editCell.appendChild(editLink);
                lessonRow.appendChild(editCell);

                // ATTENDANCE LIST -tylko dla grup
                if (isGroupPage()) {
                    const attendanceListCell = document.createElement('td');
                    attendanceListCell.setAttribute('id', `at-${lesson.lesson_id}`);
                    if (lesson.lesson_id in attendanceLists){
                        console.log("LIST EXIST FOR LESSON: " + lesson.lesson_id)
                        attendanceListCell.appendChild(attendanceListIcon(attendanceLists[lesson.lesson_id]));
                    } else {

                        const addListSvg = document.createElementNS('http://www.w3.org/2000/svg', 'svg');
                        const addListPath = document.createElementNS(
                            'http://www.w3.org/2000/svg',
                            'path'
                        );
                        addListSvg.setAttribute('fill', 'none');
                        addListSvg.setAttribute('viewBox', '0 0 24 24');
                        addListSvg.setAttribute('stroke', 'currentColor');
                        addListSvg.setAttribute('stroke-width', '1.5');
                        addListSvg.classList.add('mr-1');
                        addListSvg.setAttribute('width', '18px');

                        addListPath.setAttribute('d', 'M12 4.5v15m7.5-7.5h-15');
                        addListPath.setAttribute('stroke-linecap', 'round');
                        addListPath.setAttribute('stroke-linejoin', 'round');

                        addListSvg.setAttribute('data-content', 'Utwórz listę obecności');
                        addListSvg.setAttribute('data-placement', 'bottom');
                        addListSvg.setAttribute('data-trigger', 'hover');
                        addListSvg.setAttribute('data-toggle', 'popover');
                        addListSvg.setAttribute('data-html', 'true');
                        $(addListSvg).popover();

                        addListSvg.appendChild(addListPath);

                        const addListLink = document.createElement('a');
                        addListLink.appendChild(addListSvg);
                        addListLink.type = 'button';
                        addListLink.setAttribute("onclick", `createAttendanceList(event_id='${lesson.lesson_id}');`);

                        attendanceListCell.appendChild(addListLink);
                    }
                    lessonRow.appendChild(attendanceListCell);
                }


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


function open_months_url() {
    let urlParams = new URLSearchParams(window.location.search);
    openedMonths = urlParams.get('opened_months');
    console.log('openedMonths -> ' + openedMonths);
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

let lessonsLoaded = false;
let selected_year_div = document.getElementById("selected-year");
let nextYearBTn = document.getElementById("nextYearBTn");
let prevYearBtn = document.getElementById("prevYearBtn");


const delay = (delayInms) => {
    return new Promise(resolve => setTimeout(resolve, delayInms));
};


function generate_lessons() {
    if (!lessonsLoaded) {
        get_lessons(recordId)
        lessonsLoaded = true;
    }
}

document.addEventListener("DOMContentLoaded", function () {
    let urlParams = new URLSearchParams(window.location.search);

    let selected_year = urlParams.get('selected_year');
    if (!selected_year) {
        const current_year = new Date().getFullYear();
        selected_year = current_year;
        addParamToURL('selected_year', current_year)
    }
    selected_year_div.innerHTML = selected_year


    const tab = urlParams.get('tab');
    if (tab !== undefined) {
        if (tab === 'Lessons' && !lessonsLoaded) {
            generate_lessons();
        }
    }
})

function setNextYear() {
    setQueryYear(1);
}

function setPrevYear() {
    setQueryYear(-1);
}

function setQueryYear(value) {
    selected_year_div.innerHTML = parseInt(selected_year_div.innerHTML) + value;
    const currentURL = window.location.href;
    let urlSearchParams = new URLSearchParams(window.location.search);
    urlSearchParams.set('selected_year', selected_year_div.innerHTML);
    urlSearchParams.set('opened_months', '');
    window.history.pushState({}, document.title, '?' + urlSearchParams.toString());
    get_lessons(recordId);

    // window.location.href = currentURL.split('?')[0] + '?' + urlSearchParams.toString();

}

function setQueryYearNow() {
    selected_year_div.innerHTML = new Date().getFullYear();

    const currentURL = window.location.href;
    let urlSearchParams = new URLSearchParams(window.location.search);
    urlSearchParams.set('selected_year', selected_year_div.innerHTML);
    window.history.pushState({}, document.title, '?' + urlSearchParams.toString());
    get_lessons(recordId);

    // window.location.href = currentURL.split('?')[0] + '?' + urlSearchParams.toString();
}

function toggleDetails(element) {
    let detailsRow = element.parentElement.nextElementSibling;
    if (detailsRow.classList.contains('details')) {
        if (detailsRow.style.maxHeight === 0) {
            // detailsRow.style.display = 'table-row';
            detailsRow.style.maxHeight = 1000 + 'px';
        } else {
            detailsRow.style.maxHeight = '0px';

        }
    }
}

async function refreshOpenedMonths() {
    let delayres = await delay(1000);
    let divElements = document.querySelectorAll('[id^="collaps_"]');
    console.log('refreshing months')
    openedMonths = [];
    divElements.forEach(function (div) {
        let monthNumber = div.id.split('_')[1];
        if (div.classList.contains('show')) {
            openedMonths.push(monthNumber);
            console.log('checking ' + monthNumber);
        }
    });

    let urlParams = new URLSearchParams(window.location.search);
    urlParams.set('opened_months', openedMonths.join(','));
    window.history.replaceState({}, '', window.location.pathname + '?' + urlParams.toString());
}

document.getElementById('repeating_createLesson').addEventListener("change", function () {
    if (!document.getElementById('repeating_createLesson').checked) {
        document.getElementById('lessonDate_endSeries_div').classList.add('d-none');
        document.getElementById('lessonDate_endSeries').value = null;
    } else {
        document.getElementById('lessonDate_endSeries_div').classList.remove('d-none');
    }
});

function calculateTimeDifference(startTime, endTime) {
    // Parsowanie godzin na obiekty Date
    const start = new Date(`1970-01-01T${startTime}:00`);
    const end = new Date(`1970-01-01T${endTime}:00`);

    // Obliczenie r\u00F3\u017Cnicy w milisekundach
    const differenceInMilliseconds = end - start;

    // Konwersja milisekund na minuty
    const differenceInMinutes = differenceInMilliseconds / (1000 * 60);

    return differenceInMinutes;
}

function createAttendanceList(event_id) {
    addInformAlert("Tworzenie listy obecności...");

    const formData = new FormData();
    formData.append("event_id", event_id);
    formData.append("group_id", recordId);
    fetch("/crm_api/create-attendance-list/", {
        method: 'POST',
        headers: {
            'X-Requested-With': 'XMLHttpRequest',
            'X-CSRFToken': document.getElementById('attendance_list_form').querySelector('[name=csrfmiddlewaretoken]').value
        },
        body: formData
    })
        .then(response => response.json())
        .then(data => {
            if (data.status) {
                console.log("CHANGE ICON")
                const iconTochange = document.getElementById(`at-${event_id}`);
                iconTochange.removeChild(iconTochange.firstChild);
                $('.popover').remove();

                iconTochange.appendChild(attendanceListIcon(data.attendance_list_id));
            }
            handleResponse(data);
        })
        .catch(error => {
            console.error('Error:', error);
            alert('Wystąpił błąd przy tworzeniu listy obecności.');
        });
}

function attendanceListIcon(attendance_list_id) {
    const listSvg = document.createElementNS('http://www.w3.org/2000/svg', 'svg');
    const listPath = document.createElementNS(
        'http://www.w3.org/2000/svg',
        'path'
    );
    listSvg.setAttribute('fill', 'none');
    listSvg.setAttribute('viewBox', '0 0 24 24');
    listSvg.setAttribute('stroke', 'currentColor');
    listSvg.setAttribute('stroke-width', '1.5');
    listSvg.setAttribute('width', '18px');

    listPath.setAttribute('d', 'M9 12h3.75M9 15h3.75M9 18h3.75m3 .75H18a2.25 2.25 0 0 0 2.25-2.25V6.108c0-1.135-.845-2.098-1.976-2.192a48.424 48.424 0 0 0-1.123-.08m-5.801 0c-.065.21-.1.433-.1.664 0 .414.336.75.75.75h4.5a.75.75 0 0 0 .75-.75 2.25 2.25 0 0 0-.1-.664m-5.8 0A2.251 2.251 0 0 1 13.5 2.25H15c1.012 0 1.867.668 2.15 1.586m-5.8 0c-.376.023-.75.05-1.124.08C9.095 4.01 8.25 4.973 8.25 6.108V8.25m0 0H4.875c-.621 0-1.125.504-1.125 1.125v11.25c0 .621.504 1.125 1.125 1.125h9.75c.621 0 1.125-.504 1.125-1.125V9.375c0-.621-.504-1.125-1.125-1.125H8.25ZM6.75 12h.008v.008H6.75V12Zm0 3h.008v.008H6.75V15Zm0 3h.008v.008H6.75V18Z');
    listPath.setAttribute('stroke-linecap', 'round');
    listPath.setAttribute('stroke-linejoin', 'round');

    listSvg.setAttribute('data-content', 'Otwórz listę obecności');
    listSvg.setAttribute('data-placement', 'bottom');
    listSvg.setAttribute('data-trigger', 'hover');
    listSvg.setAttribute('data-toggle', 'popover');
    listSvg.setAttribute('data-html', 'true');
    $(listSvg).popover();


    listSvg.appendChild(listPath);

    const addListLink = document.createElement('a');
    addListLink.appendChild(listSvg);
    addListLink.setAttribute("href", `/attendancelist/${attendance_list_id}`);

    return addListLink;
}