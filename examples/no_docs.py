from typing import List, Optional, Union

class Calculator:
    def __init__(self, initial_value: float = 0) -> None:
        self.value = initial_value
    
    def add(self, number: float) -> float:
        self.value += number
        return self.value
    
    def subtract(self, number: float) -> float:
        self.value -= number
        return self.value

def calculate_average(numbers: List[float]) -> Optional[float]:
    if not numbers:
        return None
    return sum(numbers) / len(numbers)

def factorial(n: int) -> int:
    if n < 0:
        raise ValueError("Factorial is not defined for negative numbers")
    if n == 0:
        return 1
    return n * factorial(n - 1)