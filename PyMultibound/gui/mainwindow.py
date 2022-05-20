import sys

from PyQt5.QtWidgets import *

from PyMultibound.common import *
from PyMultibound.common.profiles import *
from PyMultibound.common.util import runStarbound
from PyMultibound.gui.templatewindow import CharacterTemplateMenu
from PyMultibound.gui.util import getSelectedListItem


class MainWindow(QMainWindow):

    def __init__(self, parent=None):
        logging.debug("Initializing GUI")
        super().__init__(parent)
        self.setWindowTitle('PyMultibound')

        self.profileList = QListWidget()
        self._updateProfileList()
        self.setCentralWidget(self.profileList)  # It's the only thing we need
        # no need for any container widgets

        # Use a tool bar for buttons
        tools = QToolBar()
        self.addToolBar(tools)
        tools.addAction("Run Starbound", self.attemptRunStarbound)
        tools.addAction("New Profile", self._newProfileDialog)
        tools.addAction("Delete Profile", self._deleteProfileDialog)
        tools.addAction("Character Templates", self._openTemplateMenu)

        # Status bar for current status/messages
        self.status = QStatusBar()
        self.status.showMessage(f"PyMultibound {VERSION}")
        self.setStatusBar(self.status)
        logging.debug("Initialized GUI")

    def _newProfileDialog(self):
        """
        Bring up a dialog to create a new profile
        """
        logging.debug("Creating new profile dialog")
        name, ok = QInputDialog.getText(self, "Create Profile", "Enter Profile Name:")
        if ok:
            # Import from Steam dialog
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
            logging.debug("User aborted profile creation")
            self.status.showMessage("Aborted profile creation")

        self._updateProfileList()

    def _deleteProfileDialog(self):
        """
        Bring up a confirmation window and delete the selected profile
        """
        logging.debug("Creating delete profile dialog")
        name = self._getSelectedProfile()
        if name == "":  # None selected
            self.status.showMessage("Select a profile before deleting it!")
            return

        # Confirmation message box
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
            logging.debug("User aborted profile deletion")

        self._updateProfileList()

    def attemptRunStarbound(self):
        """
        Attempt to run Starbound with the current selected profile
        """
        name = self._getSelectedProfile()
        if name == "":
            self.status.showMessage("Select a profile before starting Starbound!")
            return
        runStarbound(name)

    def _updateProfileList(self):
        """
        Update the displayed list of profiles
        """
        logging.debug("Updating profile list")
        self.profileList.clear()
        for profile in getProfiles():
            self.profileList.addItem(QListWidgetItem(profile))

    def _getSelectedProfile(self) -> str:
        """
        Get the currently selected profile
        Returns "" if no profile is selected
        """
        return getSelectedListItem(self.profileList, "profile")

    def _openTemplateMenu(self):
        """
        Open the character appearance template menu
        """
        logging.debug("Opening template menu")
        # Not a child of this; appears as its own window
        self.templateMenu = CharacterTemplateMenu()
        self.templateMenu.show()


if __name__ == '__main__':
    logging.info("Running GUI")
    app = QApplication(sys.argv)
    win = MainWindow()
    win.show()
    sys.exit(app.exec_())
