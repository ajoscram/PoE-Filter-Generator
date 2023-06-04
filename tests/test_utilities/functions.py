from core import Filter, Block

def create_filter(text: str, *formattables):
    text = text.format(*formattables)
    lines = text.splitlines()
    blocks = Block.extract(lines)
    return Filter("filepath", blocks)