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
    QComboBox,
)
from db import get_connection
from logger import logger


class OPWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Таблица: Образовательные программы (ОП)")
        self.setGeometry(100, 100, 1000, 400)

        self.layout = QVBoxLayout()
        self.setLayout(self.layout)

        self.table = QTableWidget()
        self.layout.addWidget(self.table)

        btns = QHBoxLayout()

        refresh_btn = QPushButton("Обновить")
        refresh_btn.clicked.connect(self.load_data)
        btns.addWidget(refresh_btn)

        add_btn = QPushButton("Добавить")
        add_btn.clicked.connect(self.add_op)
        btns.addWidget(add_btn)

        edit_btn = QPushButton("Редактировать")
        edit_btn.clicked.connect(self.edit_op)
        btns.addWidget(edit_btn)

        delete_btn = QPushButton("Удалить")
        delete_btn.clicked.connect(self.delete_op)
        btns.addWidget(delete_btn)

        self.layout.addLayout(btns)
        self.load_data()

    def load_data(self):
        try:
            conn = get_connection()
            cur = conn.cursor()
            cur.execute(
                """
                SELECT op."ID_OP", d."Destination_name", u."Name_of_the_department",
                       op."OP_name", op."Implementation_format", op."Hours_volume"
                FROM "OP" op
                JOIN "Direction_of_preparation" d ON op."ID_directions" = d."ID_direction"
                JOIN "University_division" u ON op."ID_divisions" = u."ID_divisions"
                ORDER BY op."ID_OP"
            """
            )
            rows = cur.fetchall()
            self.table.setRowCount(len(rows))
            self.table.setColumnCount(6)
            self.table.setHorizontalHeaderLabels(
                ["ID", "Направление", "Подразделение", "Название ОП", "Формат", "Часы"]
            )
            for i, row in enumerate(rows):
                for j, val in enumerate(row):
                    self.table.setItem(i, j, QTableWidgetItem(str(val)))
            cur.close()
            conn.close()
            logger.info("Загружены данные ОП")
        except Exception as e:
            logger.error(f"Ошибка загрузки данных ОП: {e}")
            QMessageBox.critical(self, "Ошибка", str(e))

    def add_op(self):
        dialog = OPDialog()
        if dialog.exec_() == QDialog.Accepted:
            try:
                conn = get_connection()
                cur = conn.cursor()
                cur.execute(
                    """
                    INSERT INTO "OP" (
                        "ID_directions", "ID_divisions", "OP_name", "Implementation_format", "Hours_volume"
                    ) VALUES (%s, %s, %s, %s, %s)
                """,
                    dialog.get_data(),
                )
                conn.commit()
                cur.close()
                conn.close()
                self.load_data()
                logger.info("Добавлена новая ОП")
            except Exception as e:
                logger.error(f"Ошибка добавления ОП: {e}")
                QMessageBox.critical(self, "Ошибка", str(e))

    def edit_op(self):
        selected = self.table.currentRow()
        if selected < 0:
            QMessageBox.warning(self, "Внимание", "Выберите запись для редактирования")
            return

        op_id = self.table.item(selected, 0).text()
        current_data = [self.table.item(selected, i).text() for i in range(1, 6)]

        dialog = OPDialog(*current_data)
        if dialog.exec_() == QDialog.Accepted:
            try:
                conn = get_connection()
                cur = conn.cursor()
                cur.execute(
                    """
                    UPDATE "OP"
                    SET "ID_directions" = %s,
                        "ID_divisions" = %s,
                        "OP_name" = %s,
                        "Implementation_format" = %s,
                        "Hours_volume" = %s
                    WHERE "ID_OP" = %s
                """,
                    (*dialog.get_data(), op_id),
                )
                conn.commit()
                cur.close()
                conn.close()
                self.load_data()
                logger.info(f"Отредактирована ОП ID={op_id}")
            except Exception as e:
                logger.error(f"Ошибка редактирования ОП: {e}")
                QMessageBox.critical(self, "Ошибка", str(e))

    def delete_op(self):
        selected = self.table.currentRow()
        if selected < 0:
            QMessageBox.warning(self, "Внимание", "Выберите запись для удаления")
            return

        op_id = self.table.item(selected, 0).text()
        confirm = QMessageBox.question(
            self,
            "Подтверждение",
            f"Удалить ОП ID {op_id}?",
            QMessageBox.Yes | QMessageBox.No,
        )
        if confirm == QMessageBox.Yes:
            try:
                conn = get_connection()
                cur = conn.cursor()
                cur.execute('DELETE FROM "OP" WHERE "ID_OP" = %s', (op_id,))
                conn.commit()
                cur.close()
                conn.close()
                self.load_data()
                logger.info(f"Удалена ОП ID={op_id}")
            except Exception as e:
                logger.error(f"Ошибка удаления ОП: {e}")
                QMessageBox.critical(self, "Ошибка", str(e))


class OPDialog(QDialog):
    def __init__(
        self, direction_name="", division_name="", op_name="", impl_format="", hours=""
    ):
        super().__init__()
        self.setWindowTitle("Данные ОП")
        layout = QFormLayout(self)

        self.direction_combo = QComboBox()
        self.direction_map = {}
        self.load_directions()

        self.division_combo = QComboBox()
        self.division_map = {}
        self.load_divisions()

        self.op_name = QLineEdit(op_name)

        self.impl_format = QComboBox()
        formats = ["Очно", "Дистанционно", "Смешанный"]
        self.impl_format.addItems(formats)
        if impl_format in formats:
            self.impl_format.setCurrentText(impl_format)
        else:
            self.impl_format.setCurrentIndex(0)

        self.hours = QLineEdit(hours)

        layout.addRow("Направление:", self.direction_combo)
        layout.addRow("Подразделение:", self.division_combo)
        layout.addRow("Название ОП:", self.op_name)
        layout.addRow("Формат реализации:", self.impl_format)
        layout.addRow("Объём часов:", self.hours)

        buttons = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        buttons.accepted.connect(self.accept)
        buttons.rejected.connect(self.reject)
        layout.addWidget(buttons)

        if direction_name:
            self.direction_combo.setCurrentText(direction_name)
        if division_name:
            self.division_combo.setCurrentText(division_name)

    def load_directions(self):
        try:
            conn = get_connection()
            cur = conn.cursor()
            cur.execute(
                'SELECT "ID_direction", "Destination_name" FROM "Direction_of_preparation"'
            )
            for row in cur.fetchall():
                self.direction_map[row[1]] = row[0]
                self.direction_combo.addItem(row[1])
            cur.close()
            conn.close()
        except Exception as e:
            QMessageBox.critical(self, "Ошибка загрузки направлений", str(e))

    def load_divisions(self):
        try:
            conn = get_connection()
            cur = conn.cursor()
            cur.execute(
                'SELECT "ID_divisions", "Name_of_the_department" FROM "University_division"'
            )
            for row in cur.fetchall():
                self.division_map[row[1]] = row[0]
                self.division_combo.addItem(row[1])
            cur.close()
            conn.close()
        except Exception as e:
            QMessageBox.critical(self, "Ошибка загрузки подразделений", str(e))

    def get_data(self):
        return (
            self.direction_map[self.direction_combo.currentText()],
            self.division_map[self.division_combo.currentText()],
            self.op_name.text(),
            self.impl_format.currentText(),
            int(self.hours.text()),
        )
