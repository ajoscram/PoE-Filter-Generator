from .rule import Rule 

class Section:
    """A Section is a collection of lines (strings) in a filter, which may include rules in them.
    
    Lines in a section may be appended, removed, commeted out or swapped for other lines.
    Sections may have rules which can be obtained from this class.
    Rules are automatically extracted from lines when new lines are added.
    """

    COMMENT_START = '#'

    def __init__(self, line_number: int):
        """Section constructor which only receives the line number where the section starts."""
        self.line_number = line_number
        self.lines = []
        self.rules = []

    def is_empty(self):
        """Returns true if the section has no lines. False if it has any."""
        return len(self.lines) == 0

    def append(self, line: str):
        """Appends the line at the end of the section. If any rules are present, they are extracted. Multiline strings are not allowed."""
        line_number = self.line_number + len(self.lines)
        if '\n' in line:
            raise SectionError(SectionError.MULTILINE_STRING, line_number)
        rules = Rule.extract(line_number, line)
        self.rules.extend(rules)
        self.lines.append(line)

    def remove(self, pattern: str):
        """Removes all lines which include the specified pattern outside comments in them. If the line(s) included any rules, they are removed as well."""
        #traverse the list of lines backwards because items could get deleted
        for i in range(len(self.lines)-1, 0, -1):
            line = self.lines[i]
            #remove the comment from the line
            line = line.split(self.COMMENT_START)[0]
            if pattern in line:
                del self.lines[i]
                #all rules associated with this line must be removed
                for rule in reversed(self.rules):
                    #all rules associated with this line must be removed
                    if rule.line_number == self.line_number + i:
                        self.rules.remove(rule)
                    #all rules with a line number greater than the one removed must be updated
                    if rule.line_number > self.line_number + i:
                        rule.line_number -= 1

    def comment(self, pattern: str):
        """Comments out every line with the specified pattern outside comments in them."""
        for i in range(len(self.lines)):
            line = self.lines[i]
            #remove the comment from the line
            line = line.split(self.COMMENT_START)[0]
            if pattern in line:
                self.lines[i] = "#" + self.lines[i]
    
    def uncomment(self, pattern):
        """Removes the left-most # (hashtag) in every line that has the pattern inside a comment."""
        for i in range(len(self.lines)):
            split_line = self.lines[i].split(self.COMMENT_START, 1)
            if len(split_line) == 2 and pattern in split_line[1]:
                self.lines[i] = split_line[0] + split_line[1]

    def swap(self, pattern: str, line: str):
        """Swaps out every line with the specified pattern outside comments in them for the line provided. Multiline strings are not allowed."""
        for i in range(len(self.lines)):
            #split the old line into actual line and comment
            old_line = self.lines[i].split(self.COMMENT_START, 1)
            if pattern in old_line[0]:
                #all rules associated with the old line must be removed
                for rule in reversed(self.rules):
                    if rule.line_number == self.line_number + i:
                        self.rules.remove(rule)
                #new rules associated with the new line must be added
                rules = Rule.extract(i, line)
                self.rules.extend(rules)
                #finally the line is swapped, with the comment readded if it had one
                if len(old_line) == 1:
                    self.lines[i] = line
                elif len(old_line) > 1:
                    self.lines[i] = line + self.COMMENT_START + old_line[1]
    
    def __str__(self):
        line_number = self.line_number
        string = "Line Number: " + str(line_number) + '\n'
        string += "Rules:\n"
        if len(self.rules) == 0:
            string += '\tNone\n'
        else:
            for rule in self.rules:
                string += '\t' + str(rule) + '\n'
        string += "Lines:"
        for line in self.lines:
            string += '\n[' + str(line_number) + '] ' + line
            line_number += 1
        return string

class SectionError(Exception):
    """Class for section exception handling."""

    #Error message constants
    MULTILINE_STRING = "Multiline string"

    def __init__(self, line_number: int, message: str):
        """Takes a message from the caller and a line number where the error occurred."""
        self.message = message
        self.line_number = line_number