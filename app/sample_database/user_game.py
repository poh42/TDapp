from models.user_game import UserGameModel


def get_relationships(games, users, consoles):
    return (
        # Maureen
        {
            "game": games["fifa20"],
            "user": users["maureen"],
            "console": consoles["playstation"],
            "gamertag": "maureen_fifa20",
        },
        # Asdrubal
        {
            "game": games["fifa20"],
            "user": users["asdrubal"],
            "console": consoles["xbox"],
            "gamertag": "asdru_fifa20",
        },
        {
            "game": games["rocket_league"],
            "user": users["asdrubal"],
            "console": consoles["pc"],
            "gamertag": "asdru_rocket",
        },
        # Roger
        {
            "game": games["pga_2k21"],
            "user": users["roger"],
            "console": consoles["xbox"],
            "gamertag": "roger_pga",
        },
        # Tom
        {
            "game": games["pga_2k21"],
            "user": users["tomas"],
            "console": consoles["xbox"],
            "gamertag": "tomas_pga",
        },
        # Phil
        {
            "game": games["madden21"],
            "user": users["phil"],
            "console": consoles["xbox"],
            "gamertag": "phil_nfl",
        },
        # Ryan
        {
            "game": games["madden21"],
            "user": users["ryan"],
            "console": consoles["xbox"],
            "gamertag": "ryan_nfl",
        },
        # Noah
        {
            "game": games["fifa20"],
            "user": users["noah"],
            "console": consoles["xbox"],
            "gamertag": "noah_fifa20",
        },
        {
            "game": games["fifa21"],
            "user": users["noah"],
            "console": consoles["playstation"],
            "gamertag": "noah_fifa21",
        },
        {
            "game": games["mario_kart"],
            "user": users["noah"],
            "console": consoles["xbox"],
            "gamertag": "noah_mario",
        },
        {
            "game": games["cod_modern_warfare"],
            "user": users["noah"],
            "console": consoles["playstation"],
            "gamertag": "noah_cod_modern",
        },
        {
            "game": games["cod_cold_war"],
            "user": users["noah"],
            "console": consoles["playstation"],
            "gamertag": "noah_cod_modern",
        },
        {
            "game": games["pga_2k21"],
            "user": users["noah"],
            "console": consoles["xbox"],
            "gamertag": "noah_pga",
        },
        {
            "game": games["madden21"],
            "user": users["noah"],
            "console": consoles["xbox"],
            "gamertag": "noah_nfl",
        },
        {
            "game": games["rocket_league"],
            "user": users["noah"],
            "console": consoles["pc"],
            "gamertag": "noah_rocket",
        },
    )


def save_user_game(value):
    """Saves a single user game"""
    console_id = value["console"].id
    user_id = value["user"].id
    gamertag = value["gamertag"]
    game_id = value["game"].id
    user_game = UserGameModel()
    user_game.console_id = console_id
    user_game.user_id = user_id
    user_game.game_id = game_id
    user_game.gamertag = gamertag
    user_game.save_to_db()
    return user_game


def save(games, users, consoles):
    values = get_relationships(games, users, consoles)
    ret_val = []
    for v in values:
        user_game = save_user_game(v)
        ret_val.append(user_game)
    return ret_val
