def extract_targets(line):
    """Return a list of targets seen in the beginning of a line
    targets start with @ or #"""
    if not line:
        return [], line

    if not line[0] in "#@":
        return [], line

    targets, line = line.split(None, 1)
    special_targets = targets.split(",")
    #channels need #, but usernames should be bare
    special_targets = [t.lstrip("@") for t in special_targets]

    return special_targets, line
