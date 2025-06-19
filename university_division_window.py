from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QPushButton, QTableWidget, QTableWidgetItem,
    QLineEdit, QLabel, QHBoxLayout, QMessageBox, QDialog, QFormLayout, QDialogButtonBox
)
from db import get_connection
from logger import logger

class UniversityDivisionWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Таблица: Подразделения ВУЗа")
        self.setGeometry(100, 100, 600, 300)

        self.layout = QVBoxLayout()
        self.setLayout(self.layout)

        self.search_box = QLineEdit()
        self.search_box.setPlaceholderText("Поиск по названию подразделения...")
        self.search_box.textChanged.connect(self.search_divisions)
        self.layout.addWidget(self.search_box)

        self.table = QTableWidget()
        self.layout.addWidget(self.table)

        btns = QHBoxLayout()

        refresh_btn = QPushButton("Обновить")
        refresh_btn.clicked.connect(self.load_data)
        btns.addWidget(refresh_btn)

        add_btn = QPushButton("Добавить")
        add_btn.clicked.connect(self.add_division)
        btns.addWidget(add_btn)

        edit_btn = QPushButton("Редактировать")
        edit_btn.clicked.connect(self.edit_division)
        btns.addWidget(edit_btn)

        delete_btn = QPushButton("Удалить")
        delete_btn.clicked.connect(self.delete_division)
        btns.addWidget(delete_btn)

        self.layout.addLayout(btns)
        self.load_data()

    def load_data(self):
        try:
            conn = get_connection()
            cur = conn.cursor()
            cur.execute('SELECT * FROM public."University_division" ORDER BY "ID_divisions"')
            rows = cur.fetchall()
            self.table.setRowCount(len(rows))
            self.table.setColumnCount(2)
            self.table.setHorizontalHeaderLabels(["ID", "Название подразделения"])
            for i, row in enumerate(rows):
                for j, val in enumerate(row):
                    self.table.setItem(i, j, QTableWidgetItem(str(val)))
            cur.close()
            conn.close()
            logger.info("Загружены данные подразделений ВУЗа")
        except Exception as e:
            logger.error(f"Ошибка загрузки данных: {e}")
            QMessageBox.critical(self, "Ошибка", str(e))

    def search_divisions(self):
        keyword = self.search_box.text().strip()
        try:
            conn = get_connection()
            cur = conn.cursor()
            cur.execute("""
                SELECT * FROM public."University_division"
                WHERE "Name_of_the_department" ILIKE %s
                ORDER BY "ID_divisions"
            """, (f"%{keyword}%",))
            rows = cur.fetchall()
            self.table.setRowCount(len(rows))
            for i, row in enumerate(rows):
                for j, val in enumerate(row):
                    self.table.setItem(i, j, QTableWidgetItem(str(val)))
            cur.close()
            conn.close()
            logger.info(f"Поиск подразделений: {keyword}")
        except Exception as e:
            logger.error(f"Ошибка поиска: {e}")
            QMessageBox.critical(self, "Ошибка", str(e))

    def add_division(self):
        dialog = DivisionDialog()
        if dialog.exec_() == QDialog.Accepted:
            try:
                conn = get_connection()
                cur = conn.cursor()
                cur.execute("""
                    INSERT INTO public."University_division" ("Name_of_the_department")
                    VALUES (%s)
                """, (dialog.get_data(),))
                conn.commit()
                cur.close()
                conn.close()
                self.load_data()
                logger.info("Добавлено подразделение")
            except Exception as e:
                logger.error(f"Ошибка добавления: {e}")
                QMessageBox.critical(self, "Ошибка", str(e))

    def edit_division(self):
        selected = self.table.currentRow()
        if selected < 0:
            QMessageBox.warning(self, "Внимание", "Выберите подразделение для редактирования")
            return

        division_id = self.table.item(selected, 0).text()
        current_name = self.table.item(selected, 1).text()

        dialog = DivisionDialog(current_name)
        if dialog.exec_() == QDialog.Accepted:
            try:
                conn = get_connection()
                cur = conn.cursor()
                cur.execute("""
                    UPDATE public."University_division"
                    SET "Name_of_the_department" = %s
                    WHERE "ID_divisions" = %s
                """, (dialog.get_data(), division_id))
                conn.commit()
                cur.close()
                conn.close()
                self.load_data()
                logger.info(f"Отредактировано подразделение ID={division_id}")
            except Exception as e:
                logger.error(f"Ошибка редактирования: {e}")
                QMessageBox.critical(self, "Ошибка", str(e))

    def delete_division(self):
        selected = self.table.currentRow()
        if selected < 0:
            QMessageBox.warning(self, "Внимание", "Выберите подразделение для удаления")
            return

        division_id = self.table.item(selected, 0).text()
        confirm = QMessageBox.question(
            self, "Подтверждение",
            f"Удалить подразделение ID {division_id}?",
            QMessageBox.Yes | QMessageBox.No
        )

        if confirm == QMessageBox.Yes:
            try:
                conn = get_connection()
                cur = conn.cursor()
                cur.execute('DELETE FROM public."University_division" WHERE "ID_divisions" = %s', (division_id,))
                conn.commit()
                cur.close()
                conn.close()
                self.load_data()
                logger.info(f"Удалено подразделение ID={division_id}")
            except Exception as e:
                logger.error(f"Ошибка удаления: {e}")
                QMessageBox.critical(self, "Ошибка", str(e))


class DivisionDialog(QDialog):
    def __init__(self, name=""):
        super().__init__()
        self.setWindowTitle("Данные подразделения")
        layout = QFormLayout(self)

        self.name_input = QLineEdit(name)
        layout.addRow("Название подразделения:", self.name_input)

        buttons = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        buttons.accepted.connect(self.accept)
        buttons.rejected.connect(self.reject)
        layout.addWidget(buttons)

    def get_data(self):
        return self.name_input.text()
