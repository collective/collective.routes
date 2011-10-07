

def smart_update(d1, d2):
    for key, value in d2.items():
        if key in d1:
            orig = d1[key]
            if type(orig) not in (tuple, set, list):
                orig = set([orig])
            orig = set(orig)
            orig.add(value)
            d1[key] = orig
        else:
            d1[key] = value
    return d1
