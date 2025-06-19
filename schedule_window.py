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


class ScheduleWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Таблица: Расписание")
        self.setGeometry(100, 100, 950, 450)

        self.layout = QVBoxLayout()
        self.setLayout(self.layout)

        self.search_box = QLineEdit()
        self.search_box.setPlaceholderText("Поиск по фамилии преподавателя...")
        self.search_box.textChanged.connect(self.search_schedule)
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
                SELECT s."ID_schedules", a."ID_audience", t."Surname", t."Name", g."ID_group",
                       d."Discipline_name", s."Start_time", s."End_time", s."Class_type"
                FROM public."Schedule" s
                JOIN public."Audience" a ON s."ID_audience" = a."ID_audience"
                JOIN public."Teacher" t ON s."ID_teacher" = t."ID_teacher"
                JOIN public."Group" g ON s."ID_group" = g."ID_group"
                JOIN public."Discipline" d ON s."ID_disciplines" = d."ID_disciplines"
                ORDER BY s."Start_time"
                """
            )
            rows = cur.fetchall()
            self.table.setRowCount(len(rows))
            self.table.setColumnCount(9)
            self.table.setHorizontalHeaderLabels(
                [
                    "ID расписания",
                    "ID аудитории",
                    "Фамилия преподавателя",
                    "Имя преподавателя",
                    "ID группы",
                    "Дисциплина",
                    "Дата начала",
                    "Дата окончания",
                    "Тип занятия",
                ]
            )
            for i, row in enumerate(rows):
                for j, val in enumerate(row):
                    self.table.setItem(i, j, QTableWidgetItem(str(val)))
            cur.close()
            conn.close()
            logger.info("Загружены данные расписания")
        except Exception as e:
            logger.error(f"Ошибка загрузки данных расписания: {e}")
            QMessageBox.critical(self, "Ошибка", str(e))

    def search_schedule(self):
        keyword = self.search_box.text().strip()
        try:
            conn = get_connection()
            cur = conn.cursor()
            cur.execute(
                """
                SELECT s."ID_schedules", a."ID_audience", t."Surname", t."Name", g."ID_group",
                       d."Discipline_name", s."Start_time", s."End_time", s."Class_type"
                FROM public."Schedule" s
                JOIN public."Audience" a ON s."ID_audience" = a."ID_audience"
                JOIN public."Teacher" t ON s."ID_teacher" = t."ID_teacher"
                JOIN public."Group" g ON s."ID_group" = g."ID_group"
                JOIN public."Discipline" d ON s."ID_disciplines" = d."ID_disciplines"
                WHERE t."Surname" ILIKE %s
                ORDER BY s."Start_time"
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
            logger.info(f"Поиск расписания: {keyword}")
        except Exception as e:
            logger.error(f"Ошибка поиска расписания: {e}")
            QMessageBox.critical(self, "Ошибка", str(e))

    def add_record(self):
        dialog = ScheduleDialog()
        if dialog.exec_() == QDialog.Accepted:
            try:
                data = dialog.get_data()
                conn = get_connection()
                cur = conn.cursor()
                cur.execute(
                    """
                    INSERT INTO public."Schedule"
                    ("ID_audience", "ID_teacher", "ID_group", "ID_disciplines", "Start_time", "End_time", "Class_type")
                    VALUES (%s, %s, %s, %s, %s, %s, %s)
                    """,
                    data,
                )
                conn.commit()
                cur.close()
                conn.close()
                self.load_data()
                logger.info("Добавлена запись в расписание")
            except Exception as e:
                logger.error(f"Ошибка добавления расписания: {e}")
                QMessageBox.critical(self, "Ошибка", str(e))

    def edit_record(self):
        selected = self.table.currentRow()
        if selected < 0:
            QMessageBox.warning(self, "Внимание", "Выберите запись для редактирования")
            return

        schedule_id = self.table.item(selected, 0).text()

        try:
            conn = get_connection()
            cur = conn.cursor()
            cur.execute(
                """
                SELECT "ID_audience", "ID_teacher", "ID_group", "ID_disciplines",
                       "Start_time", "End_time", "Class_type"
                FROM public."Schedule" WHERE "ID_schedules" = %s
                """,
                (schedule_id,),
            )
            row = cur.fetchone()
            if not row:
                QMessageBox.warning(self, "Внимание", "Запись не найдена")
                return
            (
                audience_id,
                teacher_id,
                group_id,
                discipline_id,
                start_time,
                end_time,
                class_type,
            ) = row
            cur.close()
            conn.close()
        except Exception as e:
            logger.error(f"Ошибка получения данных для редактирования расписания: {e}")
            QMessageBox.critical(self, "Ошибка", str(e))
            return

        dialog = ScheduleDialog(
            audience_id,
            teacher_id,
            group_id,
            discipline_id,
            start_time,
            end_time,
            class_type,
            editing=True,
        )
        if dialog.exec_() == QDialog.Accepted:
            try:
                data = dialog.get_data()
                conn = get_connection()
                cur = conn.cursor()
                cur.execute(
                    """
                    UPDATE public."Schedule"
                    SET "ID_audience" = %s, "ID_teacher" = %s, "ID_group" = %s,
                        "ID_disciplines" = %s, "Start_time" = %s, "End_time" = %s,
                        "Class_type" = %s
                    WHERE "ID_schedules" = %s
                    """,
                    (*data, schedule_id),
                )
                conn.commit()
                cur.close()
                conn.close()
                self.load_data()
                logger.info(f"Отредактирована запись расписания ID={schedule_id}")
            except Exception as e:
                logger.error(f"Ошибка редактирования расписания: {e}")
                QMessageBox.critical(self, "Ошибка", str(e))

    def delete_record(self):
        selected = self.table.currentRow()
        if selected < 0:
            QMessageBox.warning(self, "Внимание", "Выберите запись для удаления")
            return

        schedule_id = self.table.item(selected, 0).text()
        confirm = QMessageBox.question(
            self,
            "Подтверждение",
            f"Удалить расписание с ID {schedule_id}?",
            QMessageBox.Yes | QMessageBox.No,
        )
        if confirm == QMessageBox.Yes:
            try:
                conn = get_connection()
                cur = conn.cursor()
                cur.execute(
                    'DELETE FROM public."Schedule" WHERE "ID_schedules" = %s',
                    (schedule_id,),
                )
                conn.commit()
                cur.close()
                conn.close()
                self.load_data()
                logger.info(f"Удалена запись расписания ID={schedule_id}")
            except Exception as e:
                logger.error(f"Ошибка удаления расписания: {e}")
                QMessageBox.critical(self, "Ошибка", str(e))


class ScheduleDialog(QDialog):
    def __init__(
        self,
        audience_id=None,
        teacher_id=None,
        group_id=None,
        discipline_id=None,
        start_time=None,
        end_time=None,
        class_type=None,
        editing=False,
    ):
        super().__init__()
        self.setWindowTitle("Расписание")
        layout = QFormLayout(self)

        self.audience_box = QComboBox()
        self.teacher_box = QComboBox()
        self.group_box = QComboBox()
        self.discipline_box = QComboBox()
        self.class_type_box = QComboBox()
        self.class_type_box.addItems(["Лекция", "Практика", "Лабораторная работа"])

        self.load_audiences(audience_id)
        self.load_teachers(teacher_id)
        self.load_groups(group_id)
        self.load_disciplines(discipline_id)

        if editing and class_type:
            idx = self.class_type_box.findText(class_type)
            if idx >= 0:
                self.class_type_box.setCurrentIndex(idx)

        self.start_time = QDateEdit()
        self.start_time.setCalendarPopup(True)
        self.start_time.setDate(
            QDate.fromString(str(start_time), "yyyy-MM-dd")
            if start_time
            else QDate.currentDate()
        )

        self.end_time = QDateEdit()
        self.end_time.setCalendarPopup(True)
        self.end_time.setDate(
            QDate.fromString(str(end_time), "yyyy-MM-dd")
            if end_time
            else QDate.currentDate()
        )

        layout.addRow("Аудитория:", self.audience_box)
        layout.addRow("Преподаватель:", self.teacher_box)
        layout.addRow("Группа:", self.group_box)
        layout.addRow("Дисциплина:", self.discipline_box)
        layout.addRow("Тип занятия:", self.class_type_box)
        layout.addRow("Дата начала:", self.start_time)
        layout.addRow("Дата окончания:", self.end_time)

        buttons = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        buttons.accepted.connect(self.accept)
        buttons.rejected.connect(self.reject)
        layout.addWidget(buttons)

    def load_audiences(self, selected_id=None):
        conn = get_connection()
        cur = conn.cursor()
        cur.execute(
            'SELECT "ID_audience", "Audience_number" FROM public."Audience" ORDER BY "Audience_number"'
        )
        for aid, name in cur.fetchall():
            self.audience_box.addItem(f"{name} (ID={aid})", aid)
            if selected_id and aid == selected_id:
                self.audience_box.setCurrentIndex(self.audience_box.count() - 1)
        cur.close()
        conn.close()

    def load_teachers(self, selected_id=None):
        conn = get_connection()
        cur = conn.cursor()
        cur.execute(
            'SELECT "ID_teacher", "Surname" FROM public."Teacher" ORDER BY "Surname"'
        )
        for tid, surname in cur.fetchall():
            self.teacher_box.addItem(f"{surname} (ID={tid})", tid)
            if selected_id and tid == selected_id:
                self.teacher_box.setCurrentIndex(self.teacher_box.count() - 1)
        cur.close()
        conn.close()

    def load_groups(self, selected_id=None):
        conn = get_connection()
        cur = conn.cursor()
        cur.execute(
            'SELECT "ID_group", "Group_numbers" FROM public."Group" ORDER BY "Group_numbers"'
        )
        for gid, name in cur.fetchall():
            self.group_box.addItem(f"{name} (ID={gid})", gid)
            if selected_id and gid == selected_id:
                self.group_box.setCurrentIndex(self.group_box.count() - 1)
        cur.close()
        conn.close()

    def load_disciplines(self, selected_id=None):
        conn = get_connection()
        cur = conn.cursor()
        cur.execute(
            'SELECT "ID_disciplines", "Discipline_name" FROM public."Discipline" ORDER BY "Discipline_name"'
        )
        for did, name in cur.fetchall():
            self.discipline_box.addItem(f"{name} (ID={did})", did)
            if selected_id and did == selected_id:
                self.discipline_box.setCurrentIndex(self.discipline_box.count() - 1)
        cur.close()
        conn.close()

    def get_data(self):
        return (
            self.audience_box.currentData(),
            self.teacher_box.currentData(),
            self.group_box.currentData(),
            self.discipline_box.currentData(),
            self.start_time.date().toString("yyyy-MM-dd"),
            self.end_time.date().toString("yyyy-MM-dd"),
            self.class_type_box.currentText(),
        )
