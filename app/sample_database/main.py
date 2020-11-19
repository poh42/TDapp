from sample_database.console import save as save_consoles


def create_fixtures():
    consoles = save_consoles()
    return {"consoles": consoles}
