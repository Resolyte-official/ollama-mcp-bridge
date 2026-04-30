--
-- PostgreSQL database dump
--

\restrict aIViCYVlcMC0PgWto4XftYFqLAuqD8vTwgaUdb6Ot4rikI2Do57GuUyMH6zJ2xM

-- Dumped from database version 18.1
-- Dumped by pg_dump version 18.1

SET statement_timeout = 0;
SET lock_timeout = 0;
SET idle_in_transaction_session_timeout = 0;
SET transaction_timeout = 0;
SET client_encoding = 'UTF8';
SET standard_conforming_strings = on;
SELECT pg_catalog.set_config('search_path', '', false);
SET check_function_bodies = false;
SET xmloption = content;
SET client_min_messages = warning;
SET row_security = off;

--
-- Data for Name: classes; Type: TABLE DATA; Schema: public; Owner: mcpserver
--

COPY public.classes (id, class_name, section, academic_year) FROM stdin;
1	7th	A	2025-2026
2	8th	A	2025-2026
\.


--
-- Data for Name: students; Type: TABLE DATA; Schema: public; Owner: mcpserver
--

COPY public.students (id, roll_number, first_name, last_name, date_of_birth, gender, parent_mail, class_id, created_at) FROM stdin;
1	7A01	Aarav	Sharma	2013-05-10	Male	aarav.sharma.parent@example.com	1	2026-02-27 13:27:29.458339
2	7A02	Diya	Verma	2013-08-21	Female	diya.verma.parent@example.com	1	2026-02-27 13:27:29.458339
3	7A03	Kabir	Singh	2013-02-14	Male	kabir.singh.parent@example.com	1	2026-02-27 13:27:29.458339
4	7A04	Meera	Joshi	2013-11-30	Female	meera.joshi.parent@example.com	1	2026-02-27 13:27:29.458339
5	7A05	Rohan	Gupta	2013-07-19	Male	rohan.gupta.parent@example.com	1	2026-02-27 13:27:29.458339
6	8B11	Vikram	Mahajan	2011-03-26	Male	vikram.mahajan.parent@example.com	2	2026-03-01 17:20:04.997179
7	8B06	Jasmine	Raina	2012-08-03	Female	jasmine.raina.parent@example.com	2	2026-03-01 17:20:04.997179
\.


--
-- Data for Name: attendance; Type: TABLE DATA; Schema: public; Owner: mcpserver
--

COPY public.attendance (id, student_id, attendance_date, status) FROM stdin;
1	1	2025-09-01	Present
2	1	2025-09-02	Present
3	1	2025-09-03	Present
4	1	2025-09-04	Present
5	1	2025-09-05	Present
6	1	2025-09-06	Present
7	1	2025-09-07	Present
8	1	2025-09-08	Present
9	1	2025-09-09	Present
10	1	2025-09-10	Absent
11	2	2025-09-01	Present
12	2	2025-09-02	Present
13	2	2025-09-03	Present
14	2	2025-09-04	Present
15	2	2025-09-05	Present
16	2	2025-09-06	Present
17	2	2025-09-07	Present
18	2	2025-09-08	Present
19	2	2025-09-09	Present
20	2	2025-09-10	Present
21	3	2025-09-01	Present
22	3	2025-09-02	Present
23	3	2025-09-03	Absent
24	3	2025-09-04	Present
25	3	2025-09-05	Absent
26	3	2025-09-06	Present
27	3	2025-09-07	Absent
28	3	2025-09-08	Present
29	3	2025-09-09	Absent
30	3	2025-09-10	Present
31	4	2025-09-01	Present
32	4	2025-09-02	Present
33	4	2025-09-03	Present
34	4	2025-09-04	Absent
35	4	2025-09-05	Present
36	4	2025-09-06	Present
37	4	2025-09-07	Present
38	4	2025-09-08	Absent
39	4	2025-09-09	Present
40	4	2025-09-10	Present
41	5	2025-09-01	Absent
42	5	2025-09-02	Present
43	5	2025-09-03	Absent
44	5	2025-09-04	Absent
45	5	2025-09-05	Present
46	5	2025-09-06	Absent
47	5	2025-09-07	Absent
48	5	2025-09-08	Present
49	5	2025-09-09	Absent
50	5	2025-09-10	Present
\.


