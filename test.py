from main import (
    LangType,
    Lang_choice_comparison,
    Lang_compare,
    Lang_plus,
    Lang_minus,
    Lang_nesting,
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


if __name__ == "__main__":
    test_1()
    test_2()
