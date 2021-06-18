# Credit for this class goes to https://codereview.stackexchange.com/a/206233
# Modified and simplified a little

class Menu():
    def __init__(self, title, options):
        self.title = title
        self.options = options

    def display(self):
        string = self.title + '\n'
        for i, option in enumerate(self.options):
            string += f"{i + 1}) {option[0]}\n"

        return string

    def callback(self, i):
        if i <= len(self.options):
            return self.options[i - 1][1]
        else: return False
