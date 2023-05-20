from .rule import Rule
from .line import Line

_HIDE = "Hide"
_SHOW = "Show"
_CLASS = "Class"

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
    
    def hide(self):
        """Attempts to hide a block by setting every 'Show' operand in it to 'Hide'."""
        for line in self.find(operand=_SHOW):
            line.operand = _HIDE

    def show(self):
        """Attempts to hide a block by setting every 'Hide' operand in it to 'Show'.
        This is the reverse function to hide."""
        for line in self.find(operand=_HIDE):
            line.operand = _SHOW

    def find(self, operand: str = None, operator: str = None) -> list[Line]:
        """Finds all the lines that contain the queried criteria."""
        lines = self.lines
        if operand != None:
            lines = [ line for line in lines if line.operand == operand ]
        if operator != None:
            lines = [ line for line in lines if line.operator == operator ]
        return lines

    def get_rules(self, name_or_names: str | list[str]) -> list[Rule]:
        """Gets all the rules in the block with name equals to rule_name."""
        return [ rule for line in self.lines for rule in line.get_rules(name_or_names) ]
    
    def get_classes(self):
        """Returns all values included in lines which have the `Class` operand."""
        lines = self.find(operand=_CLASS)
        return [ value.replace('"', "") for line in lines for value in line.values ]
    
    def get_raw_lines(self):
        return [ str(line) for line in self.lines ]
                    
    def __str__(self):
        return '\n'.join(self.get_raw_lines())