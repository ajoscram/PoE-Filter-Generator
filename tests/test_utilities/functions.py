from core import Filter, Block, Line, Sieve

def create_filter(text: str, filepath: str ="filepath"):
    lines = text.splitlines()
    blocks = Block.extract(lines)
    return Filter(filepath, blocks)

def create_sieve_for_text(text: str):
    raw_lines = text.splitlines()
    lines_range = range(len(raw_lines))
    lines = [
        Line(raw_line, i)
        for raw_line, i in zip(raw_lines, lines_range) ]
    return Sieve(lines)

def create_sieve_for_pattern(pattern: dict[str, str], operator: str = "=="):
    raw_lines = [
        f"{operand} {operator} {value}"
        for operand, value in pattern.items() ]
    return create_sieve_for_text("\n".join(raw_lines))