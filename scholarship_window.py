from PyQt5.QtWidgets import (
<<<<<<< HEAD
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
=======
    QWidget, QVBoxLayout, QPushButton, QTableWidget, QTableWidgetItem,
    QLineEdit, QHBoxLayout, QMessageBox, QDialog, QFormLayout, QDialogButtonBox
>>>>>>> d8d353c4260bb55e6728d0a2be9f2b8092c1954a
)
from db import get_connection
from logger import logger

<<<<<<< HEAD

=======
>>>>>>> d8d353c4260bb55e6728d0a2be9f2b8092c1954a
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
<<<<<<< HEAD
            cur.execute(
                """
                SELECT * FROM public."Scholarship"
                WHERE "Type_of_scholarship" ILIKE %s
                ORDER BY "ID_scholarships"
            """,
                (f"%{keyword}%",),
            )
=======
            cur.execute("""
                SELECT * FROM public."Scholarship"
                WHERE "Type_of_scholarship" ILIKE %s
                ORDER BY "ID_scholarships"
            """, (f"%{keyword}%",))
>>>>>>> d8d353c4260bb55e6728d0a2be9f2b8092c1954a
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
<<<<<<< HEAD
                cur.execute(
                    """
                    INSERT INTO public."Scholarship" ("Type_of_scholarship", "Size")
                    VALUES (%s, %s)
                """,
                    dialog.get_data(),
                )
=======
                cur.execute("""
                    INSERT INTO public."Scholarship" ("Type_of_scholarship", "Size")
                    VALUES (%s, %s)
                """, dialog.get_data())
>>>>>>> d8d353c4260bb55e6728d0a2be9f2b8092c1954a
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
<<<<<<< HEAD
            QMessageBox.warning(
                self, "Внимание", "Выберите стипендию для редактирования"
            )
=======
            QMessageBox.warning(self, "Внимание", "Выберите стипендию для редактирования")
>>>>>>> d8d353c4260bb55e6728d0a2be9f2b8092c1954a
            return

        scholarship_id = self.table.item(selected, 0).text()
        current_type = self.table.item(selected, 1).text()
        current_size = self.table.item(selected, 2).text()

        dialog = ScholarshipDialog(current_type, current_size)
        if dialog.exec_() == QDialog.Accepted:
            try:
                conn = get_connection()
                cur = conn.cursor()
<<<<<<< HEAD
                cur.execute(
                    """
                    UPDATE public."Scholarship"
                    SET "Type_of_scholarship" = %s, "Size" = %s
                    WHERE "ID_scholarships" = %s
                """,
                    (*dialog.get_data(), scholarship_id),
                )
=======
                cur.execute("""
                    UPDATE public."Scholarship"
                    SET "Type_of_scholarship" = %s, "Size" = %s
                    WHERE "ID_scholarships" = %s
                """, (*dialog.get_data(), scholarship_id))
>>>>>>> d8d353c4260bb55e6728d0a2be9f2b8092c1954a
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
<<<<<<< HEAD
            self,
            "Подтверждение",
            f"Удалить стипендию ID {scholarship_id}?",
            QMessageBox.Yes | QMessageBox.No,
=======
            self, "Подтверждение",
            f"Удалить стипендию ID {scholarship_id}?",
            QMessageBox.Yes | QMessageBox.No
>>>>>>> d8d353c4260bb55e6728d0a2be9f2b8092c1954a
        )

        if confirm == QMessageBox.Yes:
            try:
                conn = get_connection()
                cur = conn.cursor()
<<<<<<< HEAD
                cur.execute(
                    'DELETE FROM public."Scholarship" WHERE "ID_scholarships" = %s',
                    (scholarship_id,),
                )
=======
                cur.execute('DELETE FROM public."Scholarship" WHERE "ID_scholarships" = %s', (scholarship_id,))
>>>>>>> d8d353c4260bb55e6728d0a2be9f2b8092c1954a
                conn.commit()
                cur.close()
                conn.close()
                self.load_data()
                logger.info(f"Удалена стипендия ID={scholarship_id}")
            except Exception as e:
                logger.error(f"Ошибка удаления: {e}")
                QMessageBox.critical(self, "Ошибка", str(e))


class ScholarshipDialog(QDialog):
<<<<<<< HEAD
    SCHOLARSHIP_TYPES = [
        "-",
        "ГАС",
        "СГАС",
        "Повышенная за отличную учебу",
        "Повышенная студентам 1 курса",
        "ПГАС за достижения в учебной деятельности",
        "ПГАС за достижения в научной деятельности",
        "ПГАС за достижения в спортивной деятельности",
        "ПГАС за достижения в общественной деятельности",
        "ПГАС за достижения в культурной деятельности",
    ]

    def __init__(self, scholarship_type="-", size=""):
=======
    def __init__(self, scholarship_type="", size=""):
>>>>>>> d8d353c4260bb55e6728d0a2be9f2b8092c1954a
        super().__init__()
        self.setWindowTitle("Данные стипендии")
        layout = QFormLayout(self)

<<<<<<< HEAD
        self.type_combo = QComboBox()
        self.type_combo.addItems(self.SCHOLARSHIP_TYPES)
        if scholarship_type in self.SCHOLARSHIP_TYPES:
            self.type_combo.setCurrentText(scholarship_type)
        else:
            self.type_combo.setCurrentIndex(0)

        self.size_input = QLineEdit(size)

        layout.addRow("Вид стипендии:", self.type_combo)
=======
        self.type_input = QLineEdit(scholarship_type)
        self.size_input = QLineEdit(size)

        layout.addRow("Тип стипендии:", self.type_input)
>>>>>>> d8d353c4260bb55e6728d0a2be9f2b8092c1954a
        layout.addRow("Размер:", self.size_input)

        buttons = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        buttons.accepted.connect(self.accept)
        buttons.rejected.connect(self.reject)
        layout.addWidget(buttons)

    def get_data(self):
<<<<<<< HEAD
        return (self.type_combo.currentText(), int(self.size_input.text()))
=======
        return (self.type_input.text(), int(self.size_input.text()))
>>>>>>> d8d353c4260bb55e6728d0a2be9f2b8092c1954a
