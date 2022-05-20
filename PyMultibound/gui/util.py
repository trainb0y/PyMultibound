import logging

from PyQt5.QtWidgets import QListWidget, QMessageBox


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
