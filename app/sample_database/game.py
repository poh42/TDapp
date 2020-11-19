from models.game import GameModel


def create_game(game_data):
    game = GameModel(**game_data)
    game.save_to_db()
    return game


games = {
    "fifa20": {
        "image": "https://flashdrive69.s3.amazonaws.com/05541a32827c5482b75e22c1e8c1ec350c7434632ea64e70ee0836223c2a8fb6.jpg",
        "name": "FIFA 20",
        "is_active": True,
    },
    "fifa21": {
        "image": "https://flashdrive69.s3.amazonaws.com/227103000acf5ef3ab7433f7550b372558160bfbb3a84f6a5174ca9bcd5516af.png",
        "name": "FIFA 21",
        "is_active": True,
    },
    "mario_kart": {
        "image": "https://flashdrive69.s3.amazonaws.com/48093331d420f6fc5ed18ddd72dd47d7a7e61b637b4eb44ab66abe220d5a5357.jpg",
        "name": "Mario Kart Deluxe",
        "is_active": True,
    },
    "cod_modern_warfare": {
        "image": "https://flashdrive69.s3.amazonaws.com/187bc596c6210f4ca0540c982ff9d923a192fae9b81d427c7e8a88a8bf1cfc35.jpeg",
        "name": "COD - Modern Warfare",
        "is_active": True,
    },
    "pga_2k21": {
        "image": "https://flashdrive69.s3.amazonaws.com/3c41401f32cc7b0ba7dac97373cd8f97b2014f91251fa6a21da8959536924f36.jpg",
        "name": "PGA 2K21",
        "is_active": True,
    },
    "cod_cold_war": {
        "image": "https://flashdrive69.s3.amazonaws.com/905a82df658a54d90c0fb6a8e8c14f46e9ff761ee07055802574fd8132ca39f7.jpeg",
        "name": "COD - Cold War",
        "is_active": True,
    },
    "madden21": {
        "image": "https://flashdrive69.s3.amazonaws.com/f16bdecc705589a3a2ab9e2fcd8169eec53052148454f62073be1555d1764b04.jpg",
        "name": "NFL Madden 21",
        "is_active": True,
    },
    "rocket_league": {
        "image": "https://flashdrive69.s3.amazonaws.com/60ed6e46e830706baf0932b22a483a2c0ab838e686a9ec7c5a970bbce32759c6.png",
        "name": "Rocket League",
        "is_active": True,
    },
}


def save():
    ret_val = dict()
    for key, value in games.items():
        ret_val[key] = create_game(value)
    return ret_val
