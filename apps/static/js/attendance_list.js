
let edit_btn = $('#attendanceListEdit');
let save_btn = $('#attendanceListSave');
let cancel_btn = $('#attendanceListCancel');

const preventDefaultListener = function (e) {
  e.preventDefault();
};



function editAttendanceList(){
    window.addEventListener('beforeunload', preventDefaultListener);

    let radios = document.querySelectorAll('input[type="radio"]');
    radios.forEach(radio => {
        radio.disabled = false;
    });

    let buttons = document.querySelectorAll('.attendance-select-all-btn');
    buttons.forEach(button => {
        button.style.visibility = 'visible';
    });

    edit_btn.hide();
    save_btn.show();
    cancel_btn.show();


}

function cancelEditAttendanceList() {
    if (confirm('Chcesz anulować?') !== true)
        return;
    window.removeEventListener('beforeunload', preventDefaultListener);
    window.location = window.location
}
function leaveEditMode() {

    window.removeEventListener('beforeunload', preventDefaultListener);

    let radios = document.querySelectorAll('input[type="radio"]');
    radios.forEach(radio => {
        radio.disabled = true;
    });

    let buttons = document.querySelectorAll('.attendance-select-all-btn');
    buttons.forEach(button => {
        button.style.visibility = 'hidden';
    });

    edit_btn.show();
    save_btn.hide();
    cancel_btn.hide();
}

function getAttendanceList(){
    let attendanceData = [];

    let rows = document.querySelectorAll('#attendance_student_tbody tr');

    rows.forEach(row => {
        let AttendanceStudentId = row.querySelector('input[type="radio"]').name.split('_')[1];

        let status = row.querySelector('input[type="radio"]:checked').value;

        // Dodaj do tablicy JSON
        attendanceData.push({
            "attendance_list_student_id": AttendanceStudentId,
            "status": status
        });
    });

    return attendanceData;
}

function saveAttendanceList() {

    let attendance_list_students = getAttendanceList();
    console.log(attendance_list_students);
    $.ajax({
        url: '/crm_api/save-attendance-list/',
        type: 'POST',
        data: {
            csrfmiddlewaretoken: $(csrf_token).val(),
            attendance_list_students: JSON.stringify(attendance_list_students),
            attendance_list_id: attendance_list_id
        },
        dataType: 'json',
        success: function (response) {
            if (response.status) {
                leaveEditMode();
            }
            handleResponse(response);
        },
        error: function (error) {
            console.error('B\u0142\u0105d zapisywania listy', error);
        }
    });
}

function setRadioValueForAll(value) {
    let rows = document.querySelectorAll('#attendance_student_tbody tr');

    rows.forEach(row => {
        let radios = row.querySelectorAll('input[type="radio"]');

        radios.forEach(radio => {
            if (radio.value === value) {
                radio.checked = true;
            }
        });
    });
}