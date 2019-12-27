import rule

class Section:
    """A Section is a collection of lines (strings) in a filter, which may include rules in them.
    
    Lines in a section may be appended, removed, commeted out or swapped for other lines.
    Sections may have rules which can be obtained from this class.
    Rules are automatically extracted from lines when new lines are added.
    """

    def __init__(self, line_number: int):
        """Section constructor which only receives the line number where the section starts."""
        self.line_number = line_number
        self.lines = []
        self.rules = []

    def append(self, line: str):
        """Appends the line at the end of the section. If any rules are present, they are extracted. Multiline strings are not allowed."""
        #validate for multiline strings
        #extract rules from the line
        #add rules to the list of rules
        #add the line

    def remove(self, pattern: str):
        """Removes all lines which include the specified pattern outside comments in them. If the line(s) included any rules, they are removed as well."""
        pass

    def comment(self, pattern: str):
        """Comments out every line with the specified pattern outside comments in them."""
        pass

    def swap(self, pattern: str, line: str):
        """Swaps out every line with the specified pattern outside comments in them for the line provided. If the old line(s) included any rules, they are removed. If the new line includes any rules, they are added. Multiline strings are not allowed."""
        pass