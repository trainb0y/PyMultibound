import logging
import shutil

from util import Fore, Style


# Credit for this class goes to https://codereview.stackexchange.com/a/206233
# Modified a little

class Menu:
    def __init__(self, title, options):
        self.title = title
        self.options = options
        logging.debug(f"Created menu \"{title}\"")

    def display(self):
        logging.debug(f"Displaying menu \"{self.title}\"")
        string = Fore.CYAN + self.title + Style.RESET_ALL + ":\n"
        for i, option in enumerate(self.options):
            string += f"-  {i + 1}) {option[0]}\n"

        # Add header and footer
        max_width = shutil.get_terminal_size()[0]
        string = f'{"-" * max_width}\n{string}\n{"-" * max_width}'

        return string

    def callback(self, i):
        if i <= len(self.options):
            logging.debug(f"Callback > {self.options[i - 1][1]}")
            return self.options[i - 1][1]
        else:
            logging.debug("Callback > False, option not found")
            return False

    def select(self):
        while True:
            print(self.display())
            try:
                option = int(input(">> "))
                result = self.callback(option)
                if result:
                    return result
                else:
                    print(f"{Fore.RED}Please enter a number corresponding to an option!")
            except ValueError:
                print(f"{Fore.RED}Please enter a number!")

            print()
