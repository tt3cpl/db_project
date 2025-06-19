import sys
from PyQt5.QtWidgets import QApplication, QMainWindow, QPushButton, QVBoxLayout, QWidget
from student_window import StudentWindow
from discipline_window import DisciplineWindow
<<<<<<< HEAD
from teacher_window import TeacherWindow
=======
from teacher_window import TeacherWindow  
>>>>>>> d8d353c4260bb55e6728d0a2be9f2b8092c1954a
from university_division_window import UniversityDivisionWindow
from scholarship_window import ScholarshipWindow
from job_title_window import JobTitleWindow
from direction_of_preparation_window import DirectionOfPreparationWindow
from certification_window import CertificationWindow
from audience_window import AudienceWindow
<<<<<<< HEAD
from op_window import OPWindow
from up_window import UPWindow
from discipline_in_up_window import DisciplineInUPWindow
from job_history_window import JobHistoryWindow
from schedule_window import ScheduleWindow
from group_window import GroupWindow
from student_learning_window import StudentLearningWindow
from session_schedule_window import SessionScheduleWindow
from scholarship_appointment_window import ScholarshipAppointmentWindow
from logger import logger


=======
from logger import logger

>>>>>>> d8d353c4260bb55e6728d0a2be9f2b8092c1954a
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

<<<<<<< HEAD
        btn_teacher = QPushButton("Преподаватели")
=======
        btn_teacher = QPushButton("Преподаватели") 
>>>>>>> d8d353c4260bb55e6728d0a2be9f2b8092c1954a
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

<<<<<<< HEAD
        btn_op = QPushButton("Образовательные программы")
        btn_op.clicked.connect(self.open_op)
        layout.addWidget(btn_op)

        btn_up = QPushButton("Учебные планы")
        btn_up.clicked.connect(self.open_up)
        layout.addWidget(btn_up)

        btn_discipline_in_up = QPushButton("Дисциплина в УП")
        btn_discipline_in_up.clicked.connect(self.open_discipline_in_up)
        layout.addWidget(btn_discipline_in_up)

        btn_job_history = QPushButton("История должностей преподавателей")
        btn_job_history.clicked.connect(self.open_job_history)
        layout.addWidget(btn_job_history)

        btn_schedule = QPushButton("Расписание")
        btn_schedule.clicked.connect(self.open_schedule)
        layout.addWidget(btn_schedule)

        btn_group = QPushButton("Группы")
        btn_group.clicked.connect(self.open_groups)
        layout.addWidget(btn_group)

        btn_student_learning = QPushButton("Обучающийся студент")
        btn_student_learning.clicked.connect(self.open_student_learning)
        layout.addWidget(btn_student_learning)

        btn_session_schedule = QPushButton("Расписание сессий")
        btn_session_schedule.clicked.connect(self.open_session_schedule)
        layout.addWidget(btn_session_schedule)

        btn_scholarship_appointment = QPushButton("Назначение стипендий")
        btn_scholarship_appointment.clicked.connect(self.open_scholarship_appointment)
        layout.addWidget(btn_scholarship_appointment)

=======
>>>>>>> d8d353c4260bb55e6728d0a2be9f2b8092c1954a
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

<<<<<<< HEAD
    def open_teachers(self):
        self.teacher_window = TeacherWindow()
        self.teacher_window.show()
        logger.info("Открыто окно преподавателей")

=======
    def open_teachers(self):  
        self.teacher_window = TeacherWindow()
        self.teacher_window.show()
        logger.info("Открыто окно преподавателей")
    
>>>>>>> d8d353c4260bb55e6728d0a2be9f2b8092c1954a
    def open_divisions(self):
        self.division_window = UniversityDivisionWindow()
        self.division_window.show()
        logger.info("Открыто окно подразделений ВУЗа")
<<<<<<< HEAD

=======
    
>>>>>>> d8d353c4260bb55e6728d0a2be9f2b8092c1954a
    def open_scholarships(self):
        self.scholarship_window = ScholarshipWindow()
        self.scholarship_window.show()
        logger.info("Открыто окно стипендий")

    def open_job_titles(self):
        self.job_title_window = JobTitleWindow()
        self.job_title_window.show()
        logger.info("Открыто окно должностей")
<<<<<<< HEAD

=======
    
>>>>>>> d8d353c4260bb55e6728d0a2be9f2b8092c1954a
    def open_directions(self):
        self.direction_window = DirectionOfPreparationWindow()
        self.direction_window.show()
        logger.info("Открыто окно направлений подготовки")
<<<<<<< HEAD

=======
    
>>>>>>> d8d353c4260bb55e6728d0a2be9f2b8092c1954a
    def open_certifications(self):
        self.certification_window = CertificationWindow()
        self.certification_window.show()
        logger.info("Открыто окно аттестаций")
<<<<<<< HEAD

=======
    
>>>>>>> d8d353c4260bb55e6728d0a2be9f2b8092c1954a
    def open_audience(self):
        self.audience_window = AudienceWindow()
        self.audience_window.show()
        logger.info("Открыто окно аудиторий")

<<<<<<< HEAD
    def open_op(self):
        self.op_window = OPWindow()
        self.op_window.show()
        logger.info("Открыто окно ОП")

    def open_up(self):
        self.up_window = UPWindow()
        self.up_window.show()
        logger.info("Открыто окно УП")

    def open_discipline_in_up(self):
        self.discipline_in_up_window = DisciplineInUPWindow()
        self.discipline_in_up_window.show()
        logger.info("Открыто окно дисциплин в УП")

    def open_job_history(self):
        self.job_history_window = JobHistoryWindow()
        self.job_history_window.show()
        logger.info("Открыто окно истории должностей преподавателей")

    def open_schedule(self):
        self.schedule_window = ScheduleWindow()
        self.schedule_window.show()
        logger.info("Открыто окно расписания")

    def open_groups(self):
        self.group_window = GroupWindow()
        self.group_window.show()
        logger.info("Открыто окно групп")

    def open_student_learning(self):
        self.student_learning_window = StudentLearningWindow()
        self.student_learning_window.show()
        logger.info("Открыто окно обучающегося студента")

    def open_session_schedule(self):
        self.session_schedule_window = SessionScheduleWindow()
        self.session_schedule_window.show()
        logger.info("Открыто окно расписания сессий")

    def open_scholarship_appointment(self):
        self.scholarship_appointment_window = ScholarshipAppointmentWindow()
        self.scholarship_appointment_window.show()
        logger.info("Открыто окно назначения стипендий")


if __name__ == "__main__":
=======

if __name__ == '__main__':
>>>>>>> d8d353c4260bb55e6728d0a2be9f2b8092c1954a
    app = QApplication(sys.argv)
    main_win = MainWindow()
    main_win.show()
    sys.exit(app.exec_())
