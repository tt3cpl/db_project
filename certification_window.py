from PyQt5.QtWidgets import (
<<<<<<< HEAD
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
    QComboBox,
=======
    QWidget, QVBoxLayout, QPushButton, QTableWidget, QTableWidgetItem,
    QLineEdit, QHBoxLayout, QMessageBox, QDialog, QFormLayout, QDialogButtonBox
>>>>>>> d8d353c4260bb55e6728d0a2be9f2b8092c1954a
)
from db import get_connection
from logger import logger


class CertificationWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Таблица: Аттестации")
<<<<<<< HEAD
        self.setGeometry(100, 100, 900, 400)
=======
        self.setGeometry(100, 100, 700, 350)
>>>>>>> d8d353c4260bb55e6728d0a2be9f2b8092c1954a

        self.layout = QVBoxLayout()
        self.setLayout(self.layout)

        self.search_box = QLineEdit()
<<<<<<< HEAD
        self.search_box.setPlaceholderText("Поиск по фамилии студента...")
=======
        self.search_box.setPlaceholderText("Поиск по типу аттестации...")
>>>>>>> d8d353c4260bb55e6728d0a2be9f2b8092c1954a
        self.search_box.textChanged.connect(self.search_certifications)
        self.layout.addWidget(self.search_box)

        self.table = QTableWidget()
        self.layout.addWidget(self.table)

        btns = QHBoxLayout()
<<<<<<< HEAD
        for name, handler in [
            ("Обновить", self.load_data),
            ("Добавить", self.add_record),
            ("Редактировать", self.edit_record),
            ("Удалить", self.delete_record),
        ]:
            btn = QPushButton(name)
            btn.clicked.connect(handler)
            btns.addWidget(btn)
=======

        refresh_btn = QPushButton("Обновить")
        refresh_btn.clicked.connect(self.load_data)
        btns.addWidget(refresh_btn)

        add_btn = QPushButton("Добавить")
        add_btn.clicked.connect(self.add_certification)
        btns.addWidget(add_btn)

        edit_btn = QPushButton("Редактировать")
        edit_btn.clicked.connect(self.edit_certification)
        btns.addWidget(edit_btn)

        delete_btn = QPushButton("Удалить")
        delete_btn.clicked.connect(self.delete_certification)
        btns.addWidget(delete_btn)
>>>>>>> d8d353c4260bb55e6728d0a2be9f2b8092c1954a

        self.layout.addLayout(btns)
        self.load_data()

    def load_data(self):
        try:
            conn = get_connection()
            cur = conn.cursor()
<<<<<<< HEAD
            cur.execute(
                """
                SELECT c."ID_certification", s."Surname", d."Discipline_name",
                       c."Grade", c."Certification_type", c."Try",
                       c."ID_student", c."ID_disciplines"
                FROM public."Certification" c
                JOIN public."Student" s ON c."ID_student" = s."ID_student"
                JOIN public."Discipline" d ON c."ID_disciplines" = d."ID_disciplines"
                ORDER BY s."Surname"
            """
            )
            rows = cur.fetchall()
            self.table.setRowCount(len(rows))
            self.table.setColumnCount(8)
            self.table.setHorizontalHeaderLabels(
                [
                    "ID",
                    "Фамилия студента",
                    "Дисциплина",
                    "Оценка",
                    "Тип аттестации",
                    "Попытка",
                    "ID студента",
                    "ID дисциплины",
                ]
            )
            for i, row in enumerate(rows):
                for j, val in enumerate(row):
                    if j == 3:  # Grade
                        val = CertificationDialog.REVERSE_GRADE_MAP.get(val, str(val))
=======
            cur.execute('SELECT * FROM public."Certification" ORDER BY "ID_certification"')
            rows = cur.fetchall()
            self.table.setRowCount(len(rows))
            self.table.setColumnCount(5)
            self.table.setHorizontalHeaderLabels([
                "ID", "Оценка", "ID дисциплины", "Тип аттестации", "ID студента"
            ])
            for i, row in enumerate(rows):
                for j, val in enumerate(row):
