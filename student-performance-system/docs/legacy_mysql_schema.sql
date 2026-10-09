CREATE DATABASE IF NOT EXISTS student_performance;
USE student_performance;

CREATE TABLE users (
  id INT AUTO_INCREMENT PRIMARY KEY,
  name VARCHAR(100) NOT NULL,
  email VARCHAR(100) UNIQUE NOT NULL,
  password VARCHAR(255) NOT NULL,
  role ENUM('admin','teacher','student') NOT NULL,
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE classes (
  id INT AUTO_INCREMENT PRIMARY KEY,
  class_name VARCHAR(30) NOT NULL,
  section VARCHAR(10)
);

CREATE TABLE teachers (
  id INT AUTO_INCREMENT PRIMARY KEY,
  user_id INT NOT NULL,
  department VARCHAR(100),
  FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
);

CREATE TABLE students (
  id INT AUTO_INCREMENT PRIMARY KEY,
  user_id INT NOT NULL,
  class_id INT,
  roll_no VARCHAR(20),
  FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
  FOREIGN KEY (class_id) REFERENCES classes(id)
);

CREATE TABLE subjects (
  id INT AUTO_INCREMENT PRIMARY KEY,
  subject_name VARCHAR(100) NOT NULL,
  class_id INT,
  teacher_id INT,
  FOREIGN KEY (class_id) REFERENCES classes(id),
  FOREIGN KEY (teacher_id) REFERENCES teachers(id)
);

CREATE TABLE marks (
  id INT AUTO_INCREMENT PRIMARY KEY,
  student_id INT NOT NULL,
  subject_id INT NOT NULL,
  exam_score DECIMAL(5,2),
  assignment_score DECIMAL(5,2),
  exam_type VARCHAR(30),
  date DATE,
  FOREIGN KEY (student_id) REFERENCES students(id) ON DELETE CASCADE,
  FOREIGN KEY (subject_id) REFERENCES subjects(id)
);

CREATE TABLE attendance (
  id INT AUTO_INCREMENT PRIMARY KEY,
  student_id INT NOT NULL,
  date DATE NOT NULL,
  status ENUM('present','absent') NOT NULL,
  FOREIGN KEY (student_id) REFERENCES students(id) ON DELETE CASCADE
);

CREATE TABLE study_habits (
  id INT AUTO_INCREMENT PRIMARY KEY,
  student_id INT NOT NULL,
  hours_studied_weekly INT,
  sleep_hours DECIMAL(3,1),
  tutoring_sessions INT,
  physical_activity INT,
  extracurricular ENUM('Yes','No'),
  motivation_level ENUM('Low','Medium','High'),
  parental_involvement ENUM('Low','Medium','High'),
  access_to_resources ENUM('Low','Medium','High'),
  internet_access ENUM('Yes','No'),
  family_income ENUM('Low','Medium','High'),
  teacher_quality ENUM('Low','Medium','High'),
  updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  FOREIGN KEY (student_id) REFERENCES students(id) ON DELETE CASCADE
);

CREATE TABLE predictions (
  id INT AUTO_INCREMENT PRIMARY KEY,
  student_id INT NOT NULL,
  predicted_level ENUM('High','Medium','Low'),
  predicted_score DECIMAL(5,2),
  probabilities JSON,
  model_version VARCHAR(20),
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  FOREIGN KEY (student_id) REFERENCES students(id) ON DELETE CASCADE
);

CREATE TABLE recommendations (
  id INT AUTO_INCREMENT PRIMARY KEY,
  student_id INT NOT NULL,
  subject_id INT,
  type VARCHAR(30),
  priority ENUM('High','Medium','Low'),
  tip TEXT,
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  FOREIGN KEY (student_id) REFERENCES students(id) ON DELETE CASCADE,
  FOREIGN KEY (subject_id) REFERENCES subjects(id)
);
