import sys
from PyQt5.QtWidgets import *
from PyMultibound.common import *


class MainWindow(QMainWindow):
    """Main Window."""

    def __init__(self, parent=None):
        """Initializer."""
        super().__init__(parent)
        self.setWindowTitle('PyMultibound')

        self.profileList = QListWidget()
        self._updateProfileList()
        self.setCentralWidget(self.profileList)

        tools = QToolBar()
        self.addToolBar(tools)
        tools.addAction("Run Starbound", self.attemptRunStarbound)
        tools.addAction("New Profile", self._newProfileDialog)
        tools.addAction("Delete Profile", self._deleteProfileDialog)

        self.status = QStatusBar()
        self.status.showMessage(f"PyMultibound {VERSION}")
        self.setStatusBar(self.status)

    def _newProfileDialog(self):
        name, ok = QInputDialog.getText(self, "Create Profile", "Enter Profile Name:")
        if ok:
            q = QMessageBox()
            q.setWindowTitle("Create Profile")
            q.setText("Import mods from Steam workshop?")
            q.setIcon(QMessageBox.Question)
            q.setStandardButtons(QMessageBox.Yes | QMessageBox.No)

            workshop = q.exec_() == QMessageBox.Yes
            if createProfile(name, workshop):
                self.status.showMessage(f"Created profile {name}!")
            else:
                self.status.showMessage("Failed to create profile. Check the log for details.")
        else:
            self.status.showMessage("Aborted profile creation")

        self._updateProfileList()

    def _deleteProfileDialog(self):
        name = self.getSelectedProfile()
        if name == "":
            self.status.showMessage("Select a profile before deleting it!")
            return

        confirm = QMessageBox()
        confirm.setText(f"Are you sure you want to delete profile {name}?")
        confirm.setInformativeText("This cannot be undone!")
        confirm.setWindowTitle("Delete Profile")
        confirm.setIcon(QMessageBox.Warning)
        confirm.setStandardButtons(QMessageBox.Cancel | QMessageBox.Yes)
        if confirm.exec_() == QMessageBox.Yes:
            if deleteProfile(name):
                self.status.showMessage(f"Deleted profile {name}")
            else:
                self.status.showMessage(f"Failed to delete {name}, check the log for details")
        else:
            self.status.showMessage(f"Aborted deletion of {name}")

        self._updateProfileList()

    def attemptRunStarbound(self):
        name = self.getSelectedProfile()
        if name == "":
            self.status.showMessage("Select a profile before starting Starbound!")
            return
        runStarbound(name)

    def _updateProfileList(self):
        self.profileList.clear()
        for profile in getProfiles():
            self.profileList.addItem(QListWidgetItem(profile))

    def getSelectedProfile(self) -> str:
        try:
            return self.profileList.selectedItems()[0].text()
        except:
            info = QMessageBox()
            info.setWindowTitle("Cannot Complete Operation")
            info.setText("Select a profile first!")
            info.setIcon(QMessageBox.Information)
            info.setStandardButtons(QMessageBox.Ok)
            info.exec_()
            return ""


if __name__ == '__main__':
    app = QApplication(sys.argv)
    win = MainWindow()
    win.show()
    sys.exit(app.exec_())