>>>>>>> d8d353c4260bb55e6728d0a2be9f2b8092c1954a
                    self.table.setItem(i, j, QTableWidgetItem(str(val)))
            cur.close()
            conn.close()
            logger.info("Загружены данные аттестаций")
        except Exception as e:
<<<<<<< HEAD
            logger.error(f"Ошибка загрузки аттестаций: {e}")
=======
            logger.error(f"Ошибка загрузки данных: {e}")
>>>>>>> d8d353c4260bb55e6728d0a2be9f2b8092c1954a
            QMessageBox.critical(self, "Ошибка", str(e))

    def search_certifications(self):
        keyword = self.search_box.text().strip()
        try:
            conn = get_connection()
            cur = conn.cursor()
<<<<<<< HEAD
            cur.execute(
                """
                SELECT c."ID_certification", s."Surname", d."Discipline_name",
                       c."Grade", c."Certification_type", c."Try",
                       c."ID_student", c."ID_disciplines"
                FROM public."Certification" c
                JOIN public."Student" s ON c."ID_student" = s."ID_student"
                JOIN public."Discipline" d ON c."ID_disciplines" = d."ID_disciplines"
                WHERE s."Surname" ILIKE %s
                ORDER BY s."Surname"
            """,
                (f"%{keyword}%",),
            )
=======
            cur.execute("""
                SELECT * FROM public."Certification"
                WHERE "Certification_type" ILIKE %s
                ORDER BY "ID_certification"
            """, (f"%{keyword}%",))
>>>>>>> d8d353c4260bb55e6728d0a2be9f2b8092c1954a
            rows = cur.fetchall()
            self.table.setRowCount(len(rows))
            for i, row in enumerate(rows):
                for j, val in enumerate(row):
<<<<<<< HEAD
                    if j == 3:
                        val = CertificationDialog.REVERSE_GRADE_MAP.get(val, str(val))
                    self.table.setItem(i, j, QTableWidgetItem(str(val)))
            cur.close()
            conn.close()
=======
                    self.table.setItem(i, j, QTableWidgetItem(str(val)))
            cur.close()
            conn.close()
            logger.info(f"Поиск аттестаций: {keyword}")
>>>>>>> d8d353c4260bb55e6728d0a2be9f2b8092c1954a
        except Exception as e:
            logger.error(f"Ошибка поиска: {e}")
            QMessageBox.critical(self, "Ошибка", str(e))

<<<<<<< HEAD
    def add_record(self):
        dialog = CertificationDialog()
        if dialog.exec_() == QDialog.Accepted:
            try:
                data = dialog.get_data()
                conn = get_connection()
                cur = conn.cursor()
                cur.execute(
                    """
                    INSERT INTO public."Certification" 
                        ("Grade", "ID_disciplines", "Certification_type", "ID_student", "Try")
                    VALUES (%s, %s, %s, %s, %s)
                """,
                    data,
                )
=======
    def add_certification(self):
        dialog = CertificationDialog()
        if dialog.exec_() == QDialog.Accepted:
            try:
                conn = get_connection()
                cur = conn.cursor()
                cur.execute("""
                    INSERT INTO public."Certification" ("Grade", "ID_disciplines", "Certification_type", "ID_student")
                    VALUES (%s, %s, %s, %s)
                """, dialog.get_data())
>>>>>>> d8d353c4260bb55e6728d0a2be9f2b8092c1954a
                conn.commit()
                cur.close()
                conn.close()
                self.load_data()
<<<<<<< HEAD
                logger.info("Добавлена запись аттестации")
=======
                logger.info("Добавлена аттестация")
>>>>>>> d8d353c4260bb55e6728d0a2be9f2b8092c1954a
            except Exception as e:
                logger.error(f"Ошибка добавления: {e}")
                QMessageBox.critical(self, "Ошибка", str(e))

<<<<<<< HEAD
    def edit_record(self):
=======
    def edit_certification(self):
>>>>>>> d8d353c4260bb55e6728d0a2be9f2b8092c1954a
        selected = self.table.currentRow()
        if selected < 0:
            QMessageBox.warning(self, "Внимание", "Выберите запись для редактирования")
            return

<<<<<<< HEAD
        record_id = self.table.item(selected, 0).text()
        grade_str = self.table.item(selected, 3).text()
        cert_type = self.table.item(selected, 4).text()
        attempt = self.table.item(selected, 5).text()
        student_id = self.table.item(selected, 6).text()
        discipline_id = self.table.item(selected, 7).text()

        dialog = CertificationDialog(
            grade_str, discipline_id, cert_type, student_id, attempt
        )
        if dialog.exec_() == QDialog.Accepted:
            try:
                data = dialog.get_data()
                conn = get_connection()
                cur = conn.cursor()
                cur.execute(
                    """
                    UPDATE public."Certification"
                    SET "Grade" = %s, "ID_disciplines" = %s,
                        "Certification_type" = %s, "ID_student" = %s,
                        "Try" = %s
                    WHERE "ID_certification" = %s
                """,
                    (*data, record_id),
                )
=======
        certification_id = self.table.item(selected, 0).text()
        current_data = [self.table.item(selected, i).text() for i in range(1, 5)]

        dialog = CertificationDialog(*current_data)
        if dialog.exec_() == QDialog.Accepted:
            try:
                conn = get_connection()
                cur = conn.cursor()
                cur.execute("""
                    UPDATE public."Certification"
                    SET "Grade" = %s, "ID_disciplines" = %s, "Certification_type" = %s, "ID_student" = %s
                    WHERE "ID_certification" = %s
                """, (*dialog.get_data(), certification_id))
>>>>>>> d8d353c4260bb55e6728d0a2be9f2b8092c1954a
                conn.commit()
                cur.close()
                conn.close()
                self.load_data()
<<<<<<< HEAD
                logger.info(f"Обновлена аттестация ID={record_id}")
            except Exception as e:
                logger.error(f"Ошибка обновления: {e}")
                QMessageBox.critical(self, "Ошибка", str(e))

    def delete_record(self):
=======
                logger.info(f"Отредактирована аттестация ID={certification_id}")
            except Exception as e:
                logger.error(f"Ошибка редактирования: {e}")
                QMessageBox.critical(self, "Ошибка", str(e))

    def delete_certification(self):
>>>>>>> d8d353c4260bb55e6728d0a2be9f2b8092c1954a
        selected = self.table.currentRow()
        if selected < 0:
            QMessageBox.warning(self, "Внимание", "Выберите запись для удаления")
            return

<<<<<<< HEAD
        record_id = self.table.item(selected, 0).text()
        confirm = QMessageBox.question(
            self,
            "Подтверждение",
            f"Удалить запись ID {record_id}?",
            QMessageBox.Yes | QMessageBox.No,
        )
=======
        certification_id = self.table.item(selected, 0).text()
        confirm = QMessageBox.question(
            self, "Подтверждение",
            f"Удалить аттестацию ID {certification_id}?",
            QMessageBox.Yes | QMessageBox.No
        )

>>>>>>> d8d353c4260bb55e6728d0a2be9f2b8092c1954a
        if confirm == QMessageBox.Yes:
            try:
                conn = get_connection()
                cur = conn.cursor()
<<<<<<< HEAD
                cur.execute(
                    'DELETE FROM public."Certification" WHERE "ID_certification" = %s',
                    (record_id,),
                )
=======
                cur.execute('DELETE FROM public."Certification" WHERE "ID_certification" = %s', (certification_id,))
>>>>>>> d8d353c4260bb55e6728d0a2be9f2b8092c1954a
                conn.commit()
                cur.close()
                conn.close()
                self.load_data()
<<<<<<< HEAD
                logger.info(f"Аттестация ID={record_id} удалена")
=======
                logger.info(f"Удалена аттестация ID={certification_id}")
>>>>>>> d8d353c4260bb55e6728d0a2be9f2b8092c1954a
            except Exception as e:
                logger.error(f"Ошибка удаления: {e}")
                QMessageBox.critical(self, "Ошибка", str(e))


class CertificationDialog(QDialog):
<<<<<<< HEAD
    GRADE_MAP = {"2FX": 2, "3F": 3, "3D": 4, "4C": 5, "4B": 6, "5A": 7}
    REVERSE_GRADE_MAP = {v: k for k, v in GRADE_MAP.items()}
    ATTEMPT_NUMBERS = ["1", "2", "3"]

    def __init__(
        self,
        grade="",
        discipline_id="",
        cert_type="",
        student_id="",
        attempt_number="1",
    ):
        super().__init__()
        self.setWindowTitle("Аттестация")
        layout = QFormLayout(self)

        self.grade_box = QComboBox()
        self.grade_box.addItems(self.GRADE_MAP.keys())
        if grade in self.GRADE_MAP:
            self.grade_box.setCurrentText(grade)

        self.cert_type_box = QLineEdit()
        self.cert_type_box.setReadOnly(True)

        self.attempt_box = QComboBox()
        self.attempt_box.addItems(self.ATTEMPT_NUMBERS)
        if attempt_number in self.ATTEMPT_NUMBERS:
            self.attempt_box.setCurrentText(attempt_number)

        self.student_box = QComboBox()
        self.discipline_box = QComboBox()
        self.discipline_id_map = {}

        self.load_students(student_id)
        self.load_disciplines(discipline_id)
        self.discipline_box.currentIndexChanged.connect(self.update_cert_type)

        layout.addRow("Оценка:", self.grade_box)
        layout.addRow("Тип аттестации:", self.cert_type_box)
        layout.addRow("Номер попытки:", self.attempt_box)
        layout.addRow("Студент:", self.student_box)
        layout.addRow("Дисциплина:", self.discipline_box)
=======
    def __init__(self, grade="", id_discipline="", cert_type="", id_student=""):
        super().__init__()
        self.setWindowTitle("Данные аттестации")
        layout = QFormLayout(self)

        self.grade_input = QLineEdit(grade)
        self.discipline_input = QLineEdit(id_discipline)
        self.cert_type_input = QLineEdit(cert_type)
        self.student_input = QLineEdit(id_student)

        layout.addRow("Оценка:", self.grade_input)
        layout.addRow("ID дисциплины:", self.discipline_input)
        layout.addRow("Тип аттестации:", self.cert_type_input)
        layout.addRow("ID студента:", self.student_input)
>>>>>>> d8d353c4260bb55e6728d0a2be9f2b8092c1954a

        buttons = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        buttons.accepted.connect(self.accept)
        buttons.rejected.connect(self.reject)
        layout.addWidget(buttons)

<<<<<<< HEAD
    def load_students(self, selected_id=""):
        conn = get_connection()
        cur = conn.cursor()
        cur.execute(
            'SELECT "ID_student", "Surname" FROM public."Student" ORDER BY "Surname"'
        )
        for sid, surname in cur.fetchall():
            self.student_box.addItem(f"{surname} (ID={sid})", sid)
            if str(sid) == selected_id:
                self.student_box.setCurrentIndex(self.student_box.count() - 1)
        cur.close()
        conn.close()

    def load_disciplines(self, selected_id=""):
        conn = get_connection()
        cur = conn.cursor()
        cur.execute(
            'SELECT "ID_disciplines", "Discipline_name", "Type_of_certification" FROM public."Discipline" ORDER BY "Discipline_name"'
        )
        for did, name, cert_type in cur.fetchall():
            self.discipline_box.addItem(f"{name} (ID={did})", did)
            self.discipline_id_map[did] = cert_type
            if str(did) == selected_id:
                self.discipline_box.setCurrentIndex(self.discipline_box.count() - 1)
        cur.close()
        conn.close()
        self.update_cert_type()

    def update_cert_type(self):
        did = self.discipline_box.currentData()
        if did in self.discipline_id_map:
            self.cert_type_box.setText(self.discipline_id_map[did])
        else:
            self.cert_type_box.setText("")

    def get_data(self):
        grade_value = self.GRADE_MAP[self.grade_box.currentText()]
        return (
            grade_value,
            self.discipline_box.currentData(),
            self.cert_type_box.text(),
            self.student_box.currentData(),
            int(self.attempt_box.currentText()),
=======
    def get_data(self):
        return (
            int(self.grade_input.text()),
            int(self.discipline_input.text()),
            self.cert_type_input.text(),
            int(self.student_input.text())
>>>>>>> d8d353c4260bb55e6728d0a2be9f2b8092c1954a
        )
