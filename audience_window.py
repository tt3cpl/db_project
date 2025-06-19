from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QPushButton, QTableWidget, QTableWidgetItem,
    QLineEdit, QHBoxLayout, QMessageBox, QDialog, QFormLayout, QDialogButtonBox
)
from db import get_connection
from logger import logger


class AudienceWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Таблица: Аудитории")
        self.setGeometry(100, 100, 750, 350)

        self.layout = QVBoxLayout()
        self.setLayout(self.layout)

        self.search_box = QLineEdit()
        self.search_box.setPlaceholderText("Поиск по адресу...")
        self.search_box.textChanged.connect(self.search_audience)
        self.layout.addWidget(self.search_box)

        self.table = QTableWidget()
        self.layout.addWidget(self.table)

        btns = QHBoxLayout()

        refresh_btn = QPushButton("Обновить")
        refresh_btn.clicked.connect(self.load_data)
        btns.addWidget(refresh_btn)

        add_btn = QPushButton("Добавить")
        add_btn.clicked.connect(self.add_audience)
        btns.addWidget(add_btn)

        edit_btn = QPushButton("Редактировать")
        edit_btn.clicked.connect(self.edit_audience)
        btns.addWidget(edit_btn)

        delete_btn = QPushButton("Удалить")
        delete_btn.clicked.connect(self.delete_audience)
        btns.addWidget(delete_btn)

        self.layout.addLayout(btns)
        self.load_data()

    def load_data(self):
        try:
            conn = get_connection()
            cur = conn.cursor()
            cur.execute('SELECT * FROM public."Audience" ORDER BY "ID_audience"')
            rows = cur.fetchall()
            self.table.setRowCount(len(rows))
            self.table.setColumnCount(5)
            self.table.setHorizontalHeaderLabels([
                "ID", "Тип", "Статус", "Номер аудитории", "Адрес"
            ])
            for i, row in enumerate(rows):
                for j, val in enumerate(row):
                    self.table.setItem(i, j, QTableWidgetItem(str(val)))
            cur.close()
            conn.close()
            logger.info("Загружены данные аудиторий")
        except Exception as e:
            logger.error(f"Ошибка загрузки: {e}")
            QMessageBox.critical(self, "Ошибка", str(e))

    def search_audience(self):
        keyword = self.search_box.text().strip()
        try:
            conn = get_connection()
            cur = conn.cursor()
            cur.execute("""
                SELECT * FROM public."Audience"
                WHERE "Address" ILIKE %s
                ORDER BY "ID_audience"
            """, (f"%{keyword}%",))
            rows = cur.fetchall()
            self.table.setRowCount(len(rows))
            for i, row in enumerate(rows):
                for j, val in enumerate(row):
                    self.table.setItem(i, j, QTableWidgetItem(str(val)))
            cur.close()
            conn.close()
            logger.info(f"Поиск аудиторий по адресу: {keyword}")
        except Exception as e:
            logger.error(f"Ошибка поиска: {e}")
            QMessageBox.critical(self, "Ошибка", str(e))

    def add_audience(self):
        dialog = AudienceDialog()
        if dialog.exec_() == QDialog.Accepted:
            try:
                conn = get_connection()
                cur = conn.cursor()
                cur.execute("""
                    INSERT INTO public."Audience" ("Type", "Status", "Audience_number", "Address")
                    VALUES (%s, %s, %s, %s)
                """, dialog.get_data())
                conn.commit()
                cur.close()
                conn.close()
                self.load_data()
                logger.info("Добавлена аудитория")
            except Exception as e:
                logger.error(f"Ошибка добавления: {e}")
                QMessageBox.critical(self, "Ошибка", str(e))

    def edit_audience(self):
        selected = self.table.currentRow()
        if selected < 0:
            QMessageBox.warning(self, "Внимание", "Выберите запись для редактирования")
            return

        audience_id = self.table.item(selected, 0).text()
        current_data = [self.table.item(selected, i).text() for i in range(1, 5)]

        dialog = AudienceDialog(*current_data)
        if dialog.exec_() == QDialog.Accepted:
            try:
                conn = get_connection()
                cur = conn.cursor()
                cur.execute("""
                    UPDATE public."Audience"
                    SET "Type" = %s, "Status" = %s, "Audience_number" = %s, "Address" = %s
                    WHERE "ID_audience" = %s
                """, (*dialog.get_data(), audience_id))
                conn.commit()
                cur.close()
                conn.close()
                self.load_data()
                logger.info(f"Обновлена аудитория ID={audience_id}")
            except Exception as e:
                logger.error(f"Ошибка редактирования: {e}")
                QMessageBox.critical(self, "Ошибка", str(e))

    def delete_audience(self):
        selected = self.table.currentRow()
        if selected < 0:
            QMessageBox.warning(self, "Внимание", "Выберите запись для удаления")
            return

        audience_id = self.table.item(selected, 0).text()
        confirm = QMessageBox.question(
            self, "Подтверждение",
            f"Удалить аудиторию ID {audience_id}?",
            QMessageBox.Yes | QMessageBox.No
        )

        if confirm == QMessageBox.Yes:
            try:
                conn = get_connection()
                cur = conn.cursor()
                cur.execute('DELETE FROM public."Audience" WHERE "ID_audience" = %s', (audience_id,))
                conn.commit()
                cur.close()
                conn.close()
                self.load_data()
                logger.info(f"Аудитория ID={audience_id} удалена")
            except Exception as e:
                logger.error(f"Ошибка удаления: {e}")
                QMessageBox.critical(self, "Ошибка", str(e))


class AudienceDialog(QDialog):
    def __init__(self, type_="", status="", number="", address=""):
        super().__init__()
        self.setWindowTitle("Данные аудитории")
        layout = QFormLayout(self)

        self.type_input = QLineEdit(type_)
        self.status_input = QLineEdit(status)
        self.number_input = QLineEdit(number)
        self.address_input = QLineEdit(address)

        layout.addRow("Тип:", self.type_input)
        layout.addRow("Статус:", self.status_input)
        layout.addRow("Номер аудитории:", self.number_input)
        layout.addRow("Адрес:", self.address_input)

        buttons = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        buttons.accepted.connect(self.accept)
        buttons.rejected.connect(self.reject)
        layout.addWidget(buttons)

    def get_data(self):
        return (
            self.type_input.text(),
            self.status_input.text(),
            int(self.number_input.text()),
            self.address_input.text()
        )
