"""Output-path guard only, isolated from evaluation debug commands."""
from pathlib import Path
def separate_output(output, *sources):
    output = Path(output).resolve()
    for source in sources:
        source = Path(source).resolve()
        if output == source or output in source.parents or source in output.parents:
            raise ValueError('Output must be separate from input dataset and checkout')
    return output
