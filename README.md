# Experimentation with a language

Inspired by the minecraft mod **Psi**. Minimal pure functional language. Is supposed to be represented graphically, but for now exists as an (informal) subset of Python.

Most language operations implemented as `Lang_xxx()` functions in `main.py`. The exception to this is `Lang_choice_comparison` - this operation is supposed to have lazy evaluation, and so is supposed to be implemented as an `if` statement calling `Lang_choice_comparison` for evaluation.

`test.py` contains small examples of this code, with `print` statements serving as points of entry to the language.

## Features
- Consists of function declarations. Each function declaration is a square of tiles. Each tile is either a function call, a constant, or a pipe. Each function declaration marks 1 side as an output, and 0-3 sides as inputs.
- Each function is represented both with it's declaration and it's calls. When a function is declared, it is a square of tiles. When a function is called, it is a singular tile (TODO: play around with call size in tiles? EG 3 by 3 calls? Later when implementing graphical view). All functions are in global scope. This implies recursion and cross-recursion.
- Constants are just functions with 0 inputs. "Pipes" are just the identity function, but with the added benefit of being able to be crossed in the graphical view. Pipes are directional.
- Pipes can be split off, but not united. Specifically, this means that 1 output can serve to many different inputs, but each input needs to come from 1 output.
- For each function call, sides of the declaration view can be 1-to-1 arbitrarily mapped to sides of the call view.
- The point of entry is just another function declaration with a special name. (in case of an esolang implementation, inputs of the main function would correspond to command line args. in case of a zachlike, inputs would correspond to test cases of a level specification.)

## Data Types
There are 2 data types: the **integer**, and the **immutable list** (can contain other lists).

## Operations
Every operation looks like a function call.
Fundamental operations: `?choice`, `>=comparison`, `+addition`, `-subtraction`, `~nesting`.

- `choice` function is the only fundamental function with lazy evaluation of arguments B and C. This is necessary for recursion termination.

### Choice table
| A↓?B,C | Behavior |
| :--- | :--- |
| **int** | {nonzero, zero} maps to {B,C} |
| **list** | length of list used for evaluation like for integers |

### Comparison table
| A↓>=B→ | int | list |
| :--- | :--- | :--- |
| **int** | 1 if A>=B, else 0 | always 0, ints are always "smaller" than lists |
| **list** | always 1, lists are "bigger" than ints | 1 if A is the same as B (item by item), 0 otherwise |

### Addition table
| A↓+B→ | int | list |
| :--- | :--- | :--- |
| **int** | sum | list B with A, prepended |
| **list** | list A with B, appended | concatenation |

### Subtraction table
| A↓-B→ | int | list |
| :--- | :--- | :--- |
| **int** | difference A-B | the value of item in list B on idx A (accessor) |
| **list** | copy of A with value at idx B, popped | Remove from A all instances of items encountered in B. (TODO: something else??) |

(when idx for popping and accessing is out of bounds, it is clamped in bounds. For empty list, popping and accessing return another empty list.)

Possible candidates for operation "list - list", inspired by the set difference:
1.  For each element, count the number N of element X in B. In A, remove first N instances of X.
2.  Remove from A all instances of items encountered in B. (current)

### Nesting
Nesting transforms the input into a list, containing this input.

| A | ~A |
| :--- | :--- |
| 0 | (0) |
| (0, 1) | ((0, 1),) |
