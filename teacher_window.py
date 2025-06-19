from PyQt5.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QPushButton,
    QTableWidget,
    QTableWidgetItem,
    QLineEdit,
    QLabel,
    QHBoxLayout,
    QMessageBox,
    QDialog,
    QFormLayout,
    QDialogButtonBox,
)
from db import get_connection
from logger import logger


class TeacherWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Таблица: Преподаватели")
        self.setGeometry(100, 100, 800, 400)

        self.layout = QVBoxLayout()
        self.setLayout(self.layout)

        self.search_box = QLineEdit()
        self.search_box.setPlaceholderText("Поиск по фамилии...")
        self.search_box.textChanged.connect(self.search_teachers)
        self.layout.addWidget(self.search_box)

        self.table = QTableWidget()
        self.layout.addWidget(self.table)

        btns = QHBoxLayout()

        refresh_btn = QPushButton("Обновить")
        refresh_btn.clicked.connect(self.load_data)
        btns.addWidget(refresh_btn)

        add_btn = QPushButton("Добавить")
        add_btn.clicked.connect(self.add_teacher)
        btns.addWidget(add_btn)

        edit_btn = QPushButton("Редактировать")
        edit_btn.clicked.connect(self.edit_teacher)
        btns.addWidget(edit_btn)

        delete_btn = QPushButton("Удалить")
        delete_btn.clicked.connect(self.delete_teacher)
        btns.addWidget(delete_btn)

        self.layout.addLayout(btns)
        self.load_data()

    def load_data(self):
        try:
            conn = get_connection()
            cur = conn.cursor()
            cur.execute('SELECT * FROM public."Teacher" ORDER BY "ID_teacher"')
            rows = cur.fetchall()
            self.table.setRowCount(len(rows))
            self.table.setColumnCount(6)
            self.table.setHorizontalHeaderLabels(
                ["ID", "Фамилия", "Имя", "Отчество", "Телефон", "Email"]
            )
            for i, row in enumerate(rows):
                for j, val in enumerate(row):
                    self.table.setItem(i, j, QTableWidgetItem(str(val)))
            cur.close()
            conn.close()
            logger.info("Загружены данные преподавателей")
        except Exception as e:
            logger.error(f"Ошибка загрузки данных: {e}")
            QMessageBox.critical(self, "Ошибка", str(e))

    def search_teachers(self):
        keyword = self.search_box.text().strip()
        try:
            conn = get_connection()
            cur = conn.cursor()
            cur.execute(
                """
                SELECT * FROM public."Teacher"
                WHERE "Surname" ILIKE %s
                ORDER BY "ID_teacher"
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
            logger.info(f"Поиск преподавателей: {keyword}")
        except Exception as e:
            logger.error(f"Ошибка поиска: {e}")
            QMessageBox.critical(self, "Ошибка", str(e))

    def add_teacher(self):
        dialog = TeacherDialog()
        if dialog.exec_() == QDialog.Accepted:
            try:
                conn = get_connection()
                cur = conn.cursor()
                cur.execute(
                    """
                    INSERT INTO public."Teacher" ("Surname", "Name", "Patronymic", "Phone_number", "E-mail")
                    VALUES (%s, %s, %s, %s, %s)
                """,
                    dialog.get_data(),
                )
                conn.commit()
                cur.close()
                conn.close()
                self.load_data()
                logger.info("Добавлен преподаватель")
            except Exception as e:
                logger.error(f"Ошибка добавления: {e}")
                QMessageBox.critical(self, "Ошибка", str(e))

    def edit_teacher(self):
        selected = self.table.currentRow()
        if selected < 0:
            QMessageBox.warning(
                self, "Внимание", "Выберите преподавателя для редактирования"
            )
            return

        teacher_id = self.table.item(selected, 0).text()
        current_data = [self.table.item(selected, i).text() for i in range(1, 6)]

        dialog = TeacherDialog(*current_data)
        if dialog.exec_() == QDialog.Accepted:
            try:
                conn = get_connection()
                cur = conn.cursor()
                cur.execute(
                    """
                    UPDATE public."Teacher"
                    SET "Surname" = %s, "Name" = %s, "Patronymic" = %s,
                        "Phone_number" = %s, "E-mail" = %s
                    WHERE "ID_teacher" = %s
                """,
                    (*dialog.get_data(), teacher_id),
                )
                conn.commit()
                cur.close()
                conn.close()
                self.load_data()
                logger.info(f"Отредактирован преподаватель ID={teacher_id}")
            except Exception as e:
                logger.error(f"Ошибка редактирования: {e}")
                QMessageBox.critical(self, "Ошибка", str(e))

    def delete_teacher(self):
        selected = self.table.currentRow()
        if selected < 0:
            QMessageBox.warning(self, "Внимание", "Выберите преподавателя для удаления")
            return

        teacher_id = self.table.item(selected, 0).text()
        confirm = QMessageBox.question(
            self,
            "Подтверждение",
            f"Удалить преподавателя ID {teacher_id}?",
            QMessageBox.Yes | QMessageBox.No,
        )

        if confirm == QMessageBox.Yes:
            try:
                conn = get_connection()
                cur = conn.cursor()
                cur.execute(
                    'DELETE FROM public."Teacher" WHERE "ID_teacher" = %s',
                    (teacher_id,),
                )
                conn.commit()
                cur.close()
                conn.close()
                self.load_data()
                logger.info(f"Удалён преподаватель ID={teacher_id}")
            except Exception as e:
                logger.error(f"Ошибка удаления: {e}")
                QMessageBox.critical(self, "Ошибка", str(e))


class TeacherDialog(QDialog):
    def __init__(self, surname="", name="", patronymic="", phone="", email=""):
        super().__init__()
        self.setWindowTitle("Данные преподавателя")
        layout = QFormLayout(self)

        self.surname = QLineEdit(surname)
        self.name = QLineEdit(name)
        self.patronymic = QLineEdit(patronymic)
        self.phone = QLineEdit(phone)
        self.email = QLineEdit(email)

        layout.addRow("Фамилия:", self.surname)
        layout.addRow("Имя:", self.name)
        layout.addRow("Отчество:", self.patronymic)
        layout.addRow("Телефон:", self.phone)
        layout.addRow("Email:", self.email)

        buttons = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        buttons.accepted.connect(self.accept)
        buttons.rejected.connect(self.reject)
        layout.addWidget(buttons)

    def get_data(self):
        return (
            self.surname.text(),
            self.name.text(),
            self.patronymic.text(),
            self.phone.text(),
            self.email.text(),
        )
