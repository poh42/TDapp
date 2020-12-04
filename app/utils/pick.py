def pick_from_dict(my_dict, keys):
    """Akin to lodash's pick function."""
    ret_val = dict()
    for key in keys:
        ret_val[key] = my_dict[key]
    return ret_val
