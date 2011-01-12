def extract_targets(line):
    """Return a list of targets seen in the beginning of a line
    targets start with @ or #"""
    if not line:
        return [], line

    if not line[0] in "#@":
        return [], line

    special_targets, line = line.split(None, 1)
    special_targets = special_targets.split(",")

    return special_targets, line
