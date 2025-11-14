from typing import Any, Union, Tuple, Dict, Tuple, List, Callable, Optional, Generator
from dataclasses import dataclass


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
    return (val,)


Position = Tuple[int, int]


class SpecialPosition:
    pass


ENTRY_POINT: SpecialPosition = SpecialPosition()


@dataclass
class Function:
    symbol_mapping: Dict[Position, str]
    """Mapping from positions in the function to symbols at those positions"""
    input_mapping: Dict[Union[SpecialPosition, Position], List[Position]]
    """Mapping from positions of function calls to tuples of function calls on which they depend"""
    input_positions: List[SpecialPosition]
    """List of places where the argument values will be placed in FunctionFrame on evaluation"""


@dataclass
class FunctionFrame:
    function_reference: Function
    _arguments: List

    def __post_init__(self) -> None:
        self.arguments: Dict[SpecialPosition, str] = {
            pos: arg
            for pos, arg in zip(
                self.function_reference.input_positions, self._arguments, strict=True
            )
        }

    def get_symbol_for_pos(self, pos: Union[SpecialPosition, Position]) -> str:
        """
        Return either the symbol representing a constant placed in place of an argument
        or a symbol in the body of the function.
        """
        if isinstance(pos, SpecialPosition):
            return self.arguments[pos]

        return self.function_reference.symbol_mapping[pos]


class Constant:
    pass


class Operation:
    def __call__(self, *args: Any, **kwds: Any) -> Constant:
        """Placeholder"""
        ...


class ChoosePrimitive:
    """Evaluates the 0th argument, and chooses 1st or 2nd to evaluate and return"""

    def __call__(self, *args: Any, **kwds: Any) -> Position:
        """Placeholder"""
        ...


PossibleFunc = Union[Operation, Constant, Function, ChoosePrimitive]


ExecuteGenReturnType = Generator[str, None, Constant]


def _handle_choose_gen(
    current_func: FunctionFrame,
    choose_op: ChoosePrimitive,
    input_positions: List[Position],
    function_mapping: Dict[str, PossibleFunc],
) -> ExecuteGenReturnType:
    """Handles the lazy evaluation of the ChoosePrimitive."""
    resolved_condition = yield from _execute_gen(
        current_func, input_positions[0], function_mapping
    )
    chosen_pos = choose_op(resolved_condition, input_positions[1], input_positions[2])
    ret_val = yield from _execute_gen(current_func, chosen_pos, function_mapping)
    return ret_val


def _resolve_all_inputs_gen(
    current_func: FunctionFrame,
    input_positions: List[Position],
    function_mapping: Dict[str, PossibleFunc],
) -> Generator[str, None, List[Constant]]:
    """Recursively executes all inputs and returns the resulting constants."""
    ret_val: List[Constant] = []
    for input_pos in input_positions:
        item_val = yield from _execute_gen(current_func, input_pos, function_mapping)
        ret_val.append(item_val)

    return ret_val


def _handle_operation_gen(
    current_func: FunctionFrame,
    operation: Operation,
    input_positions: List[Position],
    function_mapping: Dict[str, PossibleFunc],
) -> ExecuteGenReturnType:
    """Resolves all inputs and applies the operation to them."""
    resolved_inputs = yield from _resolve_all_inputs_gen(
        current_func, input_positions, function_mapping
    )
    return operation(*resolved_inputs)


def _handle_user_function_gen(
    current_func: FunctionFrame,
    user_function: Function,
    input_positions: List[Position],
    function_mapping: Dict[str, PossibleFunc],
) -> ExecuteGenReturnType:
    """Resolves all inputs and executes a user-defined function in a new frame."""
    resolved_inputs = yield from _resolve_all_inputs_gen(
        current_func, input_positions, function_mapping
    )
    new_frame = FunctionFrame(user_function, resolved_inputs)
    ret_val = yield from _execute_gen(new_frame, ENTRY_POINT, function_mapping)
    return ret_val


def _execute_gen(
    current_func: FunctionFrame,
    pos: Union[SpecialPosition, Position],
    function_mapping: Dict[str, PossibleFunc],
) -> ExecuteGenReturnType:
    symbol_on_pos = current_func.get_symbol_for_pos(pos)
    function_on_pos = function_mapping[symbol_on_pos]

    if isinstance(function_on_pos, Constant):
        return function_on_pos

    input_positions = current_func.function_reference.input_mapping[pos]

    if isinstance(function_on_pos, ChoosePrimitive):
        choose_val = yield from _handle_choose_gen(
            current_func, function_on_pos, input_positions, function_mapping
        )
        return choose_val
    elif isinstance(function_on_pos, Operation):
        op_val = yield from _handle_operation_gen(
            current_func, function_on_pos, input_positions, function_mapping
        )
        return op_val
    elif isinstance(function_on_pos, Function):
        func_val = yield from _handle_user_function_gen(
            current_func, function_on_pos, input_positions, function_mapping
        )
        return func_val
    else:
        raise TypeError(f"Unexpected type at position {pos}: {type(function_on_pos)}")


def execute_entry(
    current_func: FunctionFrame,
    pos: Position,
    function_mapping: Dict[str, PossibleFunc],
) -> Constant:
    gen_obj: ExecuteGenReturnType = _execute_gen(current_func, pos, function_mapping)
    while True:
        try:
            trace = next(gen_obj)
            print(trace)
        except StopIteration as e:
            print(f"\nFinal Result: {e.value}")
            return e.value


def main():
    print("Hello from toy-functional-language!")


if __name__ == "__main__":
    main()
