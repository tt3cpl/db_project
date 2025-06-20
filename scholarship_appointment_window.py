from PyQt5.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QPushButton,
    QTableWidget,
    QTableWidgetItem,
    QLineEdit,
    QHBoxLayout,
    QMessageBox,
    QDialog,
    QFormLayout,
    QDialogButtonBox,
    QDateEdit,
    QComboBox,
    QTextEdit,
)
from PyQt5.QtCore import QDate
from db import get_connection
from logger import logger


class ScholarshipAppointmentWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Назначение стипендии")
        self.setGeometry(100, 100, 900, 500)

        self.layout = QVBoxLayout()
        self.setLayout(self.layout)

        self.search_box = QLineEdit()
        self.search_box.setPlaceholderText("Поиск по студенту или типу стипендии...")
        self.search_box.textChanged.connect(self.search_records)
        self.layout.addWidget(self.search_box)

        self.table = QTableWidget()
        self.layout.addWidget(self.table)

        btns = QHBoxLayout()

        refresh_btn = QPushButton("Обновить")
        refresh_btn.clicked.connect(self.load_data)
        btns.addWidget(refresh_btn)

        add_btn = QPushButton("Добавить")
        add_btn.clicked.connect(self.add_record)
        btns.addWidget(add_btn)

        edit_btn = QPushButton("Редактировать")
        edit_btn.clicked.connect(self.edit_record)
        btns.addWidget(edit_btn)

        delete_btn = QPushButton("Удалить")
        delete_btn.clicked.connect(self.delete_record)
        btns.addWidget(delete_btn)

        self.layout.addLayout(btns)

        self.load_data()

    def load_data(self):
        try:
            conn = get_connection()
            cur = conn.cursor()
            cur.execute(
                """
                SELECT sa."ID_scholarship_assignment", sa."from", sa."by", sa."Base",
                       sa."ID_student", s."Surname", s."Name",
                       sa."ID_scholarships", sch."Type_of_scholarship", sch."Size"
                FROM public."Scholarship_Appointment" sa
                JOIN public."Student" s ON sa."ID_student" = s."ID_student"
                JOIN public."Scholarship" sch ON sa."ID_scholarships" = sch."ID_scholarships"
                ORDER BY sa."from" DESC
            """
            )
            rows = cur.fetchall()
            self.table.setRowCount(len(rows))
            self.table.setColumnCount(10)
            self.table.setHorizontalHeaderLabels(
                [
                    "ID назначения",
                    "Дата назначения",
                    "Дата окончания",
                    "Основание",
                    "ID студента",
                    "Фамилия",
                    "Имя",
                    "ID стипендии",
                    "Тип стипендии",
                    "Размер",
                ]
            )
            for i, row in enumerate(rows):
                for j, val in enumerate(row):
                    self.table.setItem(i, j, QTableWidgetItem(str(val)))
            cur.close()
            conn.close()
            logger.info("Загружены данные назначения стипендий")
        except Exception as e:
            logger.error(f"Ошибка загрузки назначения стипендий: {e}")
            QMessageBox.critical(self, "Ошибка", str(e))

    def search_records(self):
        keyword = self.search_box.text().strip()
        try:
            conn = get_connection()
            cur = conn.cursor()
            cur.execute(
                """
                SELECT sa."ID_scholarship_assignment", sa."from", sa."by", sa."Base",
                       sa."ID_student", s."Surname", s."Name",
                       sa."ID_scholarships", sch."Type_of_scholarship", sch."Size"
                FROM public."Scholarship_Appointment" sa
                JOIN public."Student" s ON sa."ID_student" = s."ID_student"
                JOIN public."Scholarship" sch ON sa."ID_scholarships" = sch."ID_scholarships"
                WHERE s."Surname" ILIKE %s OR s."Name" ILIKE %s OR sch."Type_of_scholarship" ILIKE %s
                ORDER BY sa."from" DESC
            """,
                (f"%{keyword}%", f"%{keyword}%", f"%{keyword}%"),
            )
            rows = cur.fetchall()
            self.table.setRowCount(len(rows))
            for i, row in enumerate(rows):
                for j, val in enumerate(row):
                    self.table.setItem(i, j, QTableWidgetItem(str(val)))
            cur.close()
            conn.close()
            logger.info(f"Поиск назначения стипендий: {keyword}")
        except Exception as e:
            logger.error(f"Ошибка поиска назначения стипендий: {e}")
            QMessageBox.critical(self, "Ошибка", str(e))

    def add_record(self):
        dialog = ScholarshipAppointmentDialog()
        if dialog.exec_() == QDialog.Accepted:
            try:
                data = dialog.get_data()
                conn = get_connection()
                cur = conn.cursor()
                cur.execute(
                    """
                    INSERT INTO public."Scholarship_Appointment"
                    ("by", "ID_student", "from", "Base", "ID_scholarships")
                    VALUES (%s, %s, %s, %s, %s)
                """,
                    data,
                )
                conn.commit()
                cur.close()
                conn.close()
                self.load_data()
                logger.info("Добавлена запись назначения стипендии")
            except Exception as e:
                logger.error(f"Ошибка добавления назначения стипендии: {e}")
                QMessageBox.critical(self, "Ошибка", str(e))

    def edit_record(self):
        selected = self.table.currentRow()
        if selected < 0:
            QMessageBox.warning(self, "Внимание", "Выберите запись для редактирования")
            return

        record_id = self.table.item(selected, 0).text()

        try:
            conn = get_connection()
            cur = conn.cursor()
            cur.execute(
                """
                SELECT "by", "ID_student", "from", "Base", "ID_scholarships"
                FROM public."Scholarship_Appointment"
                WHERE "ID_scholarship_assignment" = %s
            """,
                (record_id,),
            )
            row = cur.fetchone()
            if not row:
                QMessageBox.warning(self, "Внимание", "Запись не найдена")
                return
            cur.close()
            conn.close()
        except Exception as e:
            logger.error(
                f"Ошибка получения данных для редактирования назначения стипендии: {e}"
            )
            QMessageBox.critical(self, "Ошибка", str(e))
            return

        dialog = ScholarshipAppointmentDialog(*row, editing=True)
        if dialog.exec_() == QDialog.Accepted:
            try:
                data = dialog.get_data()
                conn = get_connection()
                cur = conn.cursor()
                cur.execute(
                    """
                    UPDATE public."Scholarship_Appointment"
                    SET "by" = %s, "ID_student" = %s, "from" = %s, "Base" = %s, "ID_scholarships" = %s
                    WHERE "ID_scholarship_assignment" = %s
                """,
                    (*data, record_id),
                )
                conn.commit()
                cur.close()
                conn.close()
                self.load_data()
                logger.info(
                    f"Отредактирована запись назначения стипендии ID={record_id}"
                )
            except Exception as e:
                logger.error(f"Ошибка редактирования назначения стипендии: {e}")
                QMessageBox.critical(self, "Ошибка", str(e))

    def delete_record(self):
        selected = self.table.currentRow()
        if selected < 0:
            QMessageBox.warning(self, "Внимание", "Выберите запись для удаления")
            return

        record_id = self.table.item(selected, 0).text()
        confirm = QMessageBox.question(
            self,
            "Подтверждение",
            f"Удалить запись с ID {record_id}?",
            QMessageBox.Yes | QMessageBox.No,
        )
        if confirm == QMessageBox.Yes:
            try:
                conn = get_connection()
                cur = conn.cursor()
                cur.execute(
                    'DELETE FROM public."Scholarship_Appointment" WHERE "ID_scholarship_assignment" = %s',
                    (record_id,),
                )
                conn.commit()
                cur.close()
                conn.close()
                self.load_data()
                logger.info(f"Удалена запись назначения стипендии ID={record_id}")
            except Exception as e:
                logger.error(f"Ошибка удаления назначения стипендии: {e}")
                QMessageBox.critical(self, "Ошибка", str(e))


