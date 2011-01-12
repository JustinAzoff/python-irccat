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

def maybe_int(s):
    if s.isdigit():
        return int(s)
    return s

import ConfigParser
def read_config(cfg_file):
    c = ConfigParser.ConfigParser()
    c.read([cfg_file])
    config = {}
    channels = []
    for section in c.sections():
        vars = dict(((k,maybe_int(v)) for (k,v) in c.items(section)))
        if section.startswith("channel_"):
            channels.append(vars)
        else:
            config[section] = vars
    config['channels'] = channels
    return config
