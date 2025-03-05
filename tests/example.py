#/ This is a module level documentation comment.
#/ It demonstrates how to use the #/ comments for documentation.
#/ These comments will be collected and used as module documentation.

import math
from typing import List, Optional


#/ A simple calculator class that provides basic mathematical operations.
#/ This class demonstrates how class-level documentation works.
class Calculator:
    #/ Initialize the calculator with an optional initial value.
    def __init__(self, initial_value: float = 0):
        self.value = initial_value
    
    #/ Add a number to the current value.
    #/ 
    #/ Parameters:
    #/ - number: The number to add
    #/ 
    #/ Returns:
    #/ - The new value after addition
    def add(self, number: float) -> float:
        self.value += number
        return self.value
    
    #/ Subtract a number from the current value.
    def subtract(self, number: float) -> float:
        self.value -= number
        return self.value


#/ Calculate the average of a list of numbers.
#/ 
#/ This function demonstrates standalone function documentation.
#/ 
#/ Parameters:
#/ - numbers: A list of numbers to average
#/ 
#/ Returns:
#/ - The average value, or None if the list is empty
def average(numbers: List[float]) -> Optional[float]:
    if not numbers:
        return None
    return sum(numbers) / len(numbers)


#/ Calculate the factorial of a non-negative integer.
#/ 
#/ Raises:
#/ - ValueError: If n is negative
def factorial(n: int) -> int:
    if n < 0:
        raise ValueError("Factorial is not defined for negative numbers")
    if n <= 1:
        return 1
    return n * factorial(n - 1)


# This is a regular Python comment and will NOT be included in the documentation
def undocumented_function():
    """This is a regular docstring, not a #/ comment, so it won't be processed by docu."""
    pass