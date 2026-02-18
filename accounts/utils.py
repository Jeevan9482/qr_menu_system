def get_user_hotel(user):
    if user.is_superuser:
        return None
    return user.hotelowner.hotel
