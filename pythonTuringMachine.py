#!/usr/bin/env python
# tested with python 2.7
# ben oliver (github beoliver)

import argparse
import sys
import logging
import os.path

class TuringMachine(object):

    def __init__(self):
        self.transitions = None
        self._tape = None

    def load_transitions(self, path):
        self.transitions = {}
        with open(path, 'rU') as f:
            transitions = filter(None, (line.strip() for line in f))
        assert len(transitions) > 3
        self.start  = transitions[0]
        self.accept = transitions[1]
        self.reject = transitions[2]
        assert self.accept != self.reject
        for t in transitions[3:]:
            symbs = filter(None, t.split(" "))
            assert len(symbs) == 5
            self.transitions[(symbs[0],symbs[1])] = ((symbs[2],symbs[3]),symbs[4])

    def run_tape(self, tape, verbose=False):
        logging.info("run tape")
        self.tape = list(tape) + ["_"] # add an explicit blank to the end of the tape
        tape_len = len(self.tape)
        head_index = 0
        state = self.start
        err = ((self.reject, '_'), 'L')
        while True:
            if verbose:
                tape_pre  = ' '.join(self.tape[:head_index])
                tape_at   = " [" + self.tape[head_index] + "] "
                tape_post = ' '.join(self.tape[head_index+1:])
                if head_index > 0:
                    tape_pre = " " + tape_pre
                logging.info(tape_pre + tape_at + tape_post)
            ((state, rewrite), direction) = self.transitions.get((state, self.tape[head_index]), err)
            if state in [self.accept, self.reject]:
                return state == self.accept
            if head_index == tape_len - 1:
                self.tape.append('_') # pretend the list is infinite
                tape_len += 1
            self.tape[head_index] = rewrite
            if direction == 'R':
                head_index += 1
            elif head_index > 0:
                head_index -= 1

def help_message():
    return """
    ------------------------------------
    |  A  |  B  |  O  |  U  |  T  |  ...
    ------------------------------------

    How do I get this thing running?

        Firstly you need a text file that defines the turing machine transitions.
        To create a valid input you need to know the following:

        <MOVE>   :: 'L' or 'R'
        <STATE>  :: any string containing only 'printable' characters
        <SYMBOL> :: any 'printable' character
        '_'      :: is considered the blank symbol.

    What does the input file look like?

        Three lines must appear before the transitions listing the start state,
        accept state and reject state. NOTE: accept and reject must be different
        states ('strings').

        <STATE>
        <STATE>
        <STATE>

        After this, we define the 'transition function'. It is formed by n lines
        consiting of 5 white space separated strings (remeber that <SYBBOL> must
        be a single character).

        <STATE> <SYMBOL> <STATE'> <SYMBOL'> <MOVE>
        ...
        <STATE> <SYMBOL> <STATE'> <SYMBOL'> <MOVE>

        this should be read as: (<STATE>, <SYMBOL>) -> (<STATE'>, <SYMBOL'>, <MOVE>)
        current-tm-state, current-tape-symbol -> new-tm-state new-tape-sybbol [move left or right]

    Ok. Can you show me an example?

        q1
        accept
        reject

        q1 _ accept _ R
        q1 x q1 x R
        q1 0 q2 x R
        q2 _ q4 _ L
        q2 x q2 x R
        q2 0 q3 0 R
        q3 x q3 x R
        q3 0 q2 x R
        q4 _ q1 _ R
        q4 x q4 x L
        q4 0 q4 0 L

    And running it?

        ./pythonTuringMachine.py --machine turingMachine1.tm --tape 00000000 -l
    """

# define our simple command line parser
parser = argparse.ArgumentParser(description='Run a virtual turing machine on an input string.')
# optional. we need to check for this
parser.add_argument("--machine","-m", nargs=1, metavar='M', help='a file containing start state, accept state, reject state and encoded transitions')
parser.add_argument("--tape","-t", nargs=1, metavar='T', help='an encoding of the input tape')
parser.add_argument("--log","-l", help='create a log file that documents tape traversal', action="store_true")
parser.add_argument("--about", help='how do I run this thing?', action="store_true")

if __name__ == '__main__':
    args = parser.parse_args()
    # print args.accumulate(args.integers)
    if args.about:
        print (help_message())
        sys.exit()

    tm = TuringMachine()

    try:
        assert os.path.exists(os.path.abspath(args.machine[0]))
        filename = os.path.splitext(args.machine[0])[0]
        directory = os.path.dirname(os.path.abspath(args.machine[0]))
    except Exception as e:
        print ("error opening file containing encoded transitions")
        sys.exit()

    if args.log:
        logfile  = os.path.join(directory, filename + ".log")
        logging.basicConfig(filename=logfile,level=logging.INFO)

    tm.load_transitions(os.path.abspath(args.machine[0]))
    result = tm.run_tape(args.tape[0], args.log)
    print ("ACCEPT" if result else "REJECT")
