from PyQt5.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QPushButton,
    QTableWidget,
    QTableWidgetItem,
    QHBoxLayout,
    QMessageBox,
    QDialog,
    QFormLayout,
    QDialogButtonBox,
    QComboBox,
)
from db import get_connection
from logger import logger


class DisciplineInUPWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Таблица: Дисциплины в УП")
        self.setGeometry(100, 100, 800, 400)

        self.layout = QVBoxLayout(self)

        self.table = QTableWidget()
        self.layout.addWidget(self.table)

        btns = QHBoxLayout()
        refresh_btn = QPushButton("Обновить")
        refresh_btn.clicked.connect(self.load_data)
        btns.addWidget(refresh_btn)

        add_btn = QPushButton("Добавить")
        add_btn.clicked.connect(self.add_record)
        btns.addWidget(add_btn)

        edit_btn = QPushButton("Редактировать")
        edit_btn.clicked.connect(self.edit_record)
        btns.addWidget(edit_btn)

        delete_btn = QPushButton("Удалить")
        delete_btn.clicked.connect(self.delete_record)
        btns.addWidget(delete_btn)

        self.layout.addLayout(btns)
        self.load_data()

    def load_data(self):
        try:
            conn = get_connection()
            cur = conn.cursor()
            cur.execute(
                """
                SELECT diup."ID_disciplines_in_UP",
                       d."Discipline_name",
                       up."Year_of_admission" || ' — ' || op."OP_name" AS up_display
                FROM "Discipline_in_UP" diup
                JOIN "Discipline" d ON diup."ID_discipline" = d."ID_disciplines"
                JOIN "UP" up ON diup."ID_UP" = up."ID_UP"
                JOIN "OP" op ON up."ID_OP" = op."ID_OP"
                ORDER BY diup."ID_disciplines_in_UP"
            """
            )
            rows = cur.fetchall()
            self.table.setRowCount(len(rows))
            self.table.setColumnCount(3)
            self.table.setHorizontalHeaderLabels(["ID", "Дисциплина", "УП"])
            for i, row in enumerate(rows):
                for j, val in enumerate(row):
                    self.table.setItem(i, j, QTableWidgetItem(str(val)))
            cur.close()
            conn.close()
            logger.info("Загружены данные Discipline_in_UP")
        except Exception as e:
            logger.error(f"Ошибка загрузки Discipline_in_UP: {e}")
            QMessageBox.critical(self, "Ошибка", str(e))

    def add_record(self):
        dialog = DisciplineInUPDialog()
        if dialog.exec_() == QDialog.Accepted:
            try:
                conn = get_connection()
                cur = conn.cursor()
                cur.execute(
                    """
                    INSERT INTO "Discipline_in_UP" ("ID_discipline", "ID_UP")
                    VALUES (%s, %s)
                """,
                    dialog.get_data(),
                )
                conn.commit()
                cur.close()
                conn.close()
                self.load_data()
                logger.info("Добавлена запись в Discipline_in_UP")
            except Exception as e:
                logger.error(f"Ошибка добавления: {e}")
                QMessageBox.critical(self, "Ошибка", str(e))

    def edit_record(self):
        row = self.table.currentRow()
        if row < 0:
            QMessageBox.warning(self, "Внимание", "Выберите запись для редактирования")
            return

        record_id = self.table.item(row, 0).text()
        discipline_name = self.table.item(row, 1).text()
        up_display = self.table.item(row, 2).text()

        dialog = DisciplineInUPDialog(discipline_name, up_display)
        if dialog.exec_() == QDialog.Accepted:
            try:
                conn = get_connection()
                cur = conn.cursor()
                cur.execute(
                    """
                    UPDATE "Discipline_in_UP"
                    SET "ID_discipline" = %s, "ID_UP" = %s
                    WHERE "ID_disciplines_in_UP" = %s
                """,
                    (*dialog.get_data(), record_id),
                )
                conn.commit()
                cur.close()
                conn.close()
                self.load_data()
                logger.info(f"Обновлена запись ID={record_id}")
            except Exception as e:
                logger.error(f"Ошибка обновления: {e}")
                QMessageBox.critical(self, "Ошибка", str(e))

    def delete_record(self):
        row = self.table.currentRow()
        if row < 0:
            QMessageBox.warning(self, "Внимание", "Выберите запись для удаления")
            return

        record_id = self.table.item(row, 0).text()
        confirm = QMessageBox.question(
            self,
            "Подтверждение",
            f"Удалить запись ID {record_id}?",
            QMessageBox.Yes | QMessageBox.No,
        )
        if confirm == QMessageBox.Yes:
            try:
                conn = get_connection()
                cur = conn.cursor()
                cur.execute(
                    'DELETE FROM "Discipline_in_UP" WHERE "ID_disciplines_in_UP" = %s',
                    (record_id,),
                )
                conn.commit()
                cur.close()
                conn.close()
                self.load_data()
                logger.info(f"Удалена запись ID={record_id}")
            except Exception as e:
                logger.error(f"Ошибка удаления: {e}")
                QMessageBox.critical(self, "Ошибка", str(e))


class DisciplineInUPDialog(QDialog):
    def __init__(self, discipline_name="", up_display=""):
        super().__init__()
        self.setWindowTitle("Связь Дисциплина — УП")
        layout = QFormLayout(self)

        self.discipline_combo = QComboBox()
        self.discipline_map = {}
        self.load_disciplines()

        self.up_combo = QComboBox()
        self.up_map = {}
        self.load_ups()

        layout.addRow("Дисциплина:", self.discipline_combo)
        layout.addRow("УП:", self.up_combo)

        if discipline_name:
            self.discipline_combo.setCurrentText(discipline_name)
        if up_display:
            self.up_combo.setCurrentText(up_display)

        buttons = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        buttons.accepted.connect(self.accept)
        buttons.rejected.connect(self.reject)
        layout.addWidget(buttons)

    def load_disciplines(self):
        try:
            conn = get_connection()
            cur = conn.cursor()
            cur.execute(
                'SELECT "ID_disciplines", "Discipline_name" FROM "Discipline" ORDER BY "Discipline_name"'
            )
            for disc_id, disc_name in cur.fetchall():
                self.discipline_map[disc_name] = disc_id
                self.discipline_combo.addItem(disc_name)
            cur.close()
            conn.close()
        except Exception as e:
            QMessageBox.critical(self, "Ошибка загрузки дисциплин", str(e))

    def load_ups(self):
        try:
            conn = get_connection()
            cur = conn.cursor()
            cur.execute(
                """
                SELECT up."ID_UP", up."Year_of_admission" || ' — ' || op."OP_name"
                FROM "UP" up
                JOIN "OP" op ON up."ID_OP" = op."ID_OP"
                ORDER BY up."Year_of_admission", op."OP_name"
            """
            )
            for up_id, up_display in cur.fetchall():
                self.up_map[up_display] = up_id
                self.up_combo.addItem(up_display)
            cur.close()
            conn.close()
        except Exception as e:
            QMessageBox.critical(self, "Ошибка загрузки УП", str(e))

    def get_data(self):
        discipline_id = self.discipline_map[self.discipline_combo.currentText()]
        up_id = self.up_map[self.up_combo.currentText()]
        return discipline_id, up_id
