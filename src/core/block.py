from .rule import Rule
from .line import Line
from .sieve import Sieve
from .constants import SHOW, HIDE, CLASS

class Block:
    """A block is a collection of lines (strings) in a filter, which may include rules in them."""

    def __init__(self, line_number: int):
        self.line_number: int = line_number
        self.lines: list[Line] = []

    @classmethod
    def extract(cls, raw_lines: list[str], line_number: int = 1):
        """Returns all blocks in a from a list of textual lines."""
        if len(raw_lines) == 0:
            return []
        blocks: list[Block] = [ Block(line_number) ]
        for raw_line in raw_lines:
            line = Line(raw_line, line_number)
            if line.is_block_starter() and not len(blocks[-1].lines) == 0:
                blocks.append(Block(line_number))
            blocks[-1].lines.append(line)
            line_number +=1
        
        return blocks

    def comment_out(self):
        """Comments out every line in the block."""
        for line in self.lines:
            line.comment_out()
    
    def find(self, operand: str = None, operator: str = None) -> list[Line]:
        """Finds all the lines that contain the queried criteria."""
        return [ line
            for line in self.lines
            if operand == None or line.operand == operand
            if operator == None or line.operator == operator ]

    def hide(self):
        """Attempts to hide a block by setting every 'Show' operand in it to 'Hide'."""
        for line in self.find(operand=SHOW):
            line.operand = HIDE

    def show(self):
        """Attempts to hide a block by setting every 'Hide' operand in it to 'Show'.
        This is the reverse function to hide."""
        for line in self.find(operand=HIDE):
            line.operand = SHOW
    
    def upsert(self, operand: str, values: list[str], operator: str = "=="):
        """Updates every line that contains the `operand` with the `values` listed.
        If a line with the `operand` was not found, then a new line with the
        `operand`, `operator` and `values`is appended to the block."""
        lines = self.find(operand)
        if len(lines) == 0:
            new_line = Line(f'{self.lines[-1].indentation}{operand} {operator}', self.lines[-1].number + 1)
            self.lines.append(new_line)
            lines = [ new_line ]

        for line in lines:
            line.values = values    

    def get_rules(self, name_or_names: str | list[str]):
        """Gets all the rules in the block with name equals to rule_name."""
        return [ rule for line in self.lines for rule in line.get_rules(name_or_names) ]
    
    def get_classes(self):
        """Returns all values included in lines which have the `Class` operand."""
        lines = self.find(operand=CLASS)
        return [ value.replace('"', "") for line in lines for value in line.values ]
    
    def get_raw_lines(self):
        """Gets all lines listed within this block as raw strings."""
        return [ str(line) for line in self.lines ]
    
    def get_sieve(self):
        """Creates a `Sieve` from the lines within the block.
        Lines without operands are excluded from the it."""
        sieveable_lines = [ line for line in self.lines if line.operand != "" ]
        return Sieve(sieveable_lines)
                    
    def __str__(self):
        return '\n'.join(self.get_raw_lines())