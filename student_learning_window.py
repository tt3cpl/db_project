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
)
from PyQt5.QtCore import QDate
from db import get_connection
from logger import logger


class StudentLearningWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Таблица: Обучающийся студент")
        self.setGeometry(100, 100, 900, 450)

        self.layout = QVBoxLayout()
        self.setLayout(self.layout)

        self.search_box = QLineEdit()
        self.search_box.setPlaceholderText("Поиск по фамилии студента...")
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
                SELECT sl."ID_student_learning", sl."from", sl."by",
                       sl."Status", sl."ID_groups", g."Group_numbers",
                       sl."ID_student", s."Surname", s."Name", s."Patronymic"
                FROM public."Student_learning" sl
                JOIN public."Group" g ON sl."ID_groups" = g."ID_group"
                JOIN public."Student" s ON sl."ID_student" = s."ID_student"
                ORDER BY sl."from"
            """
            )
            rows = cur.fetchall()
            self.table.setRowCount(len(rows))
            self.table.setColumnCount(10)
            self.table.setHorizontalHeaderLabels(
                [
                    "ID обучения",
                    "Дата начала",
                    "Дата окончания",
                    "Статус",
                    "ID группы",
                    "Номер группы",
                    "ID студента",
                    "Фамилия",
                    "Имя",
                    "Отчество",
                ]
            )
            for i, row in enumerate(rows):
                for j, val in enumerate(row):
                    self.table.setItem(i, j, QTableWidgetItem(str(val)))
            cur.close()
            conn.close()
            logger.info("Загружены данные обучающихся студентов")
        except Exception as e:
            logger.error(f"Ошибка загрузки данных обучающихся студентов: {e}")
            QMessageBox.critical(self, "Ошибка", str(e))

    def search_records(self):
        keyword = self.search_box.text().strip()
        try:
            conn = get_connection()
            cur = conn.cursor()
            cur.execute(
                """
                SELECT sl."ID_student_learning", sl."from", sl."by",
                       sl."Status", sl."ID_groups", g."Group_numbers",
                       sl."ID_student", s."Surname", s."Name", s."Patronymic"
                FROM public."Student_learning" sl
                JOIN public."Group" g ON sl."ID_groups" = g."ID_group"
                JOIN public."Student" s ON sl."ID_student" = s."ID_student"
                WHERE s."Surname" ILIKE %s
                ORDER BY sl."from"
            """,
                (f"%{keyword}%",),
            )
            rows = cur.fetchall()
            self.table.setRowCount(len(rows))
            for i, row in enumerate(rows):
                for j, val in enumerate(row):
                    self.table.setItem(i, j, QTableWidgetItem(str(val)))
            cur.close()
            conn.close()
            logger.info(f"Поиск обучающихся студентов: {keyword}")
        except Exception as e:
            logger.error(f"Ошибка поиска обучающихся студентов: {e}")
            QMessageBox.critical(self, "Ошибка", str(e))

    def add_record(self):
        dialog = StudentLearningDialog()
        if dialog.exec_() == QDialog.Accepted:
            try:
                data = dialog.get_data()
                conn = get_connection()
                cur = conn.cursor()
                cur.execute(
                    """
                    INSERT INTO public."Student_learning"
                    ("from", "by", "ID_groups", "Status", "ID_student")
                    VALUES (%s, %s, %s, %s, %s)
                """,
                    data,
                )
                conn.commit()
                cur.close()
                conn.close()
                self.load_data()
                logger.info("Добавлена запись обучающегося студента")
            except Exception as e:
                logger.error(f"Ошибка добавления обучающегося студента: {e}")
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
                SELECT "from", "by", "ID_groups", "Status", "ID_student"
                FROM public."Student_learning" WHERE "ID_student_learning" = %s
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
                f"Ошибка получения данных для редактирования обучающегося студента: {e}"
            )
            QMessageBox.critical(self, "Ошибка", str(e))
            return

        dialog = StudentLearningDialog(*row, editing=True)
        if dialog.exec_() == QDialog.Accepted:
            try:
                data = dialog.get_data()
                conn = get_connection()
                cur = conn.cursor()
                cur.execute(
                    """
                    UPDATE public."Student_learning"
                    SET "from" = %s, "by" = %s, "ID_groups" = %s, "Status" = %s, "ID_student" = %s
                    WHERE "ID_student_learning" = %s
                """,
                    (*data, record_id),
                )
                conn.commit()
                cur.close()
                conn.close()
                self.load_data()
                logger.info(
                    f"Отредактирована запись обучающегося студента ID={record_id}"
                )
            except Exception as e:
                logger.error(f"Ошибка редактирования обучающегося студента: {e}")
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
                    'DELETE FROM public."Student_learning" WHERE "ID_student_learning" = %s',
                    (record_id,),
                )
                conn.commit()
                cur.close()
                conn.close()
                self.load_data()
                logger.info(f"Удалена запись обучающегося студента ID={record_id}")
            except Exception as e:
                logger.error(f"Ошибка удаления обучающегося студента: {e}")
                QMessageBox.critical(self, "Ошибка", str(e))


class StudentLearningDialog(QDialog):
    STATUS_OPTIONS = [
        "Обучение",
        "Академический отпуск",
        "Отчислен ПСЖ",
        "Отчислен за неуспеваемость",
        "Диплом",
        "Отчислен по переводу",
    ]

    def __init__(
        self,
        from_date=None,
        by_date=None,
        group_id=None,
        status=None,
        student_id=None,
        editing=False,
    ):
        super().__init__()
        self.setWindowTitle("Обучающийся студент")
        layout = QFormLayout(self)

        self.from_date = QDateEdit()
        self.from_date.setCalendarPopup(True)
        if from_date:
            self.from_date.setDate(QDate.fromString(str(from_date), "yyyy-MM-dd"))
        else:
            self.from_date.setDate(QDate.currentDate())

        self.by_date = QDateEdit()
        self.by_date.setCalendarPopup(True)
        if by_date:
            self.by_date.setDate(QDate.fromString(str(by_date), "yyyy-MM-dd"))
        else:
            self.by_date.setDate(QDate.currentDate())

        self.group_box = QComboBox()
        self.load_groups(group_id)

        self.status_box = QComboBox()
        self.status_box.addItems(self.STATUS_OPTIONS)
        if status in self.STATUS_OPTIONS:
            self.status_box.setCurrentText(status)

        self.student_box = QComboBox()
        self.load_students(student_id)

        layout.addRow("Дата начала:", self.from_date)
        layout.addRow("Дата окончания:", self.by_date)
        layout.addRow("Группа:", self.group_box)
        layout.addRow("Статус:", self.status_box)
        layout.addRow("Студент:", self.student_box)

        buttons = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        buttons.accepted.connect(self.accept)
        buttons.rejected.connect(self.reject)
        layout.addRow(buttons)

    def load_groups(self, selected_id=None):
        try:
            conn = get_connection()
            cur = conn.cursor()
            cur.execute(
                'SELECT "ID_group", "Group_numbers" FROM public."Group" ORDER BY "Group_numbers"'
            )
            rows = cur.fetchall()
            for id_, name in rows:
                self.group_box.addItem(f"{id_} - {name}", id_)
            if selected_id:
                index = self.group_box.findData(selected_id)
                if index != -1:
                    self.group_box.setCurrentIndex(index)
            cur.close()
            conn.close()
        except Exception as e:
            logger.error(f"Ошибка загрузки групп: {e}")

    def load_students(self, selected_id=None):
        try:
            conn = get_connection()
            cur = conn.cursor()
            cur.execute(
                'SELECT "ID_student", "Surname", "Name" FROM public."Student" ORDER BY "Surname"'
            )
            rows = cur.fetchall()
            for id_, surname, name in rows:
                self.student_box.addItem(f"{id_} - {surname} {name}", id_)
            if selected_id:
                index = self.student_box.findData(selected_id)
                if index != -1:
                    self.student_box.setCurrentIndex(index)
            cur.close()
            conn.close()
        except Exception as e:
            logger.error(f"Ошибка загрузки студентов: {e}")

    def get_data(self):
        from_date_str = self.from_date.date().toString("yyyy-MM-dd")
        by_date_str = self.by_date.date().toString("yyyy-MM-dd")
        group_id = self.group_box.currentData()
        status = self.status_box.currentText()
        student_id = self.student_box.currentData()
        return (from_date_str, by_date_str, group_id, status, student_id)
