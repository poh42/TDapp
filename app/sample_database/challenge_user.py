from models.challenge_user import (
    STATUS_COMPLETED,
    STATUS_OPEN,
    STATUS_ACCEPTED,
    STATUS_PENDING,
    STATUS_REJECTED,
    ChallengeUserModel,
)


def get_challenge_users(challenges, users):
    return (
        # Maureen vs Asdrubal, FIFA, Sept 12, completed, 1 to 0, 25 Credits
        {
            "challenger_id": users["maureen"].id,
            "challenged_id": users["asdrubal"].id,
            "wager_id": challenges["maureen_asdrubal_1"].id,
            "status": STATUS_COMPLETED,
        },
        {
            "challenger_id": users["maureen"].id,
            "challenged_id": users["maureen"].id,
            "wager_id": challenges["maureen_asdrubal_1"].id,
            "status": STATUS_COMPLETED,
        },
        # Roger vs Tomas, PGA, Dec 12, Accepted, 30 Credits
        {
            "challenger_id": users["roger"].id,
            "challenged_id": users["roger"].id,
            "wager_id": challenges["roger_tomas"].id,
            "status": STATUS_OPEN,
        },
        {
            "challenger_id": users["roger"].id,
            "challenged_id": users["tomas"].id,
            "wager_id": challenges["roger_tomas"].id,
            "status": STATUS_ACCEPTED,
        },
        # Phil vs Ryan, Dec 1st, Pending, 20 credits
        {
            "challenger_id": users["phil"].id,
            "challenged_id": users["phil"].id,
            "wager_id": challenges["phil_ryan"].id,
            "status": STATUS_OPEN,
        },
        {
            "challenger_id": users["phil"].id,
            "challenged_id": users["ryan"].id,
            "wager_id": challenges["phil_ryan"].id,
            "status": STATUS_PENDING,
        },
        # Noah, Rocket League, Jan 21, Open, 30 credits
        {
            "challenger_id": users["noah"].id,
            "challenged_id": users["noah"].id,
            "wager_id": challenges["noah"].id,
            "status": STATUS_OPEN,
        },
        # Maureen vs Asdrubal FIFA 20, Nov 3rd, Rejected, 100 Credits
        {
            "challenger_id": users["maureen"].id,
            "challenged_id": users["maureen"].id,
            "wager_id": challenges["maureen_asdrubal_2"].id,
            "status": STATUS_OPEN,
        },
        {
            "challenger_id": users["maureen"].id,
            "challenged_id": users["asdrubal"].id,
            "wager_id": challenges["maureen_asdrubal_2"].id,
            "status": STATUS_REJECTED,
        },
    )


def create_challenge_user(challenge_user_data):
    challenge_user = ChallengeUserModel(**challenge_user_data)
    challenge_user.save_to_db()
    return challenge_user


def save(challenges, users):
    challenge_users = get_challenge_users(challenges, users)
    ret_val = []
    for item in challenge_users:
        cu = create_challenge_user(item)
        ret_val.append(cu)
    return ret_val
