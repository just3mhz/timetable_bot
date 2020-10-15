def float_to_time(x: float):
    """
    Seems that excel saves time fields as float number,
    but string 'hh:mm' is expected. So this function
    converts float number to necessary format.

    TODO: This function is not accurate

    :param x: time in excel format
    :return: string 'hh:mm'
    """
    minutes_in_day = 24 * 60
    hours = x * minutes_in_day / 60
    minutes = x * minutes_in_day % 60
    return "%02d:%02d" % (hours, minutes)