--
-- Data for Name: departments; Type: TABLE DATA; Schema: public; Owner: mcpserver
--

COPY public.departments (id, dept_name) FROM stdin;
1	Mathematics
2	Science
3	English
4	Administration
\.


--
-- Data for Name: employees; Type: TABLE DATA; Schema: public; Owner: mcpserver
--

COPY public.employees (id, emp_id, first_name, last_name, email, emp_type, dept_id) FROM stdin;
2	EMP002	Anita	Sharma	anita.sharma@admin.school.com	admin	4
3	EMP003	Vikram	Mehta	vikram.mehta@admin.school.com	admin	4
4	EMP004	Pooja	Gupta	pooja.gupta@admin.school.com	clerk	4
5	EMP005	Suresh	Raina	suresh.raina@admin.school.com	clerk	4
6	EMP006	Amit	Singh	amit.singh@math.school.com	teacher	1
7	EMP007	Neha	Verma	neha.verma@science.school.com	teacher	2
8	EMP008	Rohit	Joshi	rohit.joshi@english.school.com	teacher	3
1	EMP001	Rajesh	Kumar	rajesh.kumar@school.com	principal	4
\.


--
-- Data for Name: exams; Type: TABLE DATA; Schema: public; Owner: mcpserver
--

COPY public.exams (id, exam_name, class_id, start_date, end_date, total_marks) FROM stdin;
1	Mid Sem	1	2025-09-15	2025-09-20	100
\.


--
-- Data for Name: subjects; Type: TABLE DATA; Schema: public; Owner: mcpserver
--

COPY public.subjects (id, subject_name, class_id) FROM stdin;
1	Mathematics	1
2	Science	1
3	English	1
4	History	1
\.


--
-- Data for Name: results; Type: TABLE DATA; Schema: public; Owner: mcpserver
--

COPY public.results (id, student_id, exam_id, subject_id, marks_obtained) FROM stdin;
1	1	1	1	78
2	1	1	2	82
3	1	1	3	74
4	1	1	4	69
5	2	1	1	91
6	2	1	2	88
7	2	1	3	95
8	2	1	4	90
9	3	1	1	45
10	3	1	2	52
11	3	1	3	48
12	3	1	4	50
13	4	1	1	67
14	4	1	2	72
15	4	1	3	70
16	4	1	4	65
17	5	1	1	30
18	5	1	2	40
19	5	1	3	35
20	5	1	4	38
\.


--
-- Data for Name: schema_migrations; Type: TABLE DATA; Schema: public; Owner: mcpserver
--

COPY public.schema_migrations (version, dirty) FROM stdin;
1	f
\.


--
-- Name: attendance_id_seq; Type: SEQUENCE SET; Schema: public; Owner: mcpserver
--

SELECT pg_catalog.setval('public.attendance_id_seq', 50, true);


--
-- Name: classes_id_seq; Type: SEQUENCE SET; Schema: public; Owner: mcpserver
--

SELECT pg_catalog.setval('public.classes_id_seq', 2, true);


--
-- Name: departments_id_seq; Type: SEQUENCE SET; Schema: public; Owner: mcpserver
--

SELECT pg_catalog.setval('public.departments_id_seq', 4, true);


--
-- Name: employees_id_seq; Type: SEQUENCE SET; Schema: public; Owner: mcpserver
--

SELECT pg_catalog.setval('public.employees_id_seq', 8, true);


--
-- Name: exams_id_seq; Type: SEQUENCE SET; Schema: public; Owner: mcpserver
--

SELECT pg_catalog.setval('public.exams_id_seq', 1, true);


--
-- Name: results_id_seq; Type: SEQUENCE SET; Schema: public; Owner: mcpserver
--

SELECT pg_catalog.setval('public.results_id_seq', 20, true);


--
-- Name: students_id_seq; Type: SEQUENCE SET; Schema: public; Owner: mcpserver
--

SELECT pg_catalog.setval('public.students_id_seq', 7, true);


--
-- Name: subjects_id_seq; Type: SEQUENCE SET; Schema: public; Owner: mcpserver
--

SELECT pg_catalog.setval('public.subjects_id_seq', 4, true);


--
-- PostgreSQL database dump complete
--

\unrestrict aIViCYVlcMC0PgWto4XftYFqLAuqD8vTwgaUdb6Ot4rikI2Do57GuUyMH6zJ2xM
