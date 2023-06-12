from core import Filter, Block

def create_filter(text: str):
    lines = text.splitlines()
    blocks = Block.extract(lines)
    return Filter("filepath", blocks)