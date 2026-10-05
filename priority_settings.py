from PySide6.QtCore import Qt, Signal, QMimeData
from PySide6.QtGui import QDrag
from PySide6.QtWidgets import (
    QDialog,
    QVBoxLayout,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QListWidget,
    QListWidgetItem,
    QLineEdit,
    QMessageBox,
    QGroupBox,
    QInputDialog,
    QScrollArea,
    QWidget,
    QMenu,
    QTabWidget,
    QComboBox,
    QSpinBox,
)


# ============================================================
# KRİTERLER
# ============================================================

CRITERIA = [
    ("GEBE", "Gebe"),
    ("LOHUSA", "Lohusa"),
    ("RANDEVULU", "Randevulu"),
    ("TAHLIL", "Tahlil"),
    ("YAS_65_USTU", "65 yaş ve üzeri"),
    ("YAS_3_ALTI", "3 yaş altı"),
    ("YENIDOGAN_40_GUN", "Yenidoğan"),
    ("RANDEVUSUZ", "Randevusuz"),
    ("OZELLIKLI", "Özellikli kişi"),
]


# ============================================================
# GRUP İÇİ SIRALAMA KRİTERLERİ
# ============================================================

SORT_CRITERIA = [
    ("RANDEVULU", "Randevulu"),
    ("RANDEVU_SAATI", "Randevu saati"),
    ("GELIS_SAATI", "Geliş saati"),
    ("YAS_65_USTU", "65 yaş ve üzeri"),
    ("OZELLIKLI", "Özellikli kişi"),
    ("YAS_3_ALTI", "3 yaş altı"),
    ("YENIDOGAN_40_GUN", "Yenidoğan"),
]


# ============================================================
# YARDIMCI FONKSİYON
# ============================================================

def display_name(items, code):
    for item in items:
        if item[0] == code:
            return item[1]
    return code


# ============================================================
# KRİTER KAYNAK LİSTESİ
# ============================================================

class CriteriaSourceList(QListWidget):
    def __init__(self, parent=None):
        super().__init__(parent)

        self.setDragEnabled(True)
        self.setSelectionMode(QListWidget.SingleSelection)

        for code, name in CRITERIA:
            item = QListWidgetItem(name)
            item.setData(Qt.UserRole, code)
            self.addItem(item)

    def startDrag(self, supportedActions):
        item = self.currentItem()

        if not item:
            return

        mime = QMimeData()
        mime.setText(item.data(Qt.UserRole))

        drag = QDrag(self)
        drag.setMimeData(mime)

        drag.exec(Qt.CopyAction)


# ============================================================
# GRUP KRİTER LİSTESİ
# ============================================================

class CriteriaDropList(QListWidget):
    changed = Signal()

    def __init__(self, parent=None):
        super().__init__(parent)

        self.setAcceptDrops(True)
        self.setDragEnabled(True)
        self.setDropIndicatorShown(True)
        self.setSelectionMode(QListWidget.SingleSelection)

    def dragEnterEvent(self, event):
        if event.mimeData().hasText():
            event.acceptProposedAction()
        else:
            event.ignore()

    def dragMoveEvent(self, event):
        if event.mimeData().hasText():
            event.acceptProposedAction()
        else:
            event.ignore()

    def dropEvent(self, event):
        code = event.mimeData().text()

        if not code:
            return

        # Aynı kriter aynı grupta iki kez bulunmasın
        for i in range(self.count()):
            if self.item(i).data(Qt.UserRole) == code:
                event.ignore()
                return

        item = QListWidgetItem(
            display_name(CRITERIA, code)
        )
        item.setData(Qt.UserRole, code)

        self.addItem(item)
        self.changed.emit()

        event.acceptProposedAction()

    def contextMenuEvent(self, event):
        item = self.itemAt(event.pos())

        if not item:
            return

        menu = QMenu(self)

        remove_action = menu.addAction("Kriteri kaldır")

        action = menu.exec(event.globalPosition().toPoint())

        if action == remove_action:
            row = self.row(item)
            self.takeItem(row)
            self.changed.emit()


# ============================================================
# GRUP İÇİ SIRALAMA LİSTESİ
# ============================================================

class SortDropList(QListWidget):
    changed = Signal()

    def __init__(self, parent=None):
        super().__init__(parent)

        self.setAcceptDrops(True)
        self.setDragEnabled(True)
        self.setDropIndicatorShown(True)
        self.setSelectionMode(QListWidget.SingleSelection)

    def dragEnterEvent(self, event):
        if event.mimeData().hasText():
            event.acceptProposedAction()
        else:
            event.ignore()

    def dragMoveEvent(self, event):
        if event.mimeData().hasText():
            event.acceptProposedAction()
        else:
            event.ignore()

    def dropEvent(self, event):
        code = event.mimeData().text()

        if not code:
            return

        # Aynı sıralama kriteri iki kez eklenmesin
        for i in range(self.count()):
            if self.item(i).data(Qt.UserRole) == code:
                event.ignore()
                return

        item = QListWidgetItem(
            display_name(SORT_CRITERIA, code)
        )
        item.setData(Qt.UserRole, code)

        self.addItem(item)

        self.changed.emit()
        event.acceptProposedAction()

    def contextMenuEvent(self, event):
        item = self.itemAt(event.pos())

        if not item:
            return

        menu = QMenu(self)

        remove_action = menu.addAction(
            "Sıralama kriterini kaldır"
        )

        action = menu.exec(event.globalPosition().toPoint())

        if action == remove_action:
            row = self.row(item)
            self.takeItem(row)
            self.changed.emit()


# ============================================================
# GRUP WIDGET
# ============================================================

class GroupWidget(QGroupBox):
    changed = Signal()
    select_requested = Signal(object)

    def __init__(self, group_data, parent=None):
        super().__init__(parent)

        self.group_data = group_data

        self.setTitle(
            group_data.get("name", "Yeni Grup")
        )

        layout = QVBoxLayout(self)

        # ----------------------------------------------------
        # GRUP ADI
        # ----------------------------------------------------

        name_layout = QHBoxLayout()

        name_layout.addWidget(
            QLabel("Grup adı:")
        )

        self.name_edit = QLineEdit(
            group_data.get("name", "")
        )

        name_layout.addWidget(
            self.name_edit
        )

        layout.addLayout(name_layout)

        # ----------------------------------------------------
        # KRİTERLER
        # ----------------------------------------------------

        layout.addWidget(
            QLabel("Bu gruba dahil olan kriterler:")
        )

        self.criteria_list = CriteriaDropList()

        self.criteria_list.setMinimumHeight(90)

        for code in group_data.get("criteria", []):
            item = QListWidgetItem(
                display_name(CRITERIA, code)
            )
            item.setData(Qt.UserRole, code)
            self.criteria_list.addItem(item)

        self.criteria_list.changed.connect(
            self.emit_changed
        )

        layout.addWidget(
            self.criteria_list
        )

        # ----------------------------------------------------
        # SIRALAMA
        # ----------------------------------------------------

        layout.addWidget(
            QLabel("Grup içi sıralama:")
        )

        self.sort_list = SortDropList()

        self.sort_list.setMinimumHeight(90)

        for code in group_data.get("sort", []):
            item = QListWidgetItem(
                display_name(SORT_CRITERIA, code)
            )
            item.setData(Qt.UserRole, code)
            self.sort_list.addItem(item)

        self.sort_list.changed.connect(
            self.emit_changed
        )

        layout.addWidget(
            self.sort_list
        )

        # ----------------------------------------------------
        # GRUBU SEÇ
        # ----------------------------------------------------

        self.select_button = QPushButton(
            "Bu Grubu Seç"
        )

        self.select_button.clicked.connect(
            lambda: self.select_requested.emit(self)
        )

        layout.addWidget(
            self.select_button
        )

        self.name_edit.textChanged.connect(
            self.group_name_changed
        )

    # --------------------------------------------------------

    def group_name_changed(self, text):
        self.setTitle(text)
        self.emit_changed()

    # --------------------------------------------------------

    def emit_changed(self):
        self.changed.emit()

    # --------------------------------------------------------

    def get_data(self):
        criteria = []

        for i in range(self.criteria_list.count()):
            criteria.append(
                self.criteria_list.item(i).data(Qt.UserRole)
            )

        sort = []

        for i in range(self.sort_list.count()):
            sort.append(
                self.sort_list.item(i).data(Qt.UserRole)
            )

        return {
            "name": self.name_edit.text().strip(),
            "criteria": criteria,
            "sort": sort,
        }


# ============================================================
# ANA AYARLAR PENCERESİ
# ============================================================

