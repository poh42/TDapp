from models.results_1v1 import Results1v1Model


def get_results_1v1(challenges, users):
    return {
        "maureen_asdrubal_1": {
            "challenge_id": challenges["maureen_asdrubal_1"].id,
            "score_player_1": 1,
            "score_player_2": 0,
            "winner_id": users["maureen"].id,
            "player_1_id": users["maureen"].id,
            "player_2_id": users["asdrubal"].id,
            "played": "2020-09-12 12:00:00",
        }
    }


def create_result_1v1(data):
    results_1v1 = Results1v1Model(**data)
    results_1v1.save_to_db()
    return results_1v1


def save(challenges, users):
    results = get_results_1v1(challenges, users)
    ret_val = dict()
    for key, value in results.items():
        ret_val[key] = create_result_1v1(value)
    return ret_val
