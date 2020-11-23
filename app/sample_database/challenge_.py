from models.challenge_ import (
    STATUS_COMPLETED,
    STATUS_ACCEPTED,
    STATUS_PENDING,
    STATUS_OPEN,
    STATUS_REJECTED,
)


def get_challenges(games):
    challenges = {
        "maureen_asdrubal_1": {
            "game_id": games["fifa20"].id,
            "buy_in": 25,
            "reward": 25,
            "status": STATUS_COMPLETED,
            "date": "2020-09-12 00:00:00",
            "due_date": "2020-09-12 23:59:59",
        },
        "roger_tomas": {
            "game_id": games["pga_2k21"].id,
            "buy_in": 30,
            "reward": 30,
            "status": STATUS_ACCEPTED,
            "date": "2020-12-12 00:00:00",
            "due_date": "2020-12-12 23:59:59",
        },
        "phil_ryan": {
            "game_id": games["madden21"].id,
            "buy_in": 20,
            "reward": 20,
            "status": STATUS_PENDING,
            "date": "2020-12-01 00:00:00",
            "due_date": "2020-12-01 23:59:59",
        },
        "noah": {
            "game_id": games["rocket_league"].id,
            "buy_in": 30,
            "reward": 30,
            "status": STATUS_OPEN,
            "date": "2021-01-21 00:00:00",
            "due_date": "2021-01-21 23:59:59",
        },
        "maureen_asdrubal_2": {
            "game_id": games["fifa20"].id,
            "buy_in": 100,
            "reward": 100,
            "status": STATUS_REJECTED,
            "date": "2020-11-03 00:00:00",
            "due_date": "2020-11-03 23:59:59",
        },
    }
    return challenges
