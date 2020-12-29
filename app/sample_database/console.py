from models.console import ConsoleModel


def create_console(console_data):
    console = ConsoleModel(**console_data)
    console.save_to_db()
    return console


consoles = {
    "playstation": {"name": "PlayStation"},
    "xbox": {"name": "Xbox"},
    "pc": {"name": "PC"},
    "cross-platform": {"name": "Cross-Platform"},
    "nintendo-switch": {"name": "Nintendo Switch"},
}


def save():
    ret_val = dict()
    for key, value in consoles.items():
        ret_val[key] = create_console(value)
    return ret_val
