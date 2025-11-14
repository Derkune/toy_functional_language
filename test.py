from typing import Dict

from main import (
    LangType,
    Lang_choice_comparison,
    Lang_compare,
    Lang_plus,
    Lang_minus,
    Lang_nesting,
    Function,
    ENTRY_POINT,
    ARG1,
    ARG0,
    PossibleFunc,
    OperationPlus,
    execute_entry,
)


def test_1() -> None:
    def multiply(a: LangType, b: LangType) -> LangType:
        if Lang_choice_comparison(b):
            return Lang_plus(a, multiply(a, Lang_minus(b, 1)))
        else:
            return 0

    def exponentiate(base: LangType, power: LangType) -> LangType:
        if Lang_choice_comparison(power):
            return multiply(base, exponentiate(base, Lang_minus(power, 1)))
        else:
            return 1

    def n_to_power_n(n: LangType) -> LangType:
        return exponentiate(n, n)

    print(n_to_power_n(5))
    pass


def test_2() -> None:
    def find_idx_of_max_positive_element(
        lst: LangType, iter_idx: LangType, found_idx: LangType, found_item: LangType
    ) -> LangType:
        iter_item = Lang_minus(0, lst)

        item_comparison_result = Lang_compare(iter_item, found_item)

        if Lang_choice_comparison(item_comparison_result):
            new_found_idx = iter_idx
            new_found_item = iter_item
        else:
            new_found_idx = found_idx
            new_found_item = found_item

        if Lang_choice_comparison(lst):
            return find_idx_of_max_positive_element(
                Lang_minus(lst, 0),
                Lang_plus(iter_idx, 1),
                new_found_idx,
                new_found_item,
            )
        else:
            return found_idx

    def detect_if_val_is_list(val: LangType) -> LangType:
        val = Lang_minus(val, val)
        val = Lang_plus(val, 0)
        val = Lang_plus(val, 0)
        val = Lang_minus(val, 0)
        return Lang_compare(val, 1)

    def addition_with_possible_tuple(lst: LangType, item: LangType) -> LangType:
        if Lang_choice_comparison(detect_if_val_is_list(item)):
            return Lang_plus(lst, Lang_nesting(item))
        else:
            return Lang_plus(lst, item)

    def sort(lst: LangType) -> LangType:
        idx_of_max_element = find_idx_of_max_positive_element(lst, 0, -1, -1)

        leftover_lst_without_idx = Lang_minus(lst, idx_of_max_element)
        element_at_idx = Lang_minus(idx_of_max_element, lst)

        if Lang_choice_comparison(lst):
            return addition_with_possible_tuple(
                sort(leftover_lst_without_idx), element_at_idx
            )
        else:
            return tuple()

    print(detect_if_val_is_list(0))
    print(detect_if_val_is_list(1))
    print(detect_if_val_is_list(-1))
    print(detect_if_val_is_list(2))
    print(detect_if_val_is_list(-2))

    print(detect_if_val_is_list((0, 1)))
    print(detect_if_val_is_list(()))
    print(detect_if_val_is_list((0,)))
    print(detect_if_val_is_list((1,)))
    print(detect_if_val_is_list((0, 1, 3)))

    print(sort((3, 2, 1)))
    print(sort((9, 8, 7, 6, 5, 4, 3, 2, 1)))
    print(sort((0, 4, 5, 1, (0, 0), 4, 2, 3)))
    pass


def fib_trace_gen(n: int):
    """
    A recursive generator that calculates fib(n) and yields its execution trace.

    Yields: A tuple of (trace_string, depth_level)
    Returns: The integer result of fib(n)
    """

    # We'll use a helper to manage the call depth for nice indented printing
    def _fib_helper(n: int, depth: int):
        indent = "  " * depth
        yield (f"{indent}-> Calling fib({n})", depth)

        # Base Case
        if n <= 1:
            yield (f"{indent}   Base case, returning {n}", depth)
            return n

        # Recursive Step 1: Call fib(n-1)
        # The 'yield from' will delegate to the recursive call, yielding all its trace steps.
        # When it's done, its 'return' value is captured in 'res1'.
        res1 = yield from _fib_helper(n - 1, depth + 1)
        yield (f"{indent}<- Resumed fib({n}). Got {res1} from fib({n-1}) call.", depth)

        # Recursive Step 2: Call fib(n-2)
        res2 = yield from _fib_helper(n - 2, depth + 1)
        yield (f"{indent}<- Resumed fib({n}). Got {res2} from fib({n-2}) call.", depth)

        # Final result calculation
        final_result = res1 + res2
        yield (f"{indent}<- Returning {final_result} for fib({n})", depth)
        return final_result

    # Start the helper from the top level (depth 0)
    final_value = yield from _fib_helper(n, 0)
    return final_value


def run_and_get_result(gen_obj):
    """
    Consumes a generator that yields traces and returns its final value.
    """
    while True:
        try:
            # Get the next yielded item
            aaa = next(gen_obj)
            # Optional: Do something with the yielded item, like print it
            print(aaa)
        except StopIteration as e:
            # The generator is exhausted. The return value is in e.value.
            # We break the loop and return this value.
            return e.value


def test_3():
    gen = fib_trace_gen(10)
    result = run_and_get_result(gen)
    print(result)


def test_4():
    function1: Function = Function(
        symbol_mapping={
            (0, 0): "+",
            (-1, 0): "+",
            (1, 0): "+",
            (-2, 0): "7",
            (2, 0): "8",
        },
        input_mapping={
            ENTRY_POINT: [(0, 0)],
            (0, 0): [(-1, 0), (1, 0)],
            (-1, 0): [(-2, 0), ARG0],
            (1, 0): [(2, 0), ARG1],
        },
        input_positions=[
            ARG0,
            ARG1,
        ],
    )

    function_mapping: Dict[str, PossibleFunc] = {
        "+": OperationPlus(),
        "f1": function1,
        "7": 7,
        "8": 8,
    }

    execute_entry(function1, ENTRY_POINT, function_mapping, [1, 2])


if __name__ == "__main__":
    test_1()
    test_2()
    test_3()
    test_4()
