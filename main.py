from typing import (
    Any,
    Union,
    Tuple,
    Dict,
    Tuple,
    List,
    Callable,
    Optional,
    Generator,
    Final,
)
from dataclasses import dataclass
import enum


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


@dataclass
class SpecialPosition:
    hash_arg: str

    def __hash__(self) -> int:
        return hash(self.hash_arg)

    def __eq__(self, value: object) -> bool:
        return isinstance(value, SpecialPosition) and value.hash_arg == self.hash_arg

    def __str__(self) -> str:
        return self.hash_arg


GeneralizedPosition = Union[Position, SpecialPosition]


ENTRY_POINT: SpecialPosition = SpecialPosition("ENTRY_POINT")
ARG0: SpecialPosition = SpecialPosition("ARG0")
ARG1: SpecialPosition = SpecialPosition("ARG1")
ARG2: SpecialPosition = SpecialPosition("ARG2")


@dataclass(kw_only=True)
class Function:
    symbol_mapping: Dict[Position, str]
    """Mapping from positions in the function to symbols at those positions"""
    input_mapping: Dict[GeneralizedPosition, List[GeneralizedPosition]]
    """Mapping from positions of function calls to tuples of function calls on which they depend"""
    input_positions: List[SpecialPosition]
    """List of places where the argument values will be placed in FunctionFrame on evaluation"""
    symbol: str

    def __str__(self) -> str:
        return f"{self.symbol}: {len(self.input_positions)} args, {len(self.symbol_mapping)} symbols"


@dataclass
class FunctionFrame:
    function_reference: Function
    _arguments: List[LangType]

    def __post_init__(self) -> None:
        self.arguments: Dict[SpecialPosition, LangType] = {
            pos: arg
            for pos, arg in zip(
                self.function_reference.input_positions, self._arguments, strict=True
            )
        }

    def get_symbol_for_pos(
        self, pos: GeneralizedPosition
    ) -> Tuple[Union[str, LangType], GeneralizedPosition]:
        """
        Return either the symbol representing a constant placed in place of an argument
        or a symbol in the body of the function.
        """
        if isinstance(pos, SpecialPosition):
            if pos is ENTRY_POINT:
                entry_pos = self.function_reference.input_mapping[ENTRY_POINT]
                assert (
                    len(entry_pos) == 1
                ), "input_mapping to ENTRY_POINT should contain 1 Position"
                assert isinstance(
                    entry_pos[0], tuple
                ), "input_mapping to ENTRY_POINT should contain 1 Position"
                symbol_on_pos = self.function_reference.symbol_mapping[entry_pos[0]]
                return symbol_on_pos, entry_pos[0]

            return self.arguments[pos], pos

        return self.function_reference.symbol_mapping[pos], pos


class Operation:
    def __call__(self, *args: Any, **kwds: Any) -> LangType:
        """Placeholder"""
        ...

    def __hash__(self) -> int: ...

    def __eq__(self, value: object) -> bool:
        return type(value) is type(self)

    def __str__(self) -> str:
        return "IMPLEMENT_OPERATION_STR"


class OperationCompare(Operation):
    def __call__(self, *args: Any, **kwds: Any) -> LangType:
        return Lang_compare(*args)

    def __hash__(self) -> int:
        return hash(">")

    def __str__(self) -> str:
        return "≥"


class OperationPlus(Operation):
    def __call__(self, *args: Any, **kwds: Any) -> LangType:
        return Lang_plus(*args)

    def __hash__(self) -> int:
        return hash("+")

    def __str__(self) -> str:
        return "+"


class OperationMinus(Operation):
    def __call__(self, *args: Any, **kwds: Any) -> LangType:
        return Lang_minus(*args)

    def __hash__(self) -> int:
        return hash("-")

    def __str__(self) -> str:
        return "-"


class OperationNest(Operation):
    def __call__(self, *args: Any, **kwds: Any) -> LangType:
        return Lang_nesting(*args)

    def __hash__(self) -> int:
        return hash("~")

    def __str__(self) -> str:
        return "~"


class ChoosePrimitive:
    """Evaluates the 0th argument, and chooses 1st or 2nd to evaluate and return"""

    def __call__(
        self,
        condition: LangType,
        pos1: GeneralizedPosition,
        pos2: GeneralizedPosition,
    ) -> GeneralizedPosition:
        if Lang_choice_comparison(condition):
            return pos1
        else:
            return pos2

    def __str__(self) -> str:
        return "?"

    def __hash__(self) -> int:
        return hash("?")

    def __eq__(self, value: object) -> bool:
        return type(value) is type(self)


PossibleFunc = Union[Operation, LangType, Function, ChoosePrimitive]


class YieldType(enum.Enum):
    FUNCTION_ENTRY = enum.auto()
    FUNCTION_CALL = enum.auto()
    GOT_BACK_FROM_FUNCTION_CALL = enum.auto()
    RETURN = enum.auto()


@dataclass
class YieldData:
    yield_type: YieldType
    call_depth: int
    message: str

    def __str__(self) -> str:
        return f"{self.call_depth * '.'}{self.yield_type.name} {self.message}"


ExecuteGenReturnType = Generator[YieldData, None, LangType]


def _handle_choose_gen(
    current_func: FunctionFrame,
    choose_op: ChoosePrimitive,
    input_positions: List[GeneralizedPosition],
    function_mapping: Dict[str, PossibleFunc],
    call_depth: int,
) -> ExecuteGenReturnType:
    """Handles the lazy evaluation of the ChoosePrimitive."""
    resolved_condition = yield from _execute_gen(
        current_func, input_positions[0], function_mapping, call_depth + 1
    )
    chosen_pos = choose_op(resolved_condition, input_positions[1], input_positions[2])
    ret_val = yield from _execute_gen(
        current_func, chosen_pos, function_mapping, call_depth + 1
    )
    return ret_val


def _resolve_all_inputs_gen(
    current_func: FunctionFrame,
    input_positions: List[GeneralizedPosition],
    function_mapping: Dict[str, PossibleFunc],
    call_depth: int,
) -> Generator[YieldData, None, List[LangType]]:
    """Recursively executes all inputs and returns the resulting constants."""
    ret_val: List[LangType] = []
    for input_pos in input_positions:
        item_val = yield from _execute_gen(
            current_func, input_pos, function_mapping, call_depth + 1
        )
        ret_val.append(item_val)

    return ret_val


def _handle_operation_gen(
    current_func: FunctionFrame,
    operation: Operation,
    input_positions: List[GeneralizedPosition],
    function_mapping: Dict[str, PossibleFunc],
    call_depth: int,
) -> ExecuteGenReturnType:
    """Resolves all inputs and applies the operation to them."""
    resolved_inputs = yield from _resolve_all_inputs_gen(
        current_func, input_positions, function_mapping, call_depth
    )
    return operation(*resolved_inputs)


def _handle_user_function_gen(
    current_func: FunctionFrame,
    user_function: Function,
    input_positions: List[GeneralizedPosition],
    function_mapping: Dict[str, PossibleFunc],
    call_depth: int,
) -> ExecuteGenReturnType:
    """Resolves all inputs and executes a user-defined function in a new frame."""
    resolved_inputs = yield from _resolve_all_inputs_gen(
        current_func, input_positions, function_mapping, call_depth
    )
    new_frame = FunctionFrame(user_function, resolved_inputs)
    ret_val = yield from _execute_gen(
        new_frame, ENTRY_POINT, function_mapping, call_depth + 1
    )
    return ret_val


def _execute_gen(
    current_func: FunctionFrame,
    pos: GeneralizedPosition,
    function_mapping: Dict[str, PossibleFunc],
    call_depth: int,
) -> ExecuteGenReturnType:
    yield YieldData(
        YieldType.FUNCTION_ENTRY, call_depth, str(current_func.function_reference)
    )

    symbol_or_const_on_pos, pos = current_func.get_symbol_for_pos(pos)

    if isinstance(symbol_or_const_on_pos, str):
        function_on_pos = function_mapping[symbol_or_const_on_pos]
    else:
        function_on_pos = symbol_or_const_on_pos

    if isinstance(function_on_pos, LangType):
        yield YieldData(YieldType.RETURN, call_depth, str(function_on_pos))
        return function_on_pos

    input_positions = current_func.function_reference.input_mapping[pos]

    if isinstance(function_on_pos, ChoosePrimitive):
        yield YieldData(YieldType.FUNCTION_CALL, call_depth, str(function_on_pos))
        choose_val = yield from _handle_choose_gen(
            current_func,
            function_on_pos,
            input_positions,
            function_mapping,
            call_depth,
        )
        yield YieldData(
            YieldType.GOT_BACK_FROM_FUNCTION_CALL,
            call_depth,
            str(function_on_pos),
        )
        yield YieldData(YieldType.RETURN, call_depth, str(choose_val))
        return choose_val
    elif isinstance(function_on_pos, Operation):
        yield YieldData(YieldType.FUNCTION_CALL, call_depth, str(function_on_pos))
        op_val = yield from _handle_operation_gen(
            current_func,
            function_on_pos,
            input_positions,
            function_mapping,
            call_depth,
        )
        yield YieldData(
            YieldType.GOT_BACK_FROM_FUNCTION_CALL,
            call_depth,
            str(function_on_pos),
        )
        yield YieldData(YieldType.RETURN, call_depth, str(op_val))
        return op_val
    elif isinstance(function_on_pos, Function):
        yield YieldData(YieldType.FUNCTION_CALL, call_depth, str(function_on_pos))
        func_val = yield from _handle_user_function_gen(
            current_func,
            function_on_pos,
            input_positions,
            function_mapping,
            call_depth,
        )
        yield YieldData(
            YieldType.GOT_BACK_FROM_FUNCTION_CALL,
            call_depth,
            str(function_on_pos),
        )
        yield YieldData(YieldType.RETURN, call_depth, str(func_val))
        return func_val
    else:
        raise TypeError(f"Unexpected type at position {pos}: {type(function_on_pos)}")


def execute_entry(
    current_func: Function,
    function_mapping: Dict[str, PossibleFunc],
    args: List[LangType],
) -> LangType:
    func_frame: FunctionFrame = FunctionFrame(current_func, args)
    gen_obj: ExecuteGenReturnType = _execute_gen(
        func_frame, ENTRY_POINT, function_mapping, 0
    )
    while True:
        try:
            trace = next(gen_obj)
            print(trace)
        except StopIteration as e:
            print(f"\nFinal Result: {e.value}")
            return e.value


def main():
    print("Hello from toy-functional-language!")

    print("exit from toy-functional-language")


if __name__ == "__main__":
    main()
