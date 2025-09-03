CREATE OR REPLACE FUNCTION generate_lesson_events()
RETURNS TRIGGER AS $$
DECLARE
    curr_date DATE;
    stop_date DATE;
    calculated_stop_date DATE;
    target_month INT;
    target_year INT;
    last_day INT;
    generated_id TEXT;
BEGIN
    -- Ustawienie daty poczatkowej na wartosc lesson_date z nowego rekordu
    curr_date := NEW.lesson_date;

    -- Obliczanie daty zakonczenia (na 6 miesiecy do przodu)
    target_month := (EXTRACT(MONTH FROM NEW.lesson_date)::INT + 5) % 12 + 1;
    target_year := EXTRACT(YEAR FROM NEW.lesson_date)::INT + ((EXTRACT(MONTH FROM NEW.lesson_date)::INT + 5) / 12);

    SELECT EXTRACT(DAY FROM (DATE_TRUNC('MONTH', make_date(target_year, target_month, 1) + INTERVAL '1 month') - INTERVAL '1 day'))::INT
    INTO last_day;

    calculated_stop_date := make_date(target_year, target_month, last_day);

    -- Jesli użytkownik podal wsasna date koncowa to wybierz wczesniejsza
    IF NEW.series_end_date IS NOT NULL THEN
        stop_date := LEAST(calculated_stop_date, NEW.series_end_date);
    ELSE
        stop_date := calculated_stop_date;
    END IF;

    -- Petla generujaca wydarzenia
    WHILE curr_date <= stop_date LOOP
        generated_id := '0EV' || gen_random_uuid();
        INSERT INTO crm_event (
            id,
            event_type,
            lesson_definition_id,
            status,
            event_date,
            original_lesson_datetime,
            start_time,
            end_time,
            duration,
            teacher_id,
            location_id
        )
        VALUES (
            generated_id,
            'lesson',
            NEW.id,
            'zaplanowana',
            curr_date,
            curr_date + NEW.start_time,
            NEW.start_time,
            (NEW.start_time + (NEW.duration || ' minutes')::INTERVAL)::TIME,
            NEW.duration,
            NEW.teacher_id,
            NEW.location_id
        );

        -- Jesli to seria dodaj tydzien a jesli nie to zakoncz
        EXIT WHEN NOT NEW.is_series;
        curr_date := curr_date + INTERVAL '1 week';
    END LOOP;

    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

DROP TRIGGER IF EXISTS trg_generate_lesson_events ON crm_lessondefinition;

CREATE TRIGGER trg_generate_lesson_events
AFTER INSERT ON crm_lessondefinition
FOR EACH ROW
EXECUTE FUNCTION generate_lesson_events();


-- Obsluga generowania asocjacji miedzy lista obecnosci a uczniami

CREATE OR REPLACE FUNCTION create_attendance_list_students()
RETURNS TRIGGER AS $$
BEGIN
    INSERT INTO "crm_attendanceliststudent" (id, attendance_list_id, student_id, attendance_status)
    SELECT
        gen_random_uuid(),
        NEW.id,
        gs.student_id,
        'Obecnosc'
    FROM "crm_groupstudent" gs
    WHERE gs.group_id = NEW.group_id;

    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- Trigger wywolujacy procedure po dodaniu nowej listy obecnosci
CREATE TRIGGER trg_create_attendance_list_students
AFTER INSERT ON "crm_attendancelist"
FOR EACH ROW
EXECUTE FUNCTION create_attendance_list_students();