class PrioritySettingsDialog(QDialog):
    def __init__(self, settings, parent=None):
        super().__init__(parent)

        self.settings = settings
        self.result_settings = settings.copy()

        self.setWindowTitle(
            "Öncelik ve Program Ayarları"
        )

        self.resize(1050, 750)

        self.groups = []

        self.build_ui()

        self.load_groups()
        self.load_special_people()
        self.load_visual_settings()
        self.load_notification_settings()

    # ========================================================
    # ANA UI
    # ========================================================

    def build_ui(self):

        main_layout = QVBoxLayout(self)

        # ----------------------------------------------------
        # SEKME ALANI
        # ----------------------------------------------------

        self.tabs = QTabWidget()

        main_layout.addWidget(
            self.tabs
        )

        # ====================================================
        # 1 - ÖNCELİK GRUPLARI
        # ====================================================

        self.groups_tab = QWidget()

        groups_layout = QVBoxLayout(
            self.groups_tab
        )

        # Grup üst butonları
        top_buttons = QHBoxLayout()

        self.add_group_button = QPushButton(
            "+ Grup ekle"
        )

        self.add_group_button.clicked.connect(
            self.add_group
        )

        top_buttons.addWidget(
            self.add_group_button
        )

        self.rename_group_button = QPushButton(
            "Grup adını değiştir"
        )

        self.rename_group_button.clicked.connect(
            self.rename_selected_group
        )

        top_buttons.addWidget(
            self.rename_group_button
        )

        self.delete_group_button = QPushButton(
            "Grup sil"
        )

        self.delete_group_button.clicked.connect(
            self.delete_selected_group
        )

        top_buttons.addWidget(
            self.delete_group_button
        )

        top_buttons.addStretch()

        groups_layout.addLayout(
            top_buttons
        )

        # Açıklama
        info = QLabel(
            "Grup sırası genel önceliği belirler. "
            "Kriterleri soldan gruplara sürükleyebilirsiniz. "
            "Grup içindeki sıralama kriterlerini de sürükleyerek değiştirebilirsiniz. "
            "Bir kriteri kaldırmak için üzerine sağ tıklayın."
        )

        info.setWordWrap(True)

        groups_layout.addWidget(
            info
        )

        # ----------------------------------------------------
        # KAYNAK + GRUPLAR
        # ----------------------------------------------------

        content_layout = QHBoxLayout()

        # Sol kriter paneli
        criteria_box = QGroupBox(
            "Kullanılabilir kriterler"
        )

        criteria_layout = QVBoxLayout(
            criteria_box
        )

        criteria_layout.addWidget(
            QLabel(
                "Kriteri gruba eklemek için sürükleyin:"
            )
        )

        self.criteria_source = CriteriaSourceList()

        criteria_layout.addWidget(
            self.criteria_source
        )

        content_layout.addWidget(
            criteria_box,
            1
        )

        # Sağ grup alanı
        scroll = QScrollArea()

        scroll.setWidgetResizable(True)

        self.groups_container = QWidget()

        self.groups_layout = QVBoxLayout(
            self.groups_container
        )

        self.groups_layout.setAlignment(
            Qt.AlignTop
        )

        scroll.setWidget(
            self.groups_container
        )

        content_layout.addWidget(
            scroll,
            3
        )

        groups_layout.addLayout(
            content_layout
        )

        self.tabs.addTab(
            self.groups_tab,
            "Öncelik Grupları"
        )

        # ====================================================
        # 2 - ÖZELLİKLİ KİŞİLER
        # ====================================================

        self.special_tab = QWidget()

        special_layout = QVBoxLayout(
            self.special_tab
        )

        special_layout.addWidget(
            QLabel(
                "Özellikli kişi olarak öncelik vermek istediğiniz "
                "kişileri buradan tanımlayabilirsiniz."
            )
        )

        special_layout.addWidget(
            QLabel(
                "Bu listedeki kişiler, grup içi sıralamada "
                "'Özellikli kişi' kriteri kullanıldığında öne alınır."
            )
        )

        # Ekleme alanı
        add_layout = QHBoxLayout()

        self.special_edit = QLineEdit()

        self.special_edit.setPlaceholderText(
            "T.C. kimlik no veya ayırt edici bilgi"
        )

        add_layout.addWidget(
            self.special_edit
        )

        self.special_add_button = QPushButton(
            "Ekle"
        )

        self.special_add_button.clicked.connect(
            self.add_special_person
        )

        add_layout.addWidget(
            self.special_add_button
        )

        special_layout.addLayout(
            add_layout
        )

        # Liste
        self.special_list = QListWidget()

        special_layout.addWidget(
            self.special_list
        )

        self.special_delete_button = QPushButton(
            "Seçili kişiyi kaldır"
        )

        self.special_delete_button.clicked.connect(
            self.delete_special_person
        )

        special_layout.addWidget(
            self.special_delete_button
        )

        self.tabs.addTab(
            self.special_tab,
            "Özellikli Kişiler"
        )

        # ====================================================
        # 3 - GÖRÜNÜM
        # ====================================================

        self.visual_tab = QWidget()

        visual_layout = QVBoxLayout(
            self.visual_tab
        )

        visual_layout.addWidget(
            QLabel("Tema:")
        )

        self.theme_combo = QComboBox()

        self.theme_combo.addItem(
            "Siyah",
            "dark"
        )

        self.theme_combo.addItem(
            "Gri",
            "gray"
        )

        self.theme_combo.addItem(
            "Beyaz",
            "light"
        )

        visual_layout.addWidget(
            self.theme_combo
        )

        visual_layout.addSpacing(15)

        visual_layout.addWidget(
            QLabel(
                "Diğer görünüm ayarlarını sonraki aşamada "
                "buraya ekleyebiliriz."
            )
        )

        visual_layout.addStretch()

        self.tabs.addTab(
            self.visual_tab,
            "Görünüm"
        )

        # ====================================================
        # 4 - BİLDİRİMLER
        # ====================================================

        self.notifications_tab = QWidget()

        notifications_layout = QVBoxLayout(
            self.notifications_tab
        )

        self.visual_notification = QPushButton(
            "Yeni hasta geldiğinde görsel uyarı"
        )

        self.visual_notification.setCheckable(
            True
        )

        notifications_layout.addWidget(
            self.visual_notification
        )

        self.sound_notification = QPushButton(
            "Yeni hasta geldiğinde sesli uyarı"
        )

        self.sound_notification.setCheckable(
            True
        )

        notifications_layout.addWidget(
            self.sound_notification
        )

        self.only_empty_notification = QPushButton(
            "Yalnızca liste boşken ilk hasta geldiğinde uyar"
        )

        self.only_empty_notification.setCheckable(
            True
        )

        notifications_layout.addWidget(
            self.only_empty_notification
        )

        notifications_layout.addStretch()

        self.tabs.addTab(
            self.notifications_tab,
            "Bildirimler"
        )

        # ====================================================
        # ALT BUTONLAR
        # ====================================================

        bottom_layout = QHBoxLayout()

        bottom_layout.addStretch()

        cancel_button = QPushButton(
            "İptal"
        )

        cancel_button.clicked.connect(
            self.reject
        )

        bottom_layout.addWidget(
            cancel_button
        )

        save_button = QPushButton(
            "Kaydet"
        )

        save_button.clicked.connect(
            self.save_all
        )

        bottom_layout.addWidget(
            save_button
        )

        main_layout.addLayout(
            bottom_layout
        )

    # ========================================================
    # GRUPLAR
    # ========================================================

    def load_groups(self):

        # Eski widgetları temizle
        for group in self.groups:
            group.deleteLater()

        self.groups.clear()

        for group_data in self.settings.get(
            "priority_groups",
            []
        ):
            self.create_group_widget(
                group_data
            )

    # --------------------------------------------------------

    def create_group_widget(self, group_data):

        widget = GroupWidget(
            group_data
        )

        widget.changed.connect(
            self.group_changed
        )

        widget.select_requested.connect(
            self.select_group
        )

        self.groups.append(
            widget
        )

        self.groups_layout.addWidget(
            widget
        )

        return widget

    # --------------------------------------------------------

    def add_group(self):

        number = len(self.groups) + 1

        group_data = {
            "name": f"Yeni Grup {number}",
            "criteria": [],
            "sort": [],
        }

        self.create_group_widget(
            group_data
        )

    # --------------------------------------------------------

    def select_group(self, group):

        for item in self.groups:
            item.setStyleSheet("")

        group.setStyleSheet(
            """
            QGroupBox {
                border: 2px solid #4a90e2;
            }
            """
        )

        self.selected_group = group

    # --------------------------------------------------------

    def rename_selected_group(self):

        if not self.groups:
            return

        group = getattr(
            self,
            "selected_group",
            self.groups[0]
        )

        current_name = group.name_edit.text()

        name, ok = QInputDialog.getText(
            self,
            "Grup adını değiştir",
            "Yeni grup adı:",
            text=current_name
        )

        if ok and name.strip():
            group.name_edit.setText(
                name.strip()
            )

    # --------------------------------------------------------

    def delete_selected_group(self):

        if not self.groups:
            return

        group = getattr(
            self,
            "selected_group",
            self.groups[-1]
        )

        answer = QMessageBox.question(
            self,
            "Grup sil",
            f"'{group.name_edit.text()}' grubu silinsin mi?",
            QMessageBox.Yes | QMessageBox.No
        )

        if answer != QMessageBox.Yes:
            return

        self.groups.remove(
            group
        )

        group.setParent(None)
        group.deleteLater()

        if self.groups:
            self.selected_group = self.groups[-1]

    # --------------------------------------------------------

    def group_changed(self):

        pass

    # ========================================================
    # ÖZELLİKLİ KİŞİLER
    # ========================================================

    def load_special_people(self):

        self.special_list.clear()

        special_people = self.settings.get(
            "special_people",
            []
        )

        for person in special_people:
            self.special_list.addItem(
                str(person)
            )

    # --------------------------------------------------------

    def add_special_person(self):

        value = self.special_edit.text().strip()

        if not value:
            return

        # Aynı kişi iki kez eklenmesin
        for i in range(
            self.special_list.count()
        ):
            if (
                self.special_list.item(i).text()
                == value
            ):
                QMessageBox.information(
                    self,
                    "Bilgi",
                    "Bu kişi zaten listede."
                )
                return

        self.special_list.addItem(
            value
        )

        self.special_edit.clear()

    # --------------------------------------------------------

    def delete_special_person(self):

        row = self.special_list.currentRow()

        if row < 0:
            return

        self.special_list.takeItem(
            row
        )

    # ========================================================
    # GÖRÜNÜM
    # ========================================================

    def load_visual_settings(self):

        visual = self.settings.get(
            "visual",
            {}
        )

        theme = visual.get(
            "theme",
            "dark"
        )

        index = self.theme_combo.findData(
            theme
        )

        if index >= 0:
            self.theme_combo.setCurrentIndex(
                index
            )

    # ========================================================
    # BİLDİRİMLER
    # ========================================================

    def load_notification_settings(self):

        notifications = self.settings.get(
            "notifications",
            {}
        )

        self.visual_notification.setChecked(
            notifications.get(
                "new_patient_visual",
                True
            )
        )

        self.sound_notification.setChecked(
            notifications.get(
                "new_patient_sound",
                True
            )
        )

        self.only_empty_notification.setChecked(
            notifications.get(
                "notify_only_when_empty",
                False
            )
        )

    # ========================================================
    # KAYDET
    # ========================================================

    def save_all(self):

        # ----------------------------------------------------
        # GRUPLAR
        # ----------------------------------------------------

        self.settings["priority_groups"] = [
            group.get_data()
            for group in self.groups
        ]

        # ----------------------------------------------------
        # ÖZELLİKLİ KİŞİLER
        # ----------------------------------------------------

        self.settings["special_people"] = [
            self.special_list.item(i).text()
            for i in range(
                self.special_list.count()
            )
        ]

        # ----------------------------------------------------
        # TEMA
        # ----------------------------------------------------

        if "visual" not in self.settings:
            self.settings["visual"] = {}

        self.settings["visual"]["theme"] = (
            self.theme_combo.currentData()
        )

        # ----------------------------------------------------
        # BİLDİRİMLER
        # ----------------------------------------------------

        if "notifications" not in self.settings:
            self.settings["notifications"] = {}

        self.settings["notifications"][
            "new_patient_visual"
        ] = self.visual_notification.isChecked()

        self.settings["notifications"][
            "new_patient_sound"
        ] = self.sound_notification.isChecked()

        self.settings["notifications"][
            "notify_only_when_empty"
        ] = self.only_empty_notification.isChecked()
        # ----------------------------------------------------
        # SONUÇ AYARLARINI MAIN.PY'YE VER
        # ----------------------------------------------------

        self.result_settings = self.settings.copy()
        # ----------------------------------------------------
        # KAPAT
        # ----------------------------------------------------

        self.accept()

