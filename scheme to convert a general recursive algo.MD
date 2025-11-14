This conversion scheme utilizes the `yield from` construct to seamlessly manage the recursion, allowing the generator to pause and resume across multiple stack depths while tracing every step.

This scheme requires the use of a **Wrapper Generator** and a **Recursive Helper Function**.

---

## Scheme for Converting Recursive Algorithms to Tracing Generators

### Prerequisites

1.  **The Runner Function:** You must use a runner that manually calls `next()` and catches the `StopIteration` exception to retrieve the final returned value (as discussed in the previous answer).
2.  **State Tracking:** A tracking variable, typically `depth`, must be added to manage indentation and visualization of the call stack.

### Conversion Steps

We will convert an arbitrary recursive function $R(args)$ into a generator wrapper $G(args)$ that calls a recursive helper $H(args, depth)$.

#### Step 1: Define the Outer Generator Wrapper $G(args)$

The purpose of the wrapper is to initiate the recursion at depth 0 and capture the final return value from the helper function, which then becomes the return value of the entire generator.

| Original Code (Implicit) | Generator Wrapper $G(args)$ |
| :--- | :--- |
| `R(args)` | `def G(args):` |
| | `final_result = yield from H(args, depth=0)` |
| | `return final_result` |

---

#### Step 2: Define the Recursive Helper Function $H(args, depth)$

This function contains the core logic of the original algorithm, modified to yield trace information at key moments.

| Action Point | Original Recursive Function $R$ | Recursive Helper Generator $H$ |
| :--- | :--- | :--- |
| **A. Function Entry** | (Implicit start) | 1. `indent = "  " * depth` |
| | | 2. `yield (f"{indent}-> Calling R({args})", depth)` |
| **B. Base Case** | `if condition: return base_result` | 1. `if condition:` |
| | | 2. `yield (f"{indent}   Base case, returning {base_result}", depth)` |
| | | 3. `return base_result` |
| **C. Recursive Call** | `sub_result = R(new_args)` | 1. `sub_result = yield from H(new_args, depth + 1)` |
| **D. Resumption Trace** | (Implicit resume) | 1. `yield (f"{indent}<- Resumed R({args}). Got {sub_result}", depth)` |
| **E. Final Calculation** | `final_result = calculate(sub_results)` | 1. `final_result = calculate(sub_results)` |
| **F. Function Exit** | `return final_result` | 1. `yield (f"{indent}<- Returning {final_result}", depth)` |
| | | 2. `return final_result` |

---

## Example: Converting Factorial (Single Recursion)

To demonstrate generality, let's apply the scheme to the Factorial function:

$$
\text{fact}(n) = \begin{cases} 1 & \text{if } n=0 \\ n \times \text{fact}(n-1) & \text{if } n>0 \end{cases}
$$

### 1. Original Recursive Function

```python
def factorial(n):
    if n == 0:
        return 1
    return n * factorial(n - 1)
```

### 2. Converted Recursive Generator

We define the Wrapper `fact_gen` and the Helper `_fact_helper`.

```python
from typing import Iterator, Tuple

# Type hint for what we yield (trace) and return (result)
FactGenerator = Iterator[Tuple[str, int]]

def fact_gen(n: int) -> FactGenerator:
  # STEP 1: Wrapper to initiate recursion and capture final result
  final_result = yield from _fact_helper(n, 0)
  return final_result

def _fact_helper(n: int, depth: int):
  # STEP 2 & A: Define helper and trace entry
  indent = "  " * depth
  yield (f"{indent}-> Calling fact({n})", depth)

  # STEP B: Base Case
  if n == 0:
    base_result = 1
    yield (f"{indent}   Base case, returning {base_result}", depth)
    return base_result

  # STEP C: Recursive Call (Conversion of sub_result = R(n-1))
  # sub_result is the value returned by the yield from H(...) expression
  sub_result = yield from _fact_helper(n - 1, depth + 1)

  # STEP D: Resumption Trace
  yield (f"{indent}<- Resumed fact({n}). Got {sub_result} from fact({n-1}) call.", depth)
  
  # STEP E: Final Calculation
  final_result = n * sub_result

  # STEP F: Function Exit Trace and Return
  yield (f"{indent}<- Returning {final_result} for fact({n})", depth)
  return final_result

# --- Runner (for demonstration) ---
def run_trace(gen_obj):
    while True:
        try:
            trace, _ = next(gen_obj)
            print(trace)
        except StopIteration as e:
            print(f"\nFinal Result: {e.value}")
            return

# --- Execution ---
print("--- Trace for Factorial(3) ---")
run_trace(fact_gen(3))
```

### Execution Output (Verification)

The output shows the step-by-step execution following the conversion scheme:

```
--- Trace for Factorial(3) ---
-> Calling fact(3)
  -> Calling fact(2)
    -> Calling fact(1)
      -> Calling fact(0)
         Base case, returning 1
      <- Resumed fact(1). Got 1 from fact(0) call.
      <- Returning 1 for fact(1)
    <- Resumed fact(2). Got 1 from fact(1) call.
    <- Returning 2 for fact(2)
  <- Resumed fact(3). Got 2 from fact(2) call.
  <- Returning 6 for fact(3)

Final Result: 6
```