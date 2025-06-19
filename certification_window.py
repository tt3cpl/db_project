from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QPushButton, QTableWidget, QTableWidgetItem,
    QLineEdit, QHBoxLayout, QMessageBox, QDialog, QFormLayout, QDialogButtonBox
)
from db import get_connection
from logger import logger


class CertificationWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Таблица: Аттестации")
        self.setGeometry(100, 100, 700, 350)

        self.layout = QVBoxLayout()
        self.setLayout(self.layout)

        self.search_box = QLineEdit()
        self.search_box.setPlaceholderText("Поиск по типу аттестации...")
        self.search_box.textChanged.connect(self.search_certifications)
        self.layout.addWidget(self.search_box)

        self.table = QTableWidget()
        self.layout.addWidget(self.table)

        btns = QHBoxLayout()

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

        self.layout.addLayout(btns)
        self.load_data()

    def load_data(self):
        try:
            conn = get_connection()
            cur = conn.cursor()
            cur.execute('SELECT * FROM public."Certification" ORDER BY "ID_certification"')
            rows = cur.fetchall()
            self.table.setRowCount(len(rows))
            self.table.setColumnCount(5)
            self.table.setHorizontalHeaderLabels([
                "ID", "Оценка", "ID дисциплины", "Тип аттестации", "ID студента"
            ])
            for i, row in enumerate(rows):
                for j, val in enumerate(row):
                    self.table.setItem(i, j, QTableWidgetItem(str(val)))
            cur.close()
            conn.close()
            logger.info("Загружены данные аттестаций")
        except Exception as e:
            logger.error(f"Ошибка загрузки данных: {e}")
            QMessageBox.critical(self, "Ошибка", str(e))

    def search_certifications(self):
        keyword = self.search_box.text().strip()
        try:
            conn = get_connection()
            cur = conn.cursor()
            cur.execute("""
                SELECT * FROM public."Certification"
                WHERE "Certification_type" ILIKE %s
                ORDER BY "ID_certification"
            """, (f"%{keyword}%",))
            rows = cur.fetchall()
            self.table.setRowCount(len(rows))
            for i, row in enumerate(rows):
                for j, val in enumerate(row):
                    self.table.setItem(i, j, QTableWidgetItem(str(val)))
            cur.close()
            conn.close()
            logger.info(f"Поиск аттестаций: {keyword}")
        except Exception as e:
            logger.error(f"Ошибка поиска: {e}")
            QMessageBox.critical(self, "Ошибка", str(e))

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
                conn.commit()
                cur.close()
                conn.close()
                self.load_data()
                logger.info("Добавлена аттестация")
            except Exception as e:
                logger.error(f"Ошибка добавления: {e}")
                QMessageBox.critical(self, "Ошибка", str(e))

    def edit_certification(self):
        selected = self.table.currentRow()
        if selected < 0:
            QMessageBox.warning(self, "Внимание", "Выберите запись для редактирования")
            return

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
                conn.commit()
                cur.close()
                conn.close()
                self.load_data()
                logger.info(f"Отредактирована аттестация ID={certification_id}")
            except Exception as e:
                logger.error(f"Ошибка редактирования: {e}")
                QMessageBox.critical(self, "Ошибка", str(e))

    def delete_certification(self):
        selected = self.table.currentRow()
        if selected < 0:
            QMessageBox.warning(self, "Внимание", "Выберите запись для удаления")
            return

        certification_id = self.table.item(selected, 0).text()
        confirm = QMessageBox.question(
            self, "Подтверждение",
            f"Удалить аттестацию ID {certification_id}?",
            QMessageBox.Yes | QMessageBox.No
        )

        if confirm == QMessageBox.Yes:
            try:
                conn = get_connection()
                cur = conn.cursor()
                cur.execute('DELETE FROM public."Certification" WHERE "ID_certification" = %s', (certification_id,))
                conn.commit()
                cur.close()
                conn.close()
                self.load_data()
                logger.info(f"Удалена аттестация ID={certification_id}")
            except Exception as e:
                logger.error(f"Ошибка удаления: {e}")
                QMessageBox.critical(self, "Ошибка", str(e))


class CertificationDialog(QDialog):
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

        buttons = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        buttons.accepted.connect(self.accept)
        buttons.rejected.connect(self.reject)
        layout.addWidget(buttons)

    def get_data(self):
        return (
            int(self.grade_input.text()),
            int(self.discipline_input.text()),
            self.cert_type_input.text(),
            int(self.student_input.text())
        )
