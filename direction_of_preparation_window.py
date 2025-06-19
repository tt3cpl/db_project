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
)
from db import get_connection
from logger import logger


class DirectionOfPreparationWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Таблица: Направления подготовки")
        self.setGeometry(100, 100, 600, 300)

        self.layout = QVBoxLayout()
        self.setLayout(self.layout)

        self.search_box = QLineEdit()
        self.search_box.setPlaceholderText("Поиск по названию направления...")
        self.search_box.textChanged.connect(self.search_directions)
        self.layout.addWidget(self.search_box)

        self.table = QTableWidget()
        self.layout.addWidget(self.table)

        btns = QHBoxLayout()

        refresh_btn = QPushButton("Обновить")
        refresh_btn.clicked.connect(self.load_data)
        btns.addWidget(refresh_btn)

        add_btn = QPushButton("Добавить")
        add_btn.clicked.connect(self.add_direction)
        btns.addWidget(add_btn)

        edit_btn = QPushButton("Редактировать")
        edit_btn.clicked.connect(self.edit_direction)
        btns.addWidget(edit_btn)

        delete_btn = QPushButton("Удалить")
        delete_btn.clicked.connect(self.delete_direction)
        btns.addWidget(delete_btn)

        self.layout.addLayout(btns)
        self.load_data()

    def load_data(self):
        try:
            conn = get_connection()
            cur = conn.cursor()
            cur.execute(
                'SELECT * FROM public."Direction_of_preparation" ORDER BY "ID_direction"'
            )
            rows = cur.fetchall()
            self.table.setRowCount(len(rows))
            self.table.setColumnCount(2)
            self.table.setHorizontalHeaderLabels(["ID", "Название направления"])
            for i, row in enumerate(rows):
                for j, val in enumerate(row):
                    self.table.setItem(i, j, QTableWidgetItem(str(val)))
            cur.close()
            conn.close()
            logger.info("Загружены данные направлений подготовки")
        except Exception as e:
            logger.error(f"Ошибка загрузки данных: {e}")
            QMessageBox.critical(self, "Ошибка", str(e))

    def search_directions(self):
        keyword = self.search_box.text().strip()
        try:
            conn = get_connection()
            cur = conn.cursor()
            cur.execute(
                """
                SELECT * FROM public."Direction_of_preparation"
                WHERE "Destination_name" ILIKE %s
                ORDER BY "ID_direction"
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
            logger.info(f"Поиск направления: {keyword}")
        except Exception as e:
            logger.error(f"Ошибка поиска: {e}")
            QMessageBox.critical(self, "Ошибка", str(e))

    def add_direction(self):
        dialog = DirectionDialog()
        if dialog.exec_() == QDialog.Accepted:
            try:
                conn = get_connection()
                cur = conn.cursor()
                cur.execute(
                    """
                    INSERT INTO public."Direction_of_preparation" ("Destination_name")
                    VALUES (%s)
                """,
                    dialog.get_data(),
                )
                conn.commit()
                cur.close()
                conn.close()
                self.load_data()
                logger.info("Добавлено направление подготовки")
            except Exception as e:
                logger.error(f"Ошибка добавления: {e}")
                QMessageBox.critical(self, "Ошибка", str(e))

    def edit_direction(self):
        selected = self.table.currentRow()
        if selected < 0:
            QMessageBox.warning(
                self, "Внимание", "Выберите направление для редактирования"
            )
            return

        direction_id = self.table.item(selected, 0).text()
        current_name = self.table.item(selected, 1).text()

        dialog = DirectionDialog(current_name)
        if dialog.exec_() == QDialog.Accepted:
            try:
                conn = get_connection()
                cur = conn.cursor()
                cur.execute(
                    """
                    UPDATE public."Direction_of_preparation"
                    SET "Destination_name" = %s
                    WHERE "ID_direction" = %s
                """,
                    (dialog.get_data()[0], direction_id),
                )
                conn.commit()
                cur.close()
                conn.close()
                self.load_data()
                logger.info(f"Отредактировано направление ID={direction_id}")
            except Exception as e:
                logger.error(f"Ошибка редактирования: {e}")
                QMessageBox.critical(self, "Ошибка", str(e))

    def delete_direction(self):
        selected = self.table.currentRow()
        if selected < 0:
            QMessageBox.warning(self, "Внимание", "Выберите направление для удаления")
            return

        direction_id = self.table.item(selected, 0).text()
        confirm = QMessageBox.question(
            self,
            "Подтверждение",
            f"Удалить направление ID {direction_id}?",
            QMessageBox.Yes | QMessageBox.No,
        )

        if confirm == QMessageBox.Yes:
            try:
                conn = get_connection()
                cur = conn.cursor()
                cur.execute(
                    'DELETE FROM public."Direction_of_preparation" WHERE "ID_direction" = %s',
                    (direction_id,),
                )
                conn.commit()
                cur.close()
                conn.close()
                self.load_data()
                logger.info(f"Удалено направление ID={direction_id}")
            except Exception as e:
                logger.error(f"Ошибка удаления: {e}")
                QMessageBox.critical(self, "Ошибка", str(e))


class DirectionDialog(QDialog):
    def __init__(self, name=""):
        super().__init__()
        self.setWindowTitle("Данные направления")
        layout = QFormLayout(self)

        self.name_input = QLineEdit(name)
        layout.addRow("Название направления:", self.name_input)

        buttons = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        buttons.accepted.connect(self.accept)
        buttons.rejected.connect(self.reject)
        layout.addWidget(buttons)

    def get_data(self):
        return (self.name_input.text(),)