class ScholarshipAppointmentDialog(QDialog):
    def __init__(
        self,
        end_date=None,
        student_id=None,
        assignment_date=None,
        base=None,
        scholarship_id=None,
        editing=False,
    ):
        super().__init__()
        self.setWindowTitle("Назначение стипендии")
        layout = QFormLayout(self)

        self.end_date_edit = QDateEdit()
        self.end_date_edit.setCalendarPopup(True)
        if end_date:
            self.end_date_edit.setDate(QDate.fromString(str(end_date), "yyyy-MM-dd"))
        else:
            self.end_date_edit.setDate(QDate.currentDate())

        self.assignment_date_edit = QDateEdit()
        self.assignment_date_edit.setCalendarPopup(True)
        if assignment_date:
            self.assignment_date_edit.setDate(
                QDate.fromString(str(assignment_date), "yyyy-MM-dd")
            )
        else:
            self.assignment_date_edit.setDate(QDate.currentDate())

        self.student_box = QComboBox()
        self.load_students(student_id)

        self.scholarship_box = QComboBox()
        self.load_scholarships(scholarship_id)

        self.base_edit = QTextEdit()
        if base:
            self.base_edit.setPlainText(base)

        layout.addRow("Дата окончания:", self.end_date_edit)
        layout.addRow("Студент:", self.student_box)
        layout.addRow("Дата назначения:", self.assignment_date_edit)
        layout.addRow("Основание:", self.base_edit)
        layout.addRow("Стипендия:", self.scholarship_box)

        buttons = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        buttons.accepted.connect(self.accept)
        buttons.rejected.connect(self.reject)
        layout.addWidget(buttons)

    def load_students(self, selected_id=None):
        try:
            conn = get_connection()
            cur = conn.cursor()
            cur.execute(
                'SELECT "ID_student", "Surname", "Name" FROM public."Student" ORDER BY "Surname"'
            )
            students = cur.fetchall()
            self.student_box.clear()
            for id_, surname, name in students:
                self.student_box.addItem(f"{id_} - {surname} {name}", id_)
            if selected_id:
                index = self.student_box.findData(selected_id)
                if index != -1:
                    self.student_box.setCurrentIndex(index)
            cur.close()
            conn.close()
        except Exception as e:
            logger.error(f"Ошибка загрузки студентов: {e}")

    def load_scholarships(self, selected_id=None):
        try:
            conn = get_connection()
            cur = conn.cursor()
            cur.execute(
                'SELECT "ID_scholarships", "Type_of_scholarship" FROM public."Scholarship" ORDER BY "Type_of_scholarship"'
            )
            scholarships = cur.fetchall()
            self.scholarship_box.clear()
            for id_, typ in scholarships:
                self.scholarship_box.addItem(f"{id_} - {typ}", id_)
            if selected_id:
                index = self.scholarship_box.findData(selected_id)
                if index != -1:
                    self.scholarship_box.setCurrentIndex(index)
            cur.close()
            conn.close()
        except Exception as e:
            logger.error(f"Ошибка загрузки стипендий: {e}")

    def get_data(self):
        end_date = self.end_date_edit.date().toString("yyyy-MM-dd")
        student_id = self.student_box.currentData()
        assignment_date = self.assignment_date_edit.date().toString("yyyy-MM-dd")
        base = self.base_edit.toPlainText()
        scholarship_id = self.scholarship_box.currentData()
        return (end_date, student_id, assignment_date, base, scholarship_id)
