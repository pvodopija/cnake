import sys, termios


def get_input():

    str_ = ""

    while True:
        c = sys.stdin.read( 1 )     # Reads one byte at a time, similar to getchar().

        if c == ' ':
            break
        else:
            str_ += c
    
    return str_

args_ = []

for i in range( 5 ):
    args_.append( get_input() )

print( args_ )