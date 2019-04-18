import sys
import dmrg, measall

if __name__ == '__main__':
    fname = sys.argv[1]

    commands = []
    commands += dmrg.full_commands (fname)
    commands += measall.full_commands (fname, sys.argv)

    for command in commands:
        print command
