curl -X POST "http://127.0.0.1:8000/api/chat" \
  -H "accept: application/json" \
  -H "Content-Type: application/json" \
  -d '{
    "model": "qwen3.5:4b",
    "messages": [
      {
        "role": "system",
        "content": "You are a db-query assistant for a school. Use db schema and db-query tool to give appropriate answers.\n\nSchema:\n\n CREATE TABLE IF NOT EXISTS classes( id SERIAL PRIMARY KEY, class_name VARCHAR(20) NOT NULL, section VARCHAR(10), academic_year VARCHAR(9) NOT NULL); CREATE TABLE IF NOT EXISTS students ( id SERIAL PRIMARY KEY, roll_number VARCHAR(20) NOT NULL UNIQUE, first_name VARCHAR(100) NOT NULL, last_name VARCHAR(100), date_of_birth DATE, gender VARCHAR(10), parent_mail varchar(100) NOT NULL, class_id INT REFERENCES classes(id) ON DELETE CASCADE, created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ); CREATE TABLE IF NOT EXISTS attendance ( id SERIAL PRIMARY KEY, student_id INT REFERENCES students(id) ON DELETE CASCADE, attendance_date DATE NOT NULL, status VARCHAR(10) CHECK (status IN ('Present', 'Absent')), UNIQUE(student_id, attendance_date) ); CREATE TABLE IF NOT EXISTS subjects ( id SERIAL PRIMARY KEY, subject_name VARCHAR(100) NOT NULL, class_id INT REFERENCES classes(id) ON DELETE CASCADE ); CREATE TABLE IF NOT EXISTS exams ( id SERIAL PRIMARY KEY, exam_name VARCHAR(100) NOT NULL, class_id INT REFERENCES classes(id) ON DELETE CASCADE, start_date DATE, end_date DATE, total_marks INT NOT NULL ); CREATE TABLE IF NOT EXISTS results ( id SERIAL PRIMARY KEY, student_id INT REFERENCES students(id) ON DELETE CASCADE, exam_id INT REFERENCES exams(id) ON DELETE CASCADE, subject_id INT REFERENCES subjects(id) ON DELETE CASCADE, marks_obtained INT NOT NULL, UNIQUE(student_id, exam_id, subject_id) ); CREATE TABLE IF NOT EXISTS departments ( id SERIAL PRIMARY KEY, dept_name VARCHAR(80) NOT NULL UNIQUE ); CREATE TYPE emp_type AS ENUM ( 'teacher', 'clerk', 'admin', 'principal' ); CREATE TABLE IF NOT EXISTS employees ( id SERIAL PRIMARY KEY, emp_id VARCHAR(20) NOT NULL UNIQUE, first_name VARCHAR(100) NOT NULL, last_name VARCHAR(100), email VARCHAR(100) NOT NULL, emp_type emp_type NOT NULL, dept_id INT REFERENCES departments(id) ON DELETE SET NULL ); CREATE OR REPLACE FUNCTION get_student_attendance(p_student_id INT) RETURNS TABLE ( student_id INT, first_name VARCHAR, last_name VARCHAR, total_days INT, present_days INT, attendance_percentage FLOAT ) AS $$ BEGIN RETURN QUERY SELECT s.id, s.first_name, s.last_name, COUNT(a.*)::INT AS total_days, COUNT(*) FILTER (WHERE a.status = 'Present')::INT AS present_days, ( COUNT(*) FILTER (WHERE a.status = 'Present') * 100.0 / NULLIF(COUNT(a.*), 0) )::FLOAT AS attendance_percentage FROM students s LEFT JOIN attendance a ON s.id = a.student_id WHERE s.id = p_student_id GROUP BY s.id, s.first_name, s.last_name; END; $$ LANGUAGE plpgsql; CREATE OR REPLACE FUNCTION get_low_attendance_students(threshold FLOAT) RETURNS TABLE ( student_id INT, first_name VARCHAR, last_name VARCHAR, attendance_percentage FLOAT ) AS $$ SELECT s.id, s.first_name, s.last_name, ( COUNT(*) FILTER (WHERE a.status = 'Present') * 100.0 / COUNT(*) )::FLOAT AS attendance_percentage FROM students s JOIN attendance a ON s.id = a.student_id GROUP BY s.id, s.first_name, s.last_name HAVING ( COUNT(*) FILTER (WHERE a.status = 'Present') * 100.0 / COUNT(*) )::FLOAT < threshold; $$ LANGUAGE sql;"
      },
      {
        "role": "system",
        "content": "--- EXAMPLE FROM KNOWLEDGE BASE(SIMILAR QUERY MATCHED) --- User Intent: Retrieve students whose attendance percentage is below a given threshold. Canonical User Query Pattern: - fetch students with less than X% attendance - students below X percent attendance - list students having poor attendance under X% Preferred Execution Strategy: USE STORED FUNCTION (MANDATORY) Function to use: get_low_attendance_students(threshold) Execution Rule: - DO NOT write SQL for attendance calculation - DO NOT join students and attendance manually - ALWAYS delegate computation to the function Reason: - Encapsulates business logic for attendance calculation - Ensures consistent percentage computation - Reduces query complexity and errors Mapping: User threshold X% → function argument threshold Final Action: CALL: get_low_attendance_students(X)"
      },
      {
        "role": "user",
        "content": "fetch students with less than 90% attendance"
      }
    ],
    "think": false,
    "stream": false,
    "options": {
      "temperature": 0.0,
      "top_p": 0.9
    }
  }'

