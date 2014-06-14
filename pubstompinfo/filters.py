from flask import current_app
from datetime import datetime, timedelta


def escape_every_character(text):
    """ Returns the string provided encoded as html-entities.

    Sets up a generator iterating through `text`, formatting the ordinal of each character as a HTML entity.
    This generator is then passed to the str.join function to construct a new string of these encoded entities.

    :param text: The string to be encoded.
    :return: A string of html-entities representing the given `text`.
    """
    return "".join("&#{};".format(ord(x)) for x in text)


def timestamp_to_datestring(timestamp, _format=None):
    """
    Takes a unix timestamp and returns a string representing that date (in the format given).

    :param timestamp: A unix timestamp.
    :param _format: The format to render the date as.  Defaults to the format specified in the site's config.
    :return: A str representing the given timestamp.
    """
    """ Take a timestamp and output it in the format specified in the site's config. """
    _format = _format or current_app.config["DATE_STRING_FORMAT"]
    return datetime.utcfromtimestamp(int(timestamp)).strftime(_format)


def datetime_to_datestring(_input, _format=None):
    """
    Takes a datetime object and returns a string representing that date (in the format given).

    :param _input: A datetime object.
    :param _format: The format to render the date as.  Defaults to the format specified in the site's config.
    :return: A str representing the given timestamp.
    :return: None if the `_input` was not a datetime object.
    """

    _format = _format or current_app.config["DATE_STRING_FORMAT"]
    if isinstance(_input, datetime):
        return _input.strftime(_format)
    else:
        return None


def seconds_to_time(seconds):
    """
    Takes an integer of seconds, and outputs it formatted as a time string (00:00:00)

    :param seconds: An integer representing number o f seconds
    :return: A str which is the `seconds` as a time string (00:00:00)
    """
    return str(timedelta(seconds=seconds or 0))
