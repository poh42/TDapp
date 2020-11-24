def get_friendships(users):
    return (
        (users["maureen"], users["asdrubal"]),
        (users["phil"], users["ryan"]),
    )


def save(users):
    friendships = get_friendships(users)
    for friend1, friend2 in friendships:
        friend1.add_friend(friend2.id)
    return friendships
