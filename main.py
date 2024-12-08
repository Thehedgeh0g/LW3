import subprocess
import sys
import argparse
import re

from numpy.f2py.auxfuncs import throw_error

from GrammarParser import GrammarToNFA

RIGHT_GRAMMAR_PATTERN = r'^\s*<(\w+)>\s*->\s*(\w(?:\s+<\w+>)?(?:\s*\|\s*\w(?:\s+<\w+>)?)*)\s*$'
LEFT_GRAMMAR_PATTERN = r'^\s*<(\w+)>\s*->\s*((?:<\w+>\s+)?\w(?:\s*\|\s*(?:<\w+>\s+)?\w)*)\s*$'
GRAMMAR_TYPE_LEFT = 'left'
GRAMMAR_TYPE_RIGHT = 'right'


def createParser ():
    parser = argparse.ArgumentParser()
    parser.add_argument ('inPath', nargs='?', default='in.csv')
    parser.add_argument ('outPath', nargs='?', default='out.csv')

    return parser

def save_to_file(data, filename):
    with open(filename, "w") as file:
        file.write(data)

def generate_input_for_mealy(nfa):
    states = sorted(nfa.keys())
    inputs = {symbol for state in nfa.values() for symbol in state}
    rows = []

    for inp in sorted(inputs):
        row = [inp]
        for state in states:
            if inp in nfa[state]:
                next_state = nfa[state][inp]
                row.append(f"{next_state}/{inp}")
            else:
                row.append("-/-")
        rows.append(";".join(row))
    return f";{';'.join(states)}\n" + "\n".join(rows)

def process_with_mealy_minimizer(data, output_file="mealy_output.csv"):
    save_to_file(data, "input_mealy.csv")
    subprocess.run(["python", "moore_minimizer.py"], check=True)
    #os.rename("out1.csv", output_file)

def read_grammar(file_path):
    with open(file_path, "r") as file:
        input_data = re.sub(r"\n\s+\|", " |", file.read().strip()).split('\n')
    return input_data

def determine_grammar_type(grammar_rules):
    for rule in grammar_rules:
        if re.match(RIGHT_GRAMMAR_PATTERN, rule):
            if re.match(LEFT_GRAMMAR_PATTERN, rule):
                throw_error('invalid grammar')
            return GRAMMAR_TYPE_RIGHT
        elif re.match(LEFT_GRAMMAR_PATTERN, rule):
            return GRAMMAR_TYPE_LEFT
    throw_error('invalid grammar')

if __name__ == "__main__":
    parser = createParser()
    namespace = parser.parse_args (sys.argv[1:])
    grammar = read_grammar(namespace.inPath)
    converter = GrammarToNFA(grammar_type=determine_grammar_type(grammar))
    converter.parse_grammar(grammar)
    nfa, state_map, final_states = converter.to_nfa()
    table = converter.to_transition_table(nfa, state_map, final_states)
    print(table)
