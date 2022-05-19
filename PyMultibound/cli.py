import argparse

'''
play <profile>
template apply <template> <char>
template create <char>
template delete <template>
create <profile name>
delete <profile name>
gui <start GUI>
'''

# See https://docs.python.org/3/library/argparse.html
main_parser = argparse.ArgumentParser(description="A profile manager for Starbound")
subparsers = main_parser.add_subparsers(
    title="subcommands",
)

parser_play = subparsers.add_parser("launch", help="Launch Starbound")
parser_play.add_argument(
    "name",
    help="The name of the profile",
    type=str
)

args = main_parser.parse_args()

