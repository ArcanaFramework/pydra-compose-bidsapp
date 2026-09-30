import shlex


def flags_converter(value: str | list[str]) -> list[str]:
    if isinstance(value, str):
        return shlex.split(value)
    return list(value)
