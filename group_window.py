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
    QDateEdit,
    QComboBox,
)
from PyQt5.QtCore import QDate
from db import get_connection
from logger import logger


class GroupWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Таблица: Группы")
        self.setGeometry(100, 100, 700, 400)

        self.layout = QVBoxLayout()
        self.setLayout(self.layout)

        self.search_box = QLineEdit()
        self.search_box.setPlaceholderText("Поиск по номеру группы...")
        self.search_box.textChanged.connect(self.search_groups)
        self.layout.addWidget(self.search_box)

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
                SELECT g."ID_group", g."Group_numbers", g."from", g."by",
                       up."ID_UP", op."OP_name"
                FROM public."Group" g
                JOIN public."UP" up ON g."ID_UP" = up."ID_UP"
                JOIN public."OP" op ON up."ID_OP" = op."ID_OP"
                ORDER BY g."ID_group"
            """
            )
            rows = cur.fetchall()
            self.table.setRowCount(len(rows))
            self.table.setColumnCount(5)
            self.table.setHorizontalHeaderLabels(
                ["ID группы", "Номер группы", "С", "По", "ID_UP - Учебный план"]
            )
            for i, row in enumerate(rows):
                id_group, group_numbers, from_date, by_date, id_up, op_name = row
                self.table.setItem(i, 0, QTableWidgetItem(str(id_group)))
                self.table.setItem(i, 1, QTableWidgetItem(group_numbers))
                self.table.setItem(i, 2, QTableWidgetItem(str(from_date)))
                self.table.setItem(i, 3, QTableWidgetItem(str(by_date)))
                self.table.setItem(i, 4, QTableWidgetItem(f"{id_up} - {op_name}"))
            cur.close()
            conn.close()
            logger.info("Загружены данные групп")
        except Exception as e:
            logger.error(f"Ошибка загрузки данных групп: {e}")
            QMessageBox.critical(self, "Ошибка", str(e))

    def search_groups(self):
        keyword = self.search_box.text().strip()
        try:
            conn = get_connection()
            cur = conn.cursor()
            cur.execute(
                """
                SELECT g."ID_group", g."Group_numbers", g."from", g."by",
                       up."ID_UP", op."OP_name"
                FROM public."Group" g
                JOIN public."UP" up ON g."ID_UP" = up."ID_UP"
                JOIN public."OP" op ON up."ID_OP" = op."ID_OP"
                WHERE g."Group_numbers" ILIKE %s
                ORDER BY g."ID_group"
            """,
                (f"%{keyword}%",),
            )
            rows = cur.fetchall()
            self.table.setRowCount(len(rows))
            for i, row in enumerate(rows):
                id_group, group_numbers, from_date, by_date, id_up, op_name = row
                self.table.setItem(i, 0, QTableWidgetItem(str(id_group)))
                self.table.setItem(i, 1, QTableWidgetItem(group_numbers))
                self.table.setItem(i, 2, QTableWidgetItem(str(from_date)))
                self.table.setItem(i, 3, QTableWidgetItem(str(by_date)))
                self.table.setItem(i, 4, QTableWidgetItem(f"{id_up} - {op_name}"))
            cur.close()
            conn.close()
            logger.info(f"Поиск групп по номеру: {keyword}")
        except Exception as e:
            logger.error(f"Ошибка поиска групп: {e}")
            QMessageBox.critical(self, "Ошибка", str(e))

    def add_record(self):
        dialog = GroupDialog()
        if dialog.exec_() == QDialog.Accepted:
            try:
                data = dialog.get_data()
                conn = get_connection()
                cur = conn.cursor()
                cur.execute(
                    """
                    INSERT INTO public."Group" ("ID_UP", "Group_numbers", "from", "by")
                    VALUES (%s, %s, %s, %s)
                """,
                    data,
                )
                conn.commit()
                cur.close()
                conn.close()
                self.load_data()
                logger.info("Добавлена запись в таблицу групп")
            except Exception as e:
                logger.error(f"Ошибка добавления группы: {e}")
                QMessageBox.critical(self, "Ошибка", str(e))

    def edit_record(self):
        selected = self.table.currentRow()
        if selected < 0:
            QMessageBox.warning(self, "Внимание", "Выберите запись для редактирования")
            return

        id_group = self.table.item(selected, 0).text()

        try:
            conn = get_connection()
            cur = conn.cursor()
            cur.execute(
                """
                SELECT "ID_UP", "Group_numbers", "from", "by"
                FROM public."Group"
                WHERE "ID_group" = %s
            """,
                (id_group,),
            )
            row = cur.fetchone()
            if not row:
                QMessageBox.warning(self, "Внимание", "Запись не найдена")
                return
            id_up, group_numbers, from_date, by_date = row
            cur.close()
            conn.close()
        except Exception as e:
            logger.error(f"Ошибка получения данных для редактирования группы: {e}")
            QMessageBox.critical(self, "Ошибка", str(e))
            return

        dialog = GroupDialog(id_up, group_numbers, from_date, by_date, editing=True)
        if dialog.exec_() == QDialog.Accepted:
            try:
                data = dialog.get_data()
                conn = get_connection()
                cur = conn.cursor()
                cur.execute(
                    """
                    UPDATE public."Group"
                    SET "ID_UP" = %s, "Group_numbers" = %s, "from" = %s, "by" = %s
                    WHERE "ID_group" = %s
                """,
                    (*data, id_group),
                )
                conn.commit()
                cur.close()
                conn.close()
                self.load_data()
                logger.info(f"Отредактирована запись группы ID={id_group}")
            except Exception as e:
                logger.error(f"Ошибка редактирования группы: {e}")
                QMessageBox.critical(self, "Ошибка", str(e))

    def delete_record(self):
        selected = self.table.currentRow()
        if selected < 0:
            QMessageBox.warning(self, "Внимание", "Выберите запись для удаления")
            return

        id_group = self.table.item(selected, 0).text()
        confirm = QMessageBox.question(
            self,
            "Подтверждение",
            f"Удалить группу с ID {id_group}?",
            QMessageBox.Yes | QMessageBox.No,
        )
        if confirm == QMessageBox.Yes:
            try:
                conn = get_connection()
                cur = conn.cursor()
                cur.execute(
                    'DELETE FROM public."Group" WHERE "ID_group" = %s', (id_group,)
                )
                conn.commit()
                cur.close()
                conn.close()
                self.load_data()
                logger.info(f"Удалена запись группы ID={id_group}")
            except Exception as e:
                logger.error(f"Ошибка удаления группы: {e}")
                QMessageBox.critical(self, "Ошибка", str(e))


class GroupDialog(QDialog):
    def __init__(
        self,
        id_up=None,
        group_numbers=None,
        from_date=None,
        by_date=None,
        editing=False,
    ):
        super().__init__()
        self.setWindowTitle("Группа")
        layout = QFormLayout(self)

        self.id_up_box = QComboBox()
        self.load_id_ups(id_up)

        self.group_numbers_edit = QLineEdit()
        if group_numbers:
            self.group_numbers_edit.setText(group_numbers)

        self.from_date_edit = QDateEdit()
        self.from_date_edit.setCalendarPopup(True)
        if from_date:
            self.from_date_edit.setDate(QDate.fromString(str(from_date), "yyyy-MM-dd"))
        else:
            self.from_date_edit.setDate(QDate.currentDate())

        self.by_date_edit = QDateEdit()
        self.by_date_edit.setCalendarPopup(True)
        if by_date:
            self.by_date_edit.setDate(QDate.fromString(str(by_date), "yyyy-MM-dd"))
        else:
            self.by_date_edit.setDate(QDate.currentDate())

        layout.addRow("Учебный план (ID_UP):", self.id_up_box)
        layout.addRow("Номер группы:", self.group_numbers_edit)
        layout.addRow("Дата начала:", self.from_date_edit)
        layout.addRow("Дата окончания:", self.by_date_edit)

        buttons = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        buttons.accepted.connect(self.accept)
        buttons.rejected.connect(self.reject)
        layout.addWidget(buttons)

    def load_id_ups(self, selected_id=None):
        conn = get_connection()
        cur = conn.cursor()
        cur.execute(
            """
            SELECT up."ID_UP", op."OP_name"
            FROM public."UP" up
            JOIN public."OP" op ON up."ID_OP" = op."ID_OP"
            ORDER BY up."ID_UP"
        """
        )
        rows = cur.fetchall()
        for id_up, op_name in rows:
            display_text = f"{id_up} - {op_name}"
            self.id_up_box.addItem(display_text, id_up)
            if selected_id and id_up == selected_id:
                self.id_up_box.setCurrentIndex(self.id_up_box.count() - 1)
        cur.close()
        conn.close()

    def get_data(self):
        return (
            self.id_up_box.currentData(),
            self.group_numbers_edit.text().strip(),
            self.from_date_edit.date().toString("yyyy-MM-dd"),
            self.by_date_edit.date().toString("yyyy-MM-dd"),
        )
