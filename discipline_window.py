from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QPushButton, QTableWidget, QTableWidgetItem,
    QLineEdit, QLabel, QHBoxLayout, QMessageBox, QDialog, QFormLayout, QDialogButtonBox
)
from db import get_connection
from logger import logger

class DisciplineWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Таблица: Дисциплины")
        self.setGeometry(100, 100, 1000, 400)

        self.layout = QVBoxLayout()
        self.setLayout(self.layout)

        self.search_box = QLineEdit()
        self.search_box.setPlaceholderText("Поиск по названию дисциплины...")
        self.search_box.textChanged.connect(self.search_disciplines)
        self.layout.addWidget(self.search_box)

        self.table = QTableWidget()
        self.layout.addWidget(self.table)

        btns = QHBoxLayout()

        refresh_btn = QPushButton("Обновить")
        refresh_btn.clicked.connect(self.load_data)
        btns.addWidget(refresh_btn)

        add_btn = QPushButton("Добавить")
        add_btn.clicked.connect(self.add_discipline)
        btns.addWidget(add_btn)

        edit_btn = QPushButton("Редактировать")
        edit_btn.clicked.connect(self.edit_discipline)
        btns.addWidget(edit_btn)

        delete_btn = QPushButton("Удалить")
        delete_btn.clicked.connect(self.delete_discipline)
        btns.addWidget(delete_btn)

        self.layout.addLayout(btns)
        self.load_data()

    def load_data(self):
        try:
            conn = get_connection()
            cur = conn.cursor()
            cur.execute('SELECT * FROM public."Discipline" ORDER BY "ID_disciplines"')
            rows = cur.fetchall()
            self.table.setRowCount(len(rows))
            self.table.setColumnCount(7)
            self.table.setHorizontalHeaderLabels([
                "ID", "Название", "Лекции", "Лабораторные", "Практики", "Аттестация", "Формат"
            ])
            for i, row in enumerate(rows):
                for j, val in enumerate(row):
                    self.table.setItem(i, j, QTableWidgetItem(str(val)))
            cur.close()
            conn.close()
            logger.info("Загружены данные дисциплин")
        except Exception as e:
            logger.error(f"Ошибка загрузки данных: {e}")
            QMessageBox.critical(self, "Ошибка", str(e))

    def search_disciplines(self):
        keyword = self.search_box.text().strip()
        try:
            conn = get_connection()
            cur = conn.cursor()
            cur.execute("""
                SELECT * FROM public."Discipline"
                WHERE "Discipline_name" ILIKE %s
                ORDER BY "ID_disciplines"
            """, (f"%{keyword}%",))
            rows = cur.fetchall()
            self.table.setRowCount(len(rows))
            for i, row in enumerate(rows):
                for j, val in enumerate(row):
                    self.table.setItem(i, j, QTableWidgetItem(str(val)))
            cur.close()
            conn.close()
            logger.info(f"Поиск дисциплин: {keyword}")
        except Exception as e:
            logger.error(f"Ошибка поиска: {e}")
            QMessageBox.critical(self, "Ошибка", str(e))

    def add_discipline(self):
        dialog = DisciplineDialog()
        if dialog.exec_() == QDialog.Accepted:
            try:
                conn = get_connection()
                cur = conn.cursor()
                cur.execute("""
                    INSERT INTO public."Discipline" (
                        "Discipline_name", "Lek_hours", "Lab_hours", "Prak_hours",
                        "Type_of_certification", "Формат_реализации"
                    )
                    VALUES (%s, %s, %s, %s, %s, %s)
                """, dialog.get_data())
                conn.commit()
                cur.close()
                conn.close()
                self.load_data()
                logger.info("Добавлена дисциплина")
            except Exception as e:
                logger.error(f"Ошибка добавления: {e}")
                QMessageBox.critical(self, "Ошибка", str(e))

    def edit_discipline(self):
        selected = self.table.currentRow()
        if selected < 0:
            QMessageBox.warning(self, "Внимание", "Выберите дисциплину для редактирования")
            return

        discipline_id = self.table.item(selected, 0).text()
        current_data = [self.table.item(selected, i).text() for i in range(1, 7)]

        dialog = DisciplineDialog(*current_data)
        if dialog.exec_() == QDialog.Accepted:
            try:
                conn = get_connection()
                cur = conn.cursor()
                cur.execute("""
                    UPDATE public."Discipline"
                    SET 
                        "Discipline_name" = %s,
                        "Lek_hours" = %s,
                        "Lab_hours" = %s,
                        "Prak_hours" = %s,
                        "Type_of_certification" = %s,
                        "Формат_реализации" = %s
                    WHERE "ID_disciplines" = %s
                """, (*dialog.get_data(), discipline_id))
                conn.commit()
                cur.close()
                conn.close()
                self.load_data()
                logger.info(f"Отредактирована дисциплина ID={discipline_id}")
            except Exception as e:
                logger.error(f"Ошибка редактирования: {e}")
                QMessageBox.critical(self, "Ошибка", str(e))

    def delete_discipline(self):
        selected = self.table.currentRow()
        if selected < 0:
            QMessageBox.warning(self, "Внимание", "Выберите дисциплину для удаления")
            return

        discipline_id = self.table.item(selected, 0).text()
        confirm = QMessageBox.question(
            self, "Подтверждение",
            f"Удалить дисциплину ID {discipline_id}?",
            QMessageBox.Yes | QMessageBox.No
        )

        if confirm == QMessageBox.Yes:
            try:
                conn = get_connection()
                cur = conn.cursor()
                cur.execute('DELETE FROM public."Discipline" WHERE "ID_disciplines" = %s', (discipline_id,))
                conn.commit()
                cur.close()
                conn.close()
                self.load_data()
                logger.info(f"Удалена дисциплина ID={discipline_id}")
            except Exception as e:
                logger.error(f"Ошибка удаления: {e}")
                QMessageBox.critical(self, "Ошибка", str(e))


class DisciplineDialog(QDialog):
    def __init__(self, name="", lek="", lab="", prak="", cert="", format_=""):
        super().__init__()
        self.setWindowTitle("Данные дисциплины")
        layout = QFormLayout(self)

        self.name = QLineEdit(name)
        self.lek = QLineEdit(lek)
        self.lab = QLineEdit(lab)
        self.prak = QLineEdit(prak)
        self.cert = QLineEdit(cert)
        self.format = QLineEdit(format_)

        layout.addRow("Название:", self.name)
        layout.addRow("Лекционные часы:", self.lek)
        layout.addRow("Лабораторные часы:", self.lab)
        layout.addRow("Практические часы:", self.prak)
        layout.addRow("Тип аттестации:", self.cert)
        layout.addRow("Формат реализации:", self.format)

        buttons = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        buttons.accepted.connect(self.accept)
        buttons.rejected.connect(self.reject)
        layout.addWidget(buttons)

    def get_data(self):
        return (
            self.name.text(),
            int(self.lek.text()),
            int(self.lab.text()),
            int(self.prak.text()),
            self.cert.text(),
            self.format.text()
        )