# curl -X POST "http://127.0.0.1:8000/api/chat" \
#   -H "accept: application/json" \
#   -H "Content-Type: application/json" \
#   -d '{
#     "model": "qwen3.5:4b",
#     "messages": [
#       {
#         "role": "system",
#         "content": "You are a db-query assistant for a school. Use db schema and db-query tool to give appropriate answers.\n\nSchema:\n\n CREATE TABLE IF NOT EXISTS classes( id SERIAL PRIMARY KEY, class_name VARCHAR(20) NOT NULL, section VARCHAR(10), academic_year VARCHAR(9) NOT NULL); CREATE TABLE IF NOT EXISTS students ( id SERIAL PRIMARY KEY, roll_number VARCHAR(20) NOT NULL UNIQUE, first_name VARCHAR(100) NOT NULL, last_name VARCHAR(100), date_of_birth DATE, gender VARCHAR(10), parent_mail varchar(100) NOT NULL, class_id INT REFERENCES classes(id) ON DELETE CASCADE, created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ); CREATE TABLE IF NOT EXISTS attendance ( id SERIAL PRIMARY KEY, student_id INT REFERENCES students(id) ON DELETE CASCADE, attendance_date DATE NOT NULL, status VARCHAR(10) CHECK (status IN ('Present', 'Absent')), UNIQUE(student_id, attendance_date) ); CREATE TABLE IF NOT EXISTS subjects ( id SERIAL PRIMARY KEY, subject_name VARCHAR(100) NOT NULL, class_id INT REFERENCES classes(id) ON DELETE CASCADE ); CREATE TABLE IF NOT EXISTS exams ( id SERIAL PRIMARY KEY, exam_name VARCHAR(100) NOT NULL, class_id INT REFERENCES classes(id) ON DELETE CASCADE, start_date DATE, end_date DATE, total_marks INT NOT NULL ); CREATE TABLE IF NOT EXISTS results ( id SERIAL PRIMARY KEY, student_id INT REFERENCES students(id) ON DELETE CASCADE, exam_id INT REFERENCES exams(id) ON DELETE CASCADE, subject_id INT REFERENCES subjects(id) ON DELETE CASCADE, marks_obtained INT NOT NULL, UNIQUE(student_id, exam_id, subject_id) ); CREATE TABLE IF NOT EXISTS departments ( id SERIAL PRIMARY KEY, dept_name VARCHAR(80) NOT NULL UNIQUE ); CREATE TYPE emp_type AS ENUM ( 'teacher', 'clerk', 'admin', 'principal' ); CREATE TABLE IF NOT EXISTS employees ( id SERIAL PRIMARY KEY, emp_id VARCHAR(20) NOT NULL UNIQUE, first_name VARCHAR(100) NOT NULL, last_name VARCHAR(100), email VARCHAR(100) NOT NULL, emp_type emp_type NOT NULL, dept_id INT REFERENCES departments(id) ON DELETE SET NULL ); CREATE OR REPLACE FUNCTION get_student_attendance(p_student_id INT) RETURNS TABLE ( student_id INT, first_name VARCHAR, last_name VARCHAR, total_days INT, present_days INT, attendance_percentage FLOAT ) AS $$ BEGIN RETURN QUERY SELECT s.id, s.first_name, s.last_name, COUNT(a.*)::INT AS total_days, COUNT(*) FILTER (WHERE a.status = 'Present')::INT AS present_days, ( COUNT(*) FILTER (WHERE a.status = 'Present') * 100.0 / NULLIF(COUNT(a.*), 0) )::FLOAT AS attendance_percentage FROM students s LEFT JOIN attendance a ON s.id = a.student_id WHERE s.id = p_student_id GROUP BY s.id, s.first_name, s.last_name; END; $$ LANGUAGE plpgsql; CREATE OR REPLACE FUNCTION get_low_attendance_students(threshold FLOAT) RETURNS TABLE ( student_id INT, first_name VARCHAR, last_name VARCHAR, attendance_percentage FLOAT ) AS $$ SELECT s.id, s.first_name, s.last_name, ( COUNT(*) FILTER (WHERE a.status = 'Present') * 100.0 / COUNT(*) )::FLOAT AS attendance_percentage FROM students s JOIN attendance a ON s.id = a.student_id GROUP BY s.id, s.first_name, s.last_name HAVING ( COUNT(*) FILTER (WHERE a.status = 'Present') * 100.0 / COUNT(*) )::FLOAT < threshold; $$ LANGUAGE sql;"
#       },
#       {
#         "role": "system",
#         "content": "--- EXAMPLE FROM KNOWLEDGE BASE(MATCHED INTENT) --- User Intent: Retrieve top N overall student performers across all exams based on total marks Canonical Query Patterns: - fetch top students by total marks - list highest scoring students overall - student leaderboard across all exams - top N performers overall MANDATORY EXECUTION RULE: - ALWAYS use dynamic_select_query tool - DO NOT use stored functions - DO NOT delegate to call_db_function - MUST aggregate marks using SUM(results.marks_obtained) - MUST group by student fields only - MUST sort by total_marks DESC - MUST apply LIMIT based on user input (N) TOOL MAPPING (STRICT): table: \"results\" joins: [ { \"type\": \"INNER\", \"table\": \"students\", \"on\": \"students.id = results.student_id\" } ] projection: [ \"students.id AS student_id\", \"students.first_name\", \"students.last_name\", \"SUM(results.marks_obtained) AS total_marks\" ] group_by: [ \"students.id\", \"students.first_name\", \"students.last_name\" ] order_by: [ \"total_marks DESC\" ] limit: N (user-defined, e.g. 2) EXECUTION STRATEGY: - Perform aggregation directly using dynamic_select_query only - No stored procedures or functions allowed - Compute total_marks using SUM aggregation - Return students sorted by performance descending OUTPUT GOAL: Return top N students ranked by total marks across all exams"
#       },
#       {
#         "role": "user",
#         "content": "I want to see top 3 performers in exams"
#       }
#     ],
#     "think": false,
#     "stream": false,
#     "options": {
#       "temperature": 0.0,
#       "top_p": 0.9
#     }
#   }'