"""
Implementation of essential functions and components for a `BaseJob`.

Author: Jendrik A. Potyka, Fabian A. Preiss
"""


def str_cutoff(string: str, max_length: int, cut_tail: bool = False) -> str:
    """
    Abbreviate a string to a given length.

    The resulting string will carry an indicator if it's abbreviated,
    like ``stri#``.

    Parameters
    ----------
    string : str
        String which is to be cut.
    max_length : int
        Max resulting string length.
    cut_tail : bool
        ``False`` for string abbreviation from the front, else ``True``.

    Returns
    -------
    str
        Resulting string
    """
    if max_length < 1:
        raise ValueError("max_length < 1 not allowed")

    if len(string) > max_length:
        pos = max_length - 1
        return string[:pos] + "#" if cut_tail else "#" + string[-pos:]

    return string
