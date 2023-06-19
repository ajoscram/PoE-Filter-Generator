from core import Filter, Block

def create_filter(text: str, filepath: str ="filepath"):
    lines = text.splitlines()
    blocks = Block.extract(lines)
    return Filter(filepath, blocks)