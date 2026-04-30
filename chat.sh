curl -X POST "http://127.0.0.1:8000/api/chat" \
  -H "accept: application/json" \
  -H "Content-Type: application/json" \
  -d '{
    "model": "qwen3.5:4b",
    "messages": [
      {
        "role": "system",
        "content": "You are a db-query assistant for a school. Use db schema and db-query tool to give appropriate answers.\n\nSchema:\n\nCREATE TABLE IF NOT EXISTS classes (\n    id SERIAL PRIMARY KEY,\n    class_name VARCHAR(20) NOT NULL,\n    section VARCHAR(10),\n    academic_year VARCHAR(9) NOT NULL\n);\n\nCREATE TABLE IF NOT EXISTS students (\n    id SERIAL PRIMARY KEY,\n    roll_number VARCHAR(20) NOT NULL UNIQUE,\n    first_name VARCHAR(100) NOT NULL,\n    last_name VARCHAR(100),\n    date_of_birth DATE,\n    gender VARCHAR(10),\n    parent_mail varchar(100) NOT NULL,\n    class_id INT REFERENCES classes(id) ON DELETE CASCADE,\n    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP\n);\n\nCREATE TABLE IF NOT EXISTS attendance (\n    id SERIAL PRIMARY KEY,\n    student_id INT REFERENCES students(id) ON DELETE CASCADE,\n    attendance_date DATE NOT NULL,\n    status VARCHAR(10) CHECK (status IN ('Present', 'Absent')),\n    UNIQUE(student_id, attendance_date)\n);\n\nCREATE TABLE IF NOT EXISTS subjects (\n    id SERIAL PRIMARY KEY,\n    subject_name VARCHAR(100) NOT NULL,\n    class_id INT REFERENCES classes(id) ON DELETE CASCADE\n);\n\nCREATE TABLE IF NOT EXISTS exams (\n    id SERIAL PRIMARY KEY,\n    exam_name VARCHAR(100) NOT NULL,\n    class_id INT REFERENCES classes(id) ON DELETE CASCADE,\n    start_date DATE,\n    end_date DATE,\n    total_marks INT NOT NULL\n);\n\nCREATE TABLE IF NOT EXISTS results (\n    id SERIAL PRIMARY KEY,\n    student_id INT REFERENCES students(id) ON DELETE CASCADE,\n    exam_id INT REFERENCES exams(id) ON DELETE CASCADE,\n    subject_id INT REFERENCES subjects(id) ON DELETE CASCADE,\n    marks_obtained INT NOT NULL,\n    UNIQUE(student_id, exam_id, subject_id)\n);\n\nCREATE TABLE IF NOT EXISTS departments (\n    id SERIAL PRIMARY KEY,\n    dept_name VARCHAR(80) NOT NULL UNIQUE\n);\n\nCREATE TYPE emp_type AS ENUM ('teacher','clerk','admin','principal');\n\nCREATE TABLE IF NOT EXISTS employees (\n    id SERIAL PRIMARY KEY,\n    emp_id VARCHAR(20) NOT NULL UNIQUE,\n    first_name VARCHAR(100) NOT NULL,\n    last_name VARCHAR(100),\n    email VARCHAR(100) NOT NULL,\n    emp_type emp_type NOT NULL,\n    dept_id INT REFERENCES departments(id) ON DELETE SET NULL\n);"
      },
      {
        "role": "user",
        "content": "count no. of male and female students"
      }
    ],
    "think": false,
    "stream": false,
    "options": {
      "temperature": 0.7,
      "top_p": 0.9
    }
  }'