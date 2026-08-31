from utils.text import truncate


def test_truncate():
    short_str = "test_str_1"

    result = truncate(short_str)

    assert result == short_str

    max_length = 64
    str_longer_than_max_length = "a" * 65

    result = truncate(str_longer_than_max_length)

    assert result == str_longer_than_max_length[: max_length - 3] + "..."
