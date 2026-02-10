-- Add Professors
INSERT INTO courses (course_name, credits) VALUES 
('Intro to Databases', 3),
('Advanced Web Dev', 4),
('Data Structures', 3),
('Machine Learning 101', 4);

-- Add Students
INSERT INTO students (first_name, last_name, email) VALUES 
('Alice', 'Johnson', 'alice.j@university.edu'),
('Bob', 'Smith', 'bob.s@university.edu'),
('Charlie', 'Davis', 'charlie.d@university.edu'),
('Diana', 'Prince', 'diana.p@university.edu');

-- Add Enrollments (Linking Students to Courses)
INSERT INTO enrollments (student_id, course_id, grade, semester) VALUES 
(1, 1, 'A', 'Fall 2025'),
(1, 2, 'B+', 'Fall 2025'),
(2, 1, 'B', 'Fall 2025'),
(3, 3, 'A-', 'Spring 2026'),
(4, 4, 'A', 'Spring 2026'),
(4, 1, 'C', 'Spring 2026');