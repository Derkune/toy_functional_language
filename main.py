from typing import Any, Union, Tuple, Dict, Tuple, List, Callable, Optional
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
ENTRY_POINT: Position = -999, -999


@dataclass
class Function:
    symbol_mapping: Dict[Position, str]
    """Mapping from positions in the function to symbols at those positions"""
    input_mapping: Dict[Position, List[Position]]
    """Mapping from positions of function calls to tuples of function calls on which they depend"""
    input_positions: List[Position]
    """List of places where the argument values will be placed in FunctionFrame on evaluation"""


@dataclass
class FunctionFrame:
    function_reference: Function
    _arguments: List

    def __post_init__(self) -> None:
        self.arguments: Dict[Position, str] = {
            pos: arg
            for pos, arg in zip(
                self.function_reference.input_positions, self._arguments, strict=True
            )
        }

    def get_symbol_for_pos(self, pos: Position) -> str:
        """
        Return either the symbol representing a constant placed in place of an argument
        or a symbol in the body of the function.
        """
        if pos in self.arguments:
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


def execute(
    current_func: FunctionFrame,
    pos: Position,
    function_mapping: Dict[str, PossibleFunc],
) -> Constant:
    input_positions = current_func.function_reference.input_mapping[pos]
    symbol_on_pos = current_func.get_symbol_for_pos(pos)
    function_on_pos = function_mapping[symbol_on_pos]

    if isinstance(function_on_pos, ChoosePrimitive):
        choose_op = function_on_pos

        resolved_zeroth_input = execute(
            current_func, input_positions[0], function_mapping
        )
        chosen_argument_to_resolve_pos = choose_op(
            resolved_zeroth_input, input_positions
        )
        return execute(current_func, chosen_argument_to_resolve_pos, function_mapping)
    elif isinstance(function_on_pos, Constant):
        constant = function_on_pos
        return constant

    resolved_inputs: List[Constant] = []
    for input_pos in input_positions:
        resolved_inputs.append(execute(current_func, input_pos, function_mapping))

    if isinstance(function_on_pos, Operation):
        operation = function_on_pos
        return operation(resolved_inputs)
    else:
        new_frame = FunctionFrame(function_on_pos, resolved_inputs)
        return execute(new_frame, ENTRY_POINT, function_mapping)


def main():
    print("Hello from toy-functional-language!")


if __name__ == "__main__":
    main()
