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
    QComboBox,
)
from db import get_connection
from logger import logger


class UPWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Таблица: Учебные планы (УП)")
        self.setGeometry(100, 100, 700, 400)

        self.layout = QVBoxLayout()
        self.setLayout(self.layout)

        self.table = QTableWidget()
        self.layout.addWidget(self.table)

        btns = QHBoxLayout()

        refresh_btn = QPushButton("Обновить")
        refresh_btn.clicked.connect(self.load_data)
        btns.addWidget(refresh_btn)

        add_btn = QPushButton("Добавить")
        add_btn.clicked.connect(self.add_up)
        btns.addWidget(add_btn)

        edit_btn = QPushButton("Редактировать")
        edit_btn.clicked.connect(self.edit_up)
        btns.addWidget(edit_btn)

        delete_btn = QPushButton("Удалить")
        delete_btn.clicked.connect(self.delete_up)
        btns.addWidget(delete_btn)

        self.layout.addLayout(btns)
        self.load_data()

    def load_data(self):
        try:
            conn = get_connection()
            cur = conn.cursor()
            cur.execute(
                """
                SELECT up."ID_UP", up."Year_of_admission", op."OP_name"
                FROM "UP" up
                JOIN "OP" op ON up."ID_OP" = op."ID_OP"
                ORDER BY up."ID_UP"
            """
            )
            rows = cur.fetchall()
            self.table.setRowCount(len(rows))
            self.table.setColumnCount(3)
            self.table.setHorizontalHeaderLabels(["ID", "Год поступления", "ОП"])
            for i, row in enumerate(rows):
                for j, val in enumerate(row):
                    self.table.setItem(i, j, QTableWidgetItem(str(val)))
            cur.close()
            conn.close()
            logger.info("Загружены данные УП")
        except Exception as e:
            logger.error(f"Ошибка загрузки УП: {e}")
            QMessageBox.critical(self, "Ошибка", str(e))

    def add_up(self):
        dialog = UPDialog()
        if dialog.exec_() == QDialog.Accepted:
            try:
                conn = get_connection()
                cur = conn.cursor()
                cur.execute(
                    """
                    INSERT INTO "UP" ("Year_of_admission", "ID_OP")
                    VALUES (%s, %s)
                """,
                    dialog.get_data(),
                )
                conn.commit()
                cur.close()
                conn.close()
                self.load_data()
                logger.info("Добавлен новый УП")
            except Exception as e:
                logger.error(f"Ошибка добавления УП: {e}")
                QMessageBox.critical(self, "Ошибка", str(e))

    def edit_up(self):
        selected = self.table.currentRow()
        if selected < 0:
            QMessageBox.warning(self, "Внимание", "Выберите запись для редактирования")
            return

        up_id = self.table.item(selected, 0).text()
        year = self.table.item(selected, 1).text()
        op_name = self.table.item(selected, 2).text()

        dialog = UPDialog(year, op_name)
        if dialog.exec_() == QDialog.Accepted:
            try:
                conn = get_connection()
                cur = conn.cursor()
                cur.execute(
                    """
                    UPDATE "UP"
                    SET "Year_of_admission" = %s, "ID_OP" = %s
                    WHERE "ID_UP" = %s
                """,
                    (*dialog.get_data(), up_id),
                )
                conn.commit()
                cur.close()
                conn.close()
                self.load_data()
                logger.info(f"Обновлён УП ID={up_id}")
            except Exception as e:
                logger.error(f"Ошибка редактирования УП: {e}")
                QMessageBox.critical(self, "Ошибка", str(e))

    def delete_up(self):
        selected = self.table.currentRow()
        if selected < 0:
            QMessageBox.warning(self, "Внимание", "Выберите запись для удаления")
            return

        up_id = self.table.item(selected, 0).text()
        confirm = QMessageBox.question(
            self,
            "Подтверждение",
            f"Удалить УП ID {up_id}?",
            QMessageBox.Yes | QMessageBox.No,
        )
        if confirm == QMessageBox.Yes:
            try:
                conn = get_connection()
                cur = conn.cursor()
                cur.execute('DELETE FROM "UP" WHERE "ID_UP" = %s', (up_id,))
                conn.commit()
                cur.close()
                conn.close()
                self.load_data()
                logger.info(f"Удалён УП ID={up_id}")
            except Exception as e:
                logger.error(f"Ошибка удаления УП: {e}")
                QMessageBox.critical(self, "Ошибка", str(e))


class UPDialog(QDialog):
    def __init__(self, year="", op_name=""):
        super().__init__()
        self.setWindowTitle("Данные УП")
        layout = QFormLayout(self)

        self.year_edit = QLineEdit(str(year))
        self.op_combo = QComboBox()
        self.op_map = {}

        self.load_op_choices()

        layout.addRow("Год поступления:", self.year_edit)
        layout.addRow("ОП:", self.op_combo)

        if op_name:
            self.op_combo.setCurrentText(op_name)

        buttons = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        buttons.accepted.connect(self.accept)
        buttons.rejected.connect(self.reject)
        layout.addWidget(buttons)

    def load_op_choices(self):
        try:
            conn = get_connection()
            cur = conn.cursor()
            cur.execute('SELECT "ID_OP", "OP_name" FROM "OP" ORDER BY "OP_name"')
            for row in cur.fetchall():
                op_id, op_name = row
                self.op_map[op_name] = op_id
                self.op_combo.addItem(op_name)
            cur.close()
            conn.close()
        except Exception as e:
            QMessageBox.critical(self, "Ошибка загрузки ОП", str(e))

    def get_data(self):
        return (int(self.year_edit.text()), self.op_map[self.op_combo.currentText()])
