from PyQt5.QtWidgets import *

from common import *


class MainWindow(QMainWindow):

    def __init__(self, parent=None):
        logging.debug("Initializing GUI")
        super().__init__(parent)
        self.setWindowTitle('PyMultibound')

        self.profileList = QListWidget()
        self._updateProfileList()
        self.setCentralWidget(self.profileList) # It's the only thing we need
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
        if name == "": # None selected
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


class CharacterTemplateMenu(QMainWindow):
    """
    The menu in which the user can create,
    delete, or apply character appearance templates.
    """
    def __init__(self):
        """
        Window setup and initialization tasks
        """
        logging.debug("Initializing character template menu")
        super().__init__()
        self.setWindowTitle("PyMultibound Character Templates")

        self.grid = QGridLayout()
        # Container so we can use a layout, as you can't
        # put a layout directly in a QMainWindow
        container = QWidget()
        container.setLayout(self.grid)
        self.setCentralWidget(container)

        # The only widgets in the layout are the labels and lists,
        # the buttons are part of the toolbar.

        characterLabel = QLabel(self)
        characterLabel.setText("Characters")
        self.grid.addWidget(characterLabel)

        self.characterList = QListWidget(self)
        self.grid.addWidget(self.characterList)

        # Maybe we can condense it so this isn't repeated twice?
        templateLabel = QLabel(self)
        templateLabel.setText("Templates")
        self.grid.addWidget(templateLabel)

        self.templateList = QListWidget(self)
        self.grid.addWidget(self.templateList)

        self._updateLists()

        # Use toolbar for buttons
        tools = QToolBar()
        self.addToolBar(tools)
        tools.addAction("Create Template", self._createTemplate)
        tools.addAction("Apply Template", self._applyTemplate)
        tools.addAction("Delete Template", self._deleteTemplate)
        tools.addAction("Help", self._openHelp)

        logging.debug("Initialized template menu")

    def _openHelp(self):
        """
        Open a help/explanation dialog
        """

    def _createTemplate(self):
        """
        Attempt to create a template based on the selected character
        """
        logging.debug("Attempting to create template")
        character = self._getSelectedCharacter()
        if character == "": return # No character
        for template in getTemplates():
            # The character name cannot be the name of an existing template
            # There is probably a better way to handle this,
            # but this will work for now
            if template[0] == character[2]:
                logging.warning("Attempted to create a template, but another template with the same name exists!")
                logging.warning("Alerting user...")
                alert = QMessageBox()
                alert.setText(f"A template with name {character[2]} already exists!")
                alert.setStandardButtons(QMessageBox.Ok)
                alert.exec_()
                logging.info("Aborted template creation")
                return
        if createTemplate(character[0]):
            logging.info("Created template successfully")
        else:
            # Could do a popup dialog here, for clarity
            logging.warning("Something went wrong creating the template!")
        self._updateLists()

    def _deleteTemplate(self):
        """
        Open a confirmation dialog and delete the selected template
        """
        logging.debug("Creating template delete dialog")
        template = self._getSelectedTemplate()
        if template == "": return # no selected template

        # Confirmation message box
        confirm = QMessageBox()
        confirm.setText(f"Are you sure you want to delete template {template}?")
        confirm.setInformativeText("This cannot be undone!")
        confirm.setWindowTitle("Delete Template")
        confirm.setIcon(QMessageBox.Warning)
        confirm.setStandardButtons(QMessageBox.Cancel | QMessageBox.Yes)

        if confirm.exec_() == QMessageBox.Yes:
            logging.info(f"Deleting template {template}")
            os.remove(join(templatesDir, template+".template"))
            self._updateLists()

    def _applyTemplate(self):
        """
        Attempt to apply the selected template to the selected character
        """
        # Confirm we have the necessary selections
        logging.debug("Confirming character and template are selected")
        character = self._getSelectedCharacter()
        if character == "": return
        template = self._getSelectedTemplate()
        if template == "": return
        logging.debug("Character and template selected")
        logging.debug("Creating apply template dialog")

        # Name preservation dialog
        q = QMessageBox()
        q.setWindowTitle("Apply Template")
        q.setText("Preserve character name?")
        q.setIcon(QMessageBox.Question)
        q.setStandardButtons(QMessageBox.Yes | QMessageBox.No)
        preserveName = q.exec_() == QMessageBox.Yes
        logging.debug(f"Preserve character name {preserveName}")

        # Action confirmation dialog
        logging.debug("Creating confirmation dialog")
        confirm = QMessageBox()
        confirm.setText(f"Are you sure you want to apply template {template} to {character[2]}?")
        confirm.setInformativeText("This cannot be undone!")
        confirm.setWindowTitle("Apply Template")
        confirm.setIcon(QMessageBox.Warning)
        confirm.setStandardButtons(QMessageBox.Cancel | QMessageBox.Yes)

        if confirm.exec_() == QMessageBox.Yes:
            logging.info(f"Applying template {template} to {character}")
            applyTemplate(join(templatesDir, template + ".template"), character[0], preserveName)
            self._updateLists()
        logging.info("Aborted template application")

    def _updateLists(self):
        """
        Update the character and template lists
        """
        logging.debug("Updating template/character lists")
        self.templateList.clear()
        for template in getTemplates():
            self.templateList.addItem(QListWidgetItem(template[0]))

        self.characterList.clear()
        self.characters = [] # to store UUID and Path, because we need more than just the name
        for character in getCharacters():
            self.characterList.addItem(QListWidgetItem(f"{character[2]} - {character[1]}"))
            self.characters.append(character)

    def _getSelectedTemplate(self) -> str:
        """
        Get the currently selected template.
        Returns "" if nothing is selected
        """
        return getSelectedListItem(self.templateList, "template")

    def _getSelectedCharacter(self) -> (str, str, str) or str:
        """
        Get the selected character.
        Returns (path, uuid, name) of the character
        or "" if none is selected.
        """
        compound = getSelectedListItem(self.characterList, "character")
        name, uuid = compound.split(" - ")
        for character in self.characters:
            if character[1] == uuid: return character
        logging.error("No character found matching the UUID! This is a bug!")
        return ""


def getSelectedListItem(l: QListWidget, name: str) -> str:
    """
    Get the currently selected item of the list
    If none is selected a dialog will open, prompting the user
    to f"Select a {name} first!"

    Returns the selected list item text value, or "" if
    nothing is selected
    """
    logging.debug(f"Attempting to get selected item from {l} (name: {name})")
    try:
        return l.selectedItems()[0].text()
    except:
        logging.debug("Nothing selected in list")
        info = QMessageBox()
        info.setWindowTitle("Cannot Complete Operation")
        info.setText(f"Select a {name} first!")
        info.setIcon(QMessageBox.Information)
        info.setStandardButtons(QMessageBox.Ok)
        info.exec_()
        return ""


if __name__ == '__main__':
    logging.info("Running GUI")
    app = QApplication(sys.argv)
    win = MainWindow()
    win.show()
    sys.exit(app.exec_())
