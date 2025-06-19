from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QPushButton, QTableWidget, QTableWidgetItem,
    QLineEdit, QHBoxLayout, QMessageBox, QDialog, QFormLayout, QDialogButtonBox
)
from db import get_connection
from logger import logger

class ScholarshipWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Таблица: Стипендии")
        self.setGeometry(100, 100, 600, 300)

        self.layout = QVBoxLayout()
        self.setLayout(self.layout)

        self.search_box = QLineEdit()
        self.search_box.setPlaceholderText("Поиск по типу стипендии...")
        self.search_box.textChanged.connect(self.search_scholarships)
        self.layout.addWidget(self.search_box)

        self.table = QTableWidget()
        self.layout.addWidget(self.table)

        btns = QHBoxLayout()

        refresh_btn = QPushButton("Обновить")
        refresh_btn.clicked.connect(self.load_data)
        btns.addWidget(refresh_btn)

        add_btn = QPushButton("Добавить")
        add_btn.clicked.connect(self.add_scholarship)
        btns.addWidget(add_btn)

        edit_btn = QPushButton("Редактировать")
        edit_btn.clicked.connect(self.edit_scholarship)
        btns.addWidget(edit_btn)

        delete_btn = QPushButton("Удалить")
        delete_btn.clicked.connect(self.delete_scholarship)
        btns.addWidget(delete_btn)

        self.layout.addLayout(btns)
        self.load_data()

    def load_data(self):
        try:
            conn = get_connection()
            cur = conn.cursor()
            cur.execute('SELECT * FROM public."Scholarship" ORDER BY "ID_scholarships"')
            rows = cur.fetchall()
            self.table.setRowCount(len(rows))
            self.table.setColumnCount(3)
            self.table.setHorizontalHeaderLabels(["ID", "Тип стипендии", "Размер"])
            for i, row in enumerate(rows):
                for j, val in enumerate(row):
                    self.table.setItem(i, j, QTableWidgetItem(str(val)))
            cur.close()
            conn.close()
            logger.info("Загружены данные стипендий")
        except Exception as e:
            logger.error(f"Ошибка загрузки данных: {e}")
            QMessageBox.critical(self, "Ошибка", str(e))

    def search_scholarships(self):
        keyword = self.search_box.text().strip()
        try:
            conn = get_connection()
            cur = conn.cursor()
            cur.execute("""
                SELECT * FROM public."Scholarship"
                WHERE "Type_of_scholarship" ILIKE %s
                ORDER BY "ID_scholarships"
            """, (f"%{keyword}%",))
            rows = cur.fetchall()
            self.table.setRowCount(len(rows))
            for i, row in enumerate(rows):
                for j, val in enumerate(row):
                    self.table.setItem(i, j, QTableWidgetItem(str(val)))
            cur.close()
            conn.close()
            logger.info(f"Поиск стипендий: {keyword}")
        except Exception as e:
            logger.error(f"Ошибка поиска: {e}")
            QMessageBox.critical(self, "Ошибка", str(e))

    def add_scholarship(self):
        dialog = ScholarshipDialog()
        if dialog.exec_() == QDialog.Accepted:
            try:
                conn = get_connection()
                cur = conn.cursor()
                cur.execute("""
                    INSERT INTO public."Scholarship" ("Type_of_scholarship", "Size")
                    VALUES (%s, %s)
                """, dialog.get_data())
                conn.commit()
                cur.close()
                conn.close()
                self.load_data()
                logger.info("Добавлена стипендия")
            except Exception as e:
                logger.error(f"Ошибка добавления: {e}")
                QMessageBox.critical(self, "Ошибка", str(e))

    def edit_scholarship(self):
        selected = self.table.currentRow()
        if selected < 0:
            QMessageBox.warning(self, "Внимание", "Выберите стипендию для редактирования")
            return

        scholarship_id = self.table.item(selected, 0).text()
        current_type = self.table.item(selected, 1).text()
        current_size = self.table.item(selected, 2).text()

        dialog = ScholarshipDialog(current_type, current_size)
        if dialog.exec_() == QDialog.Accepted:
            try:
                conn = get_connection()
                cur = conn.cursor()
                cur.execute("""
                    UPDATE public."Scholarship"
                    SET "Type_of_scholarship" = %s, "Size" = %s
                    WHERE "ID_scholarships" = %s
                """, (*dialog.get_data(), scholarship_id))
                conn.commit()
                cur.close()
                conn.close()
                self.load_data()
                logger.info(f"Отредактирована стипендия ID={scholarship_id}")
            except Exception as e:
                logger.error(f"Ошибка редактирования: {e}")
                QMessageBox.critical(self, "Ошибка", str(e))

    def delete_scholarship(self):
        selected = self.table.currentRow()
        if selected < 0:
            QMessageBox.warning(self, "Внимание", "Выберите стипендию для удаления")
            return

        scholarship_id = self.table.item(selected, 0).text()
        confirm = QMessageBox.question(
            self, "Подтверждение",
            f"Удалить стипендию ID {scholarship_id}?",
            QMessageBox.Yes | QMessageBox.No
        )

        if confirm == QMessageBox.Yes:
            try:
                conn = get_connection()
                cur = conn.cursor()
                cur.execute('DELETE FROM public."Scholarship" WHERE "ID_scholarships" = %s', (scholarship_id,))
                conn.commit()
                cur.close()
                conn.close()
                self.load_data()
                logger.info(f"Удалена стипендия ID={scholarship_id}")
            except Exception as e:
                logger.error(f"Ошибка удаления: {e}")
                QMessageBox.critical(self, "Ошибка", str(e))


class ScholarshipDialog(QDialog):
    def __init__(self, scholarship_type="", size=""):
        super().__init__()
        self.setWindowTitle("Данные стипендии")
        layout = QFormLayout(self)

        self.type_input = QLineEdit(scholarship_type)
        self.size_input = QLineEdit(size)

        layout.addRow("Тип стипендии:", self.type_input)
        layout.addRow("Размер:", self.size_input)

        buttons = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        buttons.accepted.connect(self.accept)
        buttons.rejected.connect(self.reject)
        layout.addWidget(buttons)

    def get_data(self):
        return (self.type_input.text(), int(self.size_input.text()))
