from tweeapi import APISingleton

def followUsers(userInfo,  users):
    api = APISingleton.getInstanceForUser(userInfo)
    for user in users:
        api.create_friendship(user_id=user.id)
