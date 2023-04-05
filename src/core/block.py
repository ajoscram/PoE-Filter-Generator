from .rule import Rule
from .line import Line

class Block:
    """A block is a collection of lines (strings) in a filter, which may include rules in them.
    
    Lines in a block may be appended, removed, commeted out or swapped for other lines.
    Blocks may have rules which can be obtained from this class.
    Rules are automatically extracted from lines when new lines are added.
    """

    def __init__(self, line_number: int):
        self.line_number: int = line_number
        self.lines: list[Line] = []

    @classmethod
    def extract(cls, raw_lines: list[str], line_number: int = 1):
        "Returns all blocks in a from a list of textual lines."
        if len(raw_lines) == 0:
            return []
        
        blocks: list[Block] = [ Block(line_number) ]
        for raw_line in raw_lines:
            line = Line(raw_line, line_number)
            if line.is_block_starter() and not blocks[-1].is_empty():
                blocks.append(Block(line_number))
            blocks[-1].lines.append(line)
            line_number +=1
        
        return blocks

    def is_empty(self):
        """Returns true if the block has no lines. False if it has any."""
        return len(self.lines) == 0

    def append(self, raw_line: str):
        """Appends the line at the end of the block."""
        line_number = self.line_number + len(self.lines)
        line = Line(raw_line, line_number)
        self.lines.append(line)

    def remove(self, pattern: str):
        """Removes all lines which include the specified pattern outside comments in them."""
        for i in range(len(self.lines)-1, 0, -1):
            if self.lines[i].contains(pattern):
                del self.lines[i]

    def comment(self, pattern: str = None):
        """Comments out every line with the specified pattern outside comments in them.
        If no pattern is provided then every line in the block is commented out instead."""
        for line in self.lines:
            if pattern == None or line.contains(pattern):
                line.comment()
    
    def uncomment(self, pattern: str = None):
        """Uncomments every line that has the pattern inside a comment.
        If no pattern is provided then every line in the block is uncommented."""
        for line in self.lines:
            if pattern == None or line.contains_in_comment(pattern):
                line.uncomment()

    def swap(self, pattern: str, raw_line: str):
        """Swaps out every line with the specified pattern outside comments in them for the raw_line provided."""
        for i in range(len(self.lines)):
            if self.lines[i].contains(pattern):
                self.lines[i] = Line(raw_line, self.lines[i].number)
    
    def hide(self):
        """Attempts to completely hide a block by setting it to 'Hide' and
        commenting out the lines that show effects on the screen if they are present."""
        self.swap("Show", "Hide")
        self.comment("PlayAlertSound")
        self.comment("PlayAlertSoundPositional")
        self.comment("CustomAlertSound")
        self.comment("CustomAlertSoundOptional")
        self.comment("MinimapIcon")
        self.comment("PlayEffect")
    
    def show(self):
        """Attempts to show a block fully, by setting it to 'Show' and un-commenting out
        the lines that show effects on the screen if they are present.
        This is the reverse function to hide."""
        self.swap("Hide", "Show")
        self.uncomment("PlayAlertSound")
        self.uncomment("PlayAlertSoundPositional")
        self.uncomment("CustomAlertSound")
        self.uncomment("CustomAlertSoundOptional")
        self.uncomment("MinimapIcon")
        self.uncomment("PlayEffect")

    def get_rules(self, name_or_names: str | list[str]) -> list[Rule]:
        """Gets all the rules in the block with name equals to rule_name."""
        return [ rule for line in self.lines for rule in line.get_rules(name_or_names) ]
    
    def get_raw_lines(self):
        return [ line.text for line in self.lines ]
                    
    def __str__(self):
        string = f"[{self.line_number}] Block"
        for line in self.lines:
            string += f"\n{line}"
        return string