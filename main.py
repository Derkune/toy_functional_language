from typing import Union


LangType = Union[int, tuple]


Pick_B = True
Pick_C = False


def Lang_choice_comparison(condition: LangType) -> bool:
    if isinstance(condition, tuple):
        condition = len(condition)

    if condition:
        return Pick_B
    else:
        return Pick_C


def Lang_compare(a: LangType, b: LangType) -> int:
    if isinstance(a, int) and isinstance(b, int):
        return int(a >= b)
    elif isinstance(a, tuple) and isinstance(b, tuple):
        return int(a == b)
    else:
        return int(isinstance(a, tuple))


def Lang_plus(a: LangType, b: LangType) -> LangType:
    if isinstance(a, int) and isinstance(b, int):
        return a + b
    elif isinstance(a, tuple) and isinstance(b, tuple):
        return a + b
    elif isinstance(a, tuple):
        return a + tuple([b])
    else:
        assert isinstance(b, tuple), "wrong type in Lang_plus"
        return tuple([a]) + b


def _list_difference(a: tuple, b: tuple) -> tuple:
    return tuple(item for item in a if item not in b)


def Lang_minus(a: LangType, b: LangType) -> LangType:
    if isinstance(a, int) and isinstance(b, int):
        return a - b
    elif isinstance(a, tuple) and isinstance(b, tuple):
        return _list_difference(a, b)
    elif isinstance(a, tuple):
        assert isinstance(b, int), "wrong type in Lang_minus"
        if len(a) == 0:
            return tuple()

        b = max(0, b)
        b = min(len(a) - 1, b)

        a = a[:b] + a[b + 1 :]
        return a
    else:
        assert isinstance(a, int), "wrong type in Lang_minus"
        assert isinstance(b, tuple), "wrong type in Lang_minus"

        if len(b) == 0:
            return tuple()

        a = max(0, a)
        a = min(len(b) - 1, a)

        return b[a]
    

def Lang_nesting(val: LangType) -> LangType:
    return (val, )


def main():
    print("Hello from toy-functional-language!")


if __name__ == "__main__":
    main()
