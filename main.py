import sys
from PyQt5.QtWidgets import QApplication, QMainWindow, QPushButton, QVBoxLayout, QWidget
from student_window import StudentWindow
from discipline_window import DisciplineWindow
from teacher_window import TeacherWindow  
from university_division_window import UniversityDivisionWindow
from scholarship_window import ScholarshipWindow
from job_title_window import JobTitleWindow
from direction_of_preparation_window import DirectionOfPreparationWindow
from certification_window import CertificationWindow
from audience_window import AudienceWindow
from logger import logger

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Университетская БД")
        self.setGeometry(200, 200, 300, 250)

        layout = QVBoxLayout()

        btn_student = QPushButton("Студенты")
        btn_student.clicked.connect(self.open_students)
        layout.addWidget(btn_student)

        btn_discipline = QPushButton("Дисциплины")
        btn_discipline.clicked.connect(self.open_disciplines)
        layout.addWidget(btn_discipline)

        btn_teacher = QPushButton("Преподаватели") 
        btn_teacher.clicked.connect(self.open_teachers)
        layout.addWidget(btn_teacher)

        btn_division = QPushButton("Подразделения ВУЗа")
        btn_division.clicked.connect(self.open_divisions)
        layout.addWidget(btn_division)

        btn_scholarship = QPushButton("Стипендии")
        btn_scholarship.clicked.connect(self.open_scholarships)
        layout.addWidget(btn_scholarship)

        btn_job_title = QPushButton("Должности")
        btn_job_title.clicked.connect(self.open_job_titles)
        layout.addWidget(btn_job_title)

        btn_direction = QPushButton("Направления подготовки")
        btn_direction.clicked.connect(self.open_directions)
        layout.addWidget(btn_direction)

        btn_certification = QPushButton("Аттестации")
        btn_certification.clicked.connect(self.open_certifications)
        layout.addWidget(btn_certification)

        btn_audience = QPushButton("Аудитории")
        btn_audience.clicked.connect(self.open_audience)
        layout.addWidget(btn_audience)

        container = QWidget()
        container.setLayout(layout)
        self.setCentralWidget(container)

    def open_students(self):
        self.student_window = StudentWindow()
        self.student_window.show()
        logger.info("Открыто окно студентов")

    def open_disciplines(self):
        self.discipline_window = DisciplineWindow()
        self.discipline_window.show()
        logger.info("Открыто окно дисциплин")

    def open_teachers(self):  
        self.teacher_window = TeacherWindow()
        self.teacher_window.show()
        logger.info("Открыто окно преподавателей")
    
    def open_divisions(self):
        self.division_window = UniversityDivisionWindow()
        self.division_window.show()
        logger.info("Открыто окно подразделений ВУЗа")
    
    def open_scholarships(self):
        self.scholarship_window = ScholarshipWindow()
        self.scholarship_window.show()
        logger.info("Открыто окно стипендий")

    def open_job_titles(self):
        self.job_title_window = JobTitleWindow()
        self.job_title_window.show()
        logger.info("Открыто окно должностей")
    
    def open_directions(self):
        self.direction_window = DirectionOfPreparationWindow()
        self.direction_window.show()
        logger.info("Открыто окно направлений подготовки")
    
    def open_certifications(self):
        self.certification_window = CertificationWindow()
        self.certification_window.show()
        logger.info("Открыто окно аттестаций")
    
    def open_audience(self):
        self.audience_window = AudienceWindow()
        self.audience_window.show()
        logger.info("Открыто окно аудиторий")


if __name__ == '__main__':
    app = QApplication(sys.argv)
    main_win = MainWindow()
    main_win.show()
    sys.exit(app.exec_())
