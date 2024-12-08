import re
from collections import defaultdict


class GrammarToNFA:
    def __init__(self, grammar_type="right", regex = r"^\s*<(\w+)>\s*->\s*((?:<\w+>\s+)?\w(?:\s*\|\s*(?:<\w+>\s+)?\w)*)\s*$"):
        self.grammar_type = grammar_type
        self.rules = defaultdict(list)
        self.start_symbol = None
        self.regex = regex

    def parse_grammar(self, grammar_lines):
        for line in grammar_lines:
            match = re.match(self.regex, line.strip())
            if match:
                non_terminal = match.group(1)
                productions = match.group(2).split('|')
                for production in productions:
                    self.rules[non_terminal].append(production.strip())
                if self.start_symbol is None:
                    self.start_symbol = non_terminal

    def to_nfa(self):
        nfa = defaultdict(list)
        state_counter = 0

        def get_new_state():
            nonlocal state_counter
            state = f"q{state_counter}"
            state_counter += 1
            return state

        state_map = {}
        final_states = set()

        for non_terminal, productions in self.rules.items():
            if non_terminal not in state_map:
                state_map[non_terminal] = get_new_state()

            for production in productions:
                if self.grammar_type == "right":
                    if "<" in production:
                        terminal, next_non_terminal = production.split()
                        next_non_terminal = next_non_terminal.strip('<>')

                        if next_non_terminal not in state_map:
                            state_map[next_non_terminal] = get_new_state()

                        nfa[state_map[non_terminal]].append((terminal, state_map[next_non_terminal]))
                    else:
                        if (len(final_states) == 0):
                            state_map["F"] = get_new_state()
                            final_states.add(state_map["F"])
                        nfa[state_map[non_terminal]].append((production, state_map["F"]))
                elif self.grammar_type == "left":
                    if "<" in production:
                        next_non_terminal, terminal = production.split()
                        next_non_terminal = next_non_terminal.strip('<>')

                        if next_non_terminal not in state_map:
                            state_map[next_non_terminal] = get_new_state()

                        nfa[state_map[non_terminal]].append((terminal, state_map[next_non_terminal]))
                    else:
                        if (len(final_states) == 0):
                            state_map["F"] = get_new_state()
                            final_states.add(state_map["F"])
                        nfa[state_map[non_terminal]].append((production, state_map["F"]))

        return nfa, state_map, final_states

    def to_transition_table(self, nfa, state_map, final_states):
        states = sorted(state_map.values())
        inputs = sorted({symbol[0] for state in nfa.values() for symbol in state})
        table = defaultdict(lambda: [""] * len(states))

        for state, transitions in nfa.items():
            for symbol, next_state in transitions:
                if (next_state == 'ε'):
                    next_state = state
                table[symbol][states.index(state)] += ("," if table[symbol][states.index(state)] else "") + next_state

        final_state_indexes = {}
        for final_state in final_states:
            final_state_indexes[states.index(final_state)] = final_state
        print(final_states)
        print(final_state_indexes)
        final_string = ''
        for index in sorted(final_state_indexes):
            final_string += (';'*(index-len(final_string))+'F')
        output = [f";{final_string}", f";{';'.join(states)}"]
        for symbol in inputs:
            row = f"{symbol[0]};" + ";".join(table[symbol[0]])
            output.append(row)

        return "\n".join(output)