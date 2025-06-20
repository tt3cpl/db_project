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
    QDateTimeEdit,
    QComboBox,
)
from PyQt5.QtCore import QDateTime, QDate, QTime
from db import get_connection
from logger import logger


class SessionScheduleWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Таблица: Расписание сессии")
        self.setGeometry(100, 100, 1000, 500)

        self.layout = QVBoxLayout()
        self.setLayout(self.layout)

        self.search_box = QLineEdit()
        self.search_box.setPlaceholderText(
            "Поиск по номеру аудитории или названию дисциплины..."
        )
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
                SELECT ss."ID_session_schedules", ss."Start_time",
                       ss."ID_audience", a."Audience_number", a."Type",
                       ss."ID_disciplines", d."Discipline_name",
                       ss."ID_groups", g."Group_numbers"
                FROM public."Session_schedule" ss
                JOIN public."Audience" a ON ss."ID_audience" = a."ID_audience"
                JOIN public."Discipline" d ON ss."ID_disciplines" = d."ID_disciplines"
                JOIN public."Group" g ON ss."ID_groups" = g."ID_group"
                ORDER BY ss."Start_time"
            """
            )
            rows = cur.fetchall()
            self.table.setRowCount(len(rows))
            self.table.setColumnCount(9)
            self.table.setHorizontalHeaderLabels(
                [
                    "ID расписания",
                    "Дата и время начала",
                    "ID аудитории",
                    "Номер аудитории",
                    "Тип аудитории",
                    "ID дисциплины",
                    "Название дисциплины",
                    "ID группы",
                    "Номер группы",
                ]
            )
            for i, row in enumerate(rows):
                for j, val in enumerate(row):
                    self.table.setItem(i, j, QTableWidgetItem(str(val)))
            cur.close()
            conn.close()
            logger.info("Загружены данные расписания сессии")
        except Exception as e:
            logger.error(f"Ошибка загрузки расписания сессии: {e}")
            QMessageBox.critical(self, "Ошибка", str(e))

    def search_records(self):
        keyword = self.search_box.text().strip()
        try:
            conn = get_connection()
            cur = conn.cursor()
            cur.execute(
                """
                SELECT ss."ID_session_schedules", ss."Start_time",
                       ss."ID_audience", a."Audience_number", a."Type",
                       ss."ID_disciplines", d."Discipline_name",
                       ss."ID_groups", g."Group_numbers"
                FROM public."Session_schedule" ss
                JOIN public."Audience" a ON ss."ID_audience" = a."ID_audience"
                JOIN public."Discipline" d ON ss."ID_disciplines" = d."ID_disciplines"
                JOIN public."Group" g ON ss."ID_groups" = g."ID_group"
                WHERE CAST(a."Audience_number" AS TEXT) ILIKE %s OR d."Discipline_name" ILIKE %s
                ORDER BY ss."Start_time"
            """,
                (f"%{keyword}%", f"%{keyword}%"),
            )
            rows = cur.fetchall()
            self.table.setRowCount(len(rows))
            for i, row in enumerate(rows):
                for j, val in enumerate(row):
                    self.table.setItem(i, j, QTableWidgetItem(str(val)))
            cur.close()
            conn.close()
            logger.info(f"Поиск расписания сессии: {keyword}")
        except Exception as e:
            logger.error(f"Ошибка поиска расписания сессии: {e}")
            QMessageBox.critical(self, "Ошибка", str(e))

    def add_record(self):
        dialog = SessionScheduleDialog()
        if dialog.exec_() == QDialog.Accepted:
            try:
                data = dialog.get_data()
                conn = get_connection()
                cur = conn.cursor()
                cur.execute(
                    """
                    INSERT INTO public."Session_schedule"
                    ("ID_audience", "ID_disciplines", "ID_groups", "Start_time")
                    VALUES (%s, %s, %s, %s)
                """,
                    data,
                )
                conn.commit()
                cur.close()
                conn.close()
                self.load_data()
                logger.info("Добавлена запись расписания сессии")
            except Exception as e:
                logger.error(f"Ошибка добавления расписания сессии: {e}")
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
                SELECT "ID_audience", "ID_disciplines", "ID_groups", "Start_time"
                FROM public."Session_schedule" WHERE "ID_session_schedules" = %s
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
                f"Ошибка получения данных для редактирования расписания сессии: {e}"
            )
            QMessageBox.critical(self, "Ошибка", str(e))
            return

        dialog = SessionScheduleDialog(*row, editing=True)
        if dialog.exec_() == QDialog.Accepted:
            try:
                data = dialog.get_data()
                conn = get_connection()
                cur = conn.cursor()
                cur.execute(
                    """
                    UPDATE public."Session_schedule"
                    SET "ID_audience" = %s, "ID_disciplines" = %s, "ID_groups" = %s, "Start_time" = %s
                    WHERE "ID_session_schedules" = %s
                """,
                    (*data, record_id),
                )
                conn.commit()
                cur.close()
                conn.close()
                self.load_data()
                logger.info(f"Отредактирована запись расписания сессии ID={record_id}")
            except Exception as e:
                logger.error(f"Ошибка редактирования расписания сессии: {e}")
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
                    'DELETE FROM public."Session_schedule" WHERE "ID_session_schedules" = %s',
                    (record_id,),
                )
                conn.commit()
                cur.close()
                conn.close()
                self.load_data()
                logger.info(f"Удалена запись расписания сессии ID={record_id}")
            except Exception as e:
                logger.error(f"Ошибка удаления расписания сессии: {e}")
                QMessageBox.critical(self, "Ошибка", str(e))


class SessionScheduleDialog(QDialog):
    def __init__(
        self,
        audience_id=None,
        discipline_id=None,
        group_id=None,
        start=None,
        editing=False,
    ):
        super().__init__()
        self.setWindowTitle("Расписание сессии")
        layout = QFormLayout(self)

        self.audience_box = QComboBox()
        self.load_audiences(audience_id)

        self.discipline_box = QComboBox()
        self.load_disciplines(discipline_id)

        self.group_box = QComboBox()
        self.load_groups(group_id)

        self.start = QDateTimeEdit()
        self.start.setCalendarPopup(True)
        self.start.setDisplayFormat("yyyy-MM-dd HH:mm:ss")
        self.start.setDate(
            QDate.fromString(str(start), "yyyy-MM-dd") if start else QDate.currentDate()
        )

        layout.addRow("Аудитория:", self.audience_box)
        layout.addRow("Дисциплина:", self.discipline_box)
        layout.addRow("Группа:", self.group_box)
        layout.addRow("Дата и время начала:", self.start)

        buttons = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        buttons.accepted.connect(self.accept)
        buttons.rejected.connect(self.reject)
        layout.addRow(buttons)

    def load_audiences(self, selected_id=None):
        try:
            conn = get_connection()
            cur = conn.cursor()
            cur.execute(
                """
                SELECT "ID_audience", "Audience_number", "Type"
                FROM public."Audience"
                ORDER BY "Audience_number"
            """
            )
            rows = cur.fetchall()
            for id_, number, type_ in rows:
                self.audience_box.addItem(f"{id_} - №{number} ({type_})", id_)
            if selected_id:
                index = self.audience_box.findData(selected_id)
                if index != -1:
                    self.audience_box.setCurrentIndex(index)
            cur.close()
            conn.close()
        except Exception as e:
            logger.error(f"Ошибка загрузки аудиторий: {e}")

    def load_disciplines(self, selected_id=None):
        try:
            conn = get_connection()
            cur = conn.cursor()
            cur.execute(
                """
                SELECT "ID_disciplines", "Discipline_name"
                FROM public."Discipline"
                ORDER BY "Discipline_name"
            """
            )
            rows = cur.fetchall()
            for id_, name in rows:
                self.discipline_box.addItem(f"{id_} - {name}", id_)
            if selected_id:
                index = self.discipline_box.findData(selected_id)
                if index != -1:
                    self.discipline_box.setCurrentIndex(index)
            cur.close()
            conn.close()
        except Exception as e:
            logger.error(f"Ошибка загрузки дисциплин: {e}")

    def load_groups(self, selected_id=None):
        try:
            conn = get_connection()
            cur = conn.cursor()
            cur.execute(
                """
                SELECT "ID_group", "Group_numbers"
                FROM public."Group"
                ORDER BY "Group_numbers"
            """
            )
            rows = cur.fetchall()
            for id_, number in rows:
                self.group_box.addItem(f"{id_} - {number}", id_)
            if selected_id:
                index = self.group_box.findData(selected_id)
                if index != -1:
                    self.group_box.setCurrentIndex(index)
            cur.close()
            conn.close()
        except Exception as e:
            logger.error(f"Ошибка загрузки групп: {e}")

    def get_data(self):
        from_date_str = self.start.text()
        audience_id = self.audience_box.currentData()
        discipline_id = self.discipline_box.currentData()
        group_id = self.group_box.currentData()
        return (audience_id, discipline_id, group_id, from_date_str)
