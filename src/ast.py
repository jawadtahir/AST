'''
Created on Feb 4, 2020

@author: foobar
'''
from getopt import getopt
import sys
from com.ripstech.commands.commands import CommandFactory


def print_help():
    print("python3 ast.py [-s sql file path (Default: .\operations.sql)]")


if __name__ == '__main__':
    file_name = "operations.sql"
    options, remainder = getopt(sys.argv[1:], "hs:")

    for opt, arg in options:
        if opt == "-h":
            print_help()
            sys.exit(0)
        elif opt == "-s":
            file_name = arg

    with open(file_name, "r") as fd:
        commands = fd.readlines()

    for command in commands:
        com = CommandFactory.get_command(command)
        com.print_ast()
