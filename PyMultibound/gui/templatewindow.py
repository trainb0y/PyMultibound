from PyQt5.QtWidgets import *

from PyMultibound.common.templates import *
from PyMultibound.gui.util import getSelectedListItem


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
        help = QMessageBox()
        help.setWindowTitle("PyMultibound Template Help")
        help.setText("""
You can create a character appearance template by selecting a character and pressing "Create Template"
Select a character and a template to Apply the template.
This will change the character's Race, Gender, Appearance, and optionally Name to that of the template.

Note that this feature is experimental, and may have unforseen consequences on your player.
Be sure to save a backup before use!
        """)
        help.setStandardButtons(QMessageBox.Ok)
        help.exec_()

    def _createTemplate(self):
        """
        Attempt to create a template based on the selected character
        """
        logging.debug("Attempting to create template")
        character = self._getSelectedCharacter()
        if character == "": return  # No character
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
        if template == "": return  # no selected template

        # Confirmation message box
        confirm = QMessageBox()
        confirm.setText(f"Are you sure you want to delete template {template}?")
        confirm.setInformativeText("This cannot be undone!")
        confirm.setWindowTitle("Delete Template")
        confirm.setIcon(QMessageBox.Warning)
        confirm.setStandardButtons(QMessageBox.Cancel | QMessageBox.Yes)

        if confirm.exec_() == QMessageBox.Yes:
            logging.info(f"Deleting template {template}")
            os.remove(join(paths["templates"], template + ".template"))
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
            applyTemplate(join(paths["templates"], template + ".template"), character[0], preserveName)
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
        self.characters = []  # to store UUID and Path, because we need more than just the name
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
