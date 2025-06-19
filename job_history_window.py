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


class JobHistoryWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Таблица: История должностей")
        self.setGeometry(100, 100, 800, 400)

        self.layout = QVBoxLayout()
        self.setLayout(self.layout)

        self.search_box = QLineEdit()
        self.search_box.setPlaceholderText("Поиск по фамилии преподавателя...")
        self.search_box.textChanged.connect(self.search_history)
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
                SELECT h."Start_date", t."Surname", t."Name", t."Patronymic",
                       j."Job_title_name", h."End_date", h."ID_teacher", h."ID_job"
                FROM public."Job_History" h
                JOIN public."Teacher" t ON h."ID_teacher" = t."ID_teacher"
                JOIN public."Job_title" j ON h."ID_job" = j."ID_job_title"
                ORDER BY h."Start_date"
            """
            )
            rows = cur.fetchall()
            self.table.setRowCount(len(rows))
            self.table.setColumnCount(8)
            self.table.setHorizontalHeaderLabels(
                [
                    "Дата начала",
                    "Фамилия",
                    "Имя",
                    "Отчество",
                    "Должность",
                    "Дата окончания",
                    "ID преподавателя",
                    "ID должности",
                ]
            )
            for i, row in enumerate(rows):
                for j, val in enumerate(row):
                    self.table.setItem(i, j, QTableWidgetItem(str(val)))
            cur.close()
            conn.close()
            logger.info("Загружены данные истории должностей")
        except Exception as e:
            logger.error(f"Ошибка загрузки данных: {e}")
            QMessageBox.critical(self, "Ошибка", str(e))

    def search_history(self):
        keyword = self.search_box.text().strip()
        try:
            conn = get_connection()
            cur = conn.cursor()
            cur.execute(
                """
                SELECT h."Start_date", t."Surname", t."Name", t."Patronymic",
                       j."Job_title_name", h."End_date", h."ID_teacher", h."ID_job"
                FROM public."Job_History" h
                JOIN public."Teacher" t ON h."ID_teacher" = t."ID_teacher"
                JOIN public."Job_title" j ON h."ID_job" = j."ID_job_title"
                WHERE t."Surname" ILIKE %s
                ORDER BY h."Start_date"
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
            logger.info(f"Поиск истории: {keyword}")
        except Exception as e:
            logger.error(f"Ошибка поиска: {e}")
            QMessageBox.critical(self, "Ошибка", str(e))

    def add_record(self):
        dialog = JobHistoryDialog()
        if dialog.exec_() == QDialog.Accepted:
            try:
                data = dialog.get_data()
                conn = get_connection()
                cur = conn.cursor()
                cur.execute(
                    """
                    INSERT INTO public."Job_History" ("Start_date", "ID_teacher", "End_date", "ID_job")
                    VALUES (%s, %s, %s, %s)
                """,
                    data,
                )
                conn.commit()
                cur.close()
                conn.close()
                self.load_data()
                logger.info("Добавлена запись в историю должностей")
            except Exception as e:
                logger.error(f"Ошибка добавления: {e}")
                QMessageBox.critical(self, "Ошибка", str(e))

    def edit_record(self):
        selected = self.table.currentRow()
        if selected < 0:
            QMessageBox.warning(self, "Внимание", "Выберите запись для редактирования")
            return

        start_date = self.table.item(selected, 0).text()
        teacher_id = self.table.item(selected, 6).text()
        end_date = self.table.item(selected, 5).text()
        job_id = self.table.item(selected, 7).text()

        dialog = JobHistoryDialog(
            start_date, teacher_id, end_date, job_id, editing=True
        )
        if dialog.exec_() == QDialog.Accepted:
            try:
                data = dialog.get_data()
                conn = get_connection()
                cur = conn.cursor()
                cur.execute(
                    """
                    UPDATE public."Job_History"
                    SET "End_date" = %s, "ID_teacher" = %s, "ID_job" = %s
                    WHERE "Start_date" = %s
                """,
                    (data[2], data[1], data[3], data[0]),
                )
                conn.commit()
                cur.close()
                conn.close()
                self.load_data()
                logger.info(f"Отредактирована запись: {start_date}")
            except Exception as e:
                logger.error(f"Ошибка редактирования: {e}")
                QMessageBox.critical(self, "Ошибка", str(e))

    def delete_record(self):
        selected = self.table.currentRow()
        if selected < 0:
            QMessageBox.warning(self, "Внимание", "Выберите запись для удаления")
            return

        start_date = self.table.item(selected, 0).text()
        confirm = QMessageBox.question(
            self,
            "Подтверждение",
            f"Удалить запись с датой начала {start_date}?",
            QMessageBox.Yes | QMessageBox.No,
        )
        if confirm == QMessageBox.Yes:
            try:
                conn = get_connection()
                cur = conn.cursor()
                cur.execute(
                    'DELETE FROM public."Job_History" WHERE "Start_date" = %s',
                    (start_date,),
                )
                conn.commit()
                cur.close()
                conn.close()
                self.load_data()
                logger.info(f"Удалена запись с датой начала: {start_date}")
            except Exception as e:
                logger.error(f"Ошибка удаления: {e}")
                QMessageBox.critical(self, "Ошибка", str(e))


class JobHistoryDialog(QDialog):
    def __init__(
        self, start_date="", teacher_id="", end_date="", job_id="", editing=False
    ):
        super().__init__()
        self.setWindowTitle("История должности")
        layout = QFormLayout(self)

        self.start_date = QDateEdit()
        self.start_date.setCalendarPopup(True)
        self.start_date.setDate(
            QDate.fromString(start_date, "yyyy-MM-dd")
            if start_date
            else QDate.currentDate()
        )
        self.start_date.setEnabled(not editing)

        self.end_date = QDateEdit()
        self.end_date.setCalendarPopup(True)
        self.end_date.setDate(
            QDate.fromString(end_date, "yyyy-MM-dd")
            if end_date
            else QDate.currentDate()
        )

        self.teacher_box = QComboBox()
        self.job_box = QComboBox()

        self.load_teachers(teacher_id)
        self.load_jobs(job_id)

        layout.addRow("Дата начала:", self.start_date)
        layout.addRow("Дата окончания:", self.end_date)
        layout.addRow("Преподаватель:", self.teacher_box)
        layout.addRow("Должность:", self.job_box)

        buttons = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        buttons.accepted.connect(self.accept)
        buttons.rejected.connect(self.reject)
        layout.addWidget(buttons)

    def load_teachers(self, selected_id=""):
        conn = get_connection()
        cur = conn.cursor()
        cur.execute(
            'SELECT "ID_teacher", "Surname" FROM public."Teacher" ORDER BY "Surname"'
        )
        rows = cur.fetchall()
        for tid, surname in rows:
            self.teacher_box.addItem(f"{surname} (ID={tid})", tid)
            if str(tid) == selected_id:
                self.teacher_box.setCurrentIndex(self.teacher_box.count() - 1)
        cur.close()
        conn.close()

    def load_jobs(self, selected_id=""):
        conn = get_connection()
        cur = conn.cursor()
        cur.execute(
            'SELECT "ID_job_title", "Job_title_name" FROM public."Job_title" ORDER BY "Job_title_name"'
        )
        rows = cur.fetchall()
        for jid, title in rows:
            self.job_box.addItem(f"{title} (ID={jid})", jid)
            if str(jid) == selected_id:
                self.job_box.setCurrentIndex(self.job_box.count() - 1)
        cur.close()
        conn.close()

    def get_data(self):
        return (
            self.start_date.date().toString("yyyy-MM-dd"),
            self.teacher_box.currentData(),
            self.end_date.date().toString("yyyy-MM-dd"),
            self.job_box.currentData(),
        )
