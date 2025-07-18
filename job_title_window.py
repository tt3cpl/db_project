from PyQt5.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QPushButton,
    QTableWidget,
    QTableWidgetItem,
    QComboBox,
    QLineEdit,
    QHBoxLayout,
    QMessageBox,
    QDialog,
    QFormLayout,
    QDialogButtonBox,
)
from db import get_connection
from logger import logger


class JobTitleWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Таблица: Должности")
        self.setGeometry(100, 100, 700, 350)

        self.layout = QVBoxLayout()
        self.setLayout(self.layout)

        self.search_box = QLineEdit()
        self.search_box.setPlaceholderText("Поиск по названию должности...")
        self.search_box.textChanged.connect(self.search_job_titles)
        self.layout.addWidget(self.search_box)

        self.table = QTableWidget()
        self.layout.addWidget(self.table)

        btns = QHBoxLayout()

        refresh_btn = QPushButton("Обновить")
        refresh_btn.clicked.connect(self.load_data)
        btns.addWidget(refresh_btn)

        add_btn = QPushButton("Добавить")
        add_btn.clicked.connect(self.add_job_title)
        btns.addWidget(add_btn)

        edit_btn = QPushButton("Редактировать")
        edit_btn.clicked.connect(self.edit_job_title)
        btns.addWidget(edit_btn)

        delete_btn = QPushButton("Удалить")
        delete_btn.clicked.connect(self.delete_job_title)
        btns.addWidget(delete_btn)

        self.layout.addLayout(btns)
        self.load_data()

    def load_data(self):
        try:
            conn = get_connection()
            cur = conn.cursor()
            cur.execute('SELECT * FROM public."Job_title" ORDER BY "ID_job_title"')
            rows = cur.fetchall()
            self.table.setRowCount(len(rows))
            self.table.setColumnCount(4)
            self.table.setHorizontalHeaderLabels(
                ["ID", "Зарплата", "Название должности", "Количество ставок"]
            )
            for i, row in enumerate(rows):
                for j, val in enumerate(row):
                    self.table.setItem(i, j, QTableWidgetItem(str(val)))
            cur.close()
            conn.close()
            logger.info("Загружены данные должностей")
        except Exception as e:
            logger.error(f"Ошибка загрузки данных: {e}")
            QMessageBox.critical(self, "Ошибка", str(e))

    def search_job_titles(self):
        keyword = self.search_box.text().strip()
        try:
            conn = get_connection()
            cur = conn.cursor()
            cur.execute(
                """
                SELECT * FROM public."Job_title"
                WHERE "Job_title_name" ILIKE %s
                ORDER BY "ID_job_title"
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
            logger.info(f"Поиск должностей: {keyword}")
        except Exception as e:
            logger.error(f"Ошибка поиска: {e}")
            QMessageBox.critical(self, "Ошибка", str(e))

    def add_job_title(self):
        dialog = JobTitleDialog()
        if dialog.exec_() == QDialog.Accepted:
            try:
                conn = get_connection()
                cur = conn.cursor()
                cur.execute(
                    """
                    INSERT INTO public."Job_title" ("Salary", "Job_title_name", "Number_of_bets")
                    VALUES (%s, %s, %s)
                """,
                    dialog.get_data(),
                )
                conn.commit()
                cur.close()
                conn.close()
                self.load_data()
                logger.info("Добавлена должность")
            except Exception as e:
                logger.error(f"Ошибка добавления: {e}")
                QMessageBox.critical(self, "Ошибка", str(e))

    def edit_job_title(self):
        selected = self.table.currentRow()
        if selected < 0:
            QMessageBox.warning(
                self, "Внимание", "Выберите должность для редактирования"
            )
            return

        job_title_id = self.table.item(selected, 0).text()
        current_data = [
            self.table.item(selected, 1).text(),
            self.table.item(selected, 2).text(),
            self.table.item(selected, 3).text(),
        ]

        dialog = JobTitleDialog(*current_data)
        if dialog.exec_() == QDialog.Accepted:
            try:
                conn = get_connection()
                cur = conn.cursor()
                cur.execute(
                    """
                    UPDATE public."Job_title"
                    SET "Salary" = %s, "Job_title_name" = %s, "Number_of_bets" = %s
                    WHERE "ID_job_title" = %s
                """,
                    (*dialog.get_data(), job_title_id),
                )
                conn.commit()
                cur.close()
                conn.close()
                self.load_data()
                logger.info(f"Отредактирована должность ID={job_title_id}")
            except Exception as e:
                logger.error(f"Ошибка редактирования: {e}")
                QMessageBox.critical(self, "Ошибка", str(e))

    def delete_job_title(self):
        selected = self.table.currentRow()
        if selected < 0:
            QMessageBox.warning(self, "Внимание", "Выберите должность для удаления")
            return

        job_title_id = self.table.item(selected, 0).text()
        confirm = QMessageBox.question(
            self,
            "Подтверждение",
            f"Удалить должность ID {job_title_id}?",
            QMessageBox.Yes | QMessageBox.No,
        )

        if confirm == QMessageBox.Yes:
            try:
                conn = get_connection()
                cur = conn.cursor()
                cur.execute(
                    'DELETE FROM public."Job_title" WHERE "ID_job_title" = %s',
                    (job_title_id,),
                )
                conn.commit()
                cur.close()
                conn.close()
                self.load_data()
                logger.info(f"Удалена должность ID={job_title_id}")
            except Exception as e:
                logger.error(f"Ошибка удаления: {e}")
                QMessageBox.critical(self, "Ошибка", str(e))


class JobTitleDialog(QDialog):
    BETS_OPTIONS = ["0.25", "0.5", "0.75", "1.0"]

    def __init__(self, salary="", title="", bets=""):
        super().__init__()
        self.setWindowTitle("Данные должности")
        layout = QFormLayout(self)

        self.salary_input = QLineEdit(salary)
        self.title_input = QLineEdit(title)

        self.bets_combo = QComboBox()
        self.bets_combo.addItems(self.BETS_OPTIONS)
        if bets in self.BETS_OPTIONS:
            self.bets_combo.setCurrentText(bets)
        else:
            self.bets_combo.setCurrentIndex(0)

        layout.addRow("Зарплата:", self.salary_input)
        layout.addRow("Название должности:", self.title_input)
        layout.addRow("Количество ставок:", self.bets_combo)

        buttons = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        buttons.accepted.connect(self.accept)
        buttons.rejected.connect(self.reject)
        layout.addWidget(buttons)

    def get_data(self):
        return (
            float(self.salary_input.text()),
            self.title_input.text(),
            float(self.bets_combo.currentText()),
        )
