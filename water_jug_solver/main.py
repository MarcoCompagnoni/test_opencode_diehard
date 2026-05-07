"""CLI entry point for Water Jug Puzzle Solver.

Parses command line input and displays the solution.
"""

from typing import Optional
import sys

from water_jug_solver.solver import bfs_solve, can_solve
from water_jug_solver.formatter import format_solution, format_no_solution, simulate_solution


def main() -> None:
    """Run the CLI solver with hardcoded or user-provided input."""
    # Default example: Die Hard water jug problem
    capacities = [3, 5]
    target = 4
    
    print("=" * 50)
    print("Water Jug Puzzle Solver (CLI)")
    print("=" * 50)
    print(f"Capacità vasi: {capacities}")
    print(f"Target: {target}")
    print()
    
    # Check if solvable
    if not can_solve(capacities, target):
        print(format_no_solution(target))
        sys.exit(1)
    
    # Solve
    solution = bfs_solve(capacities, target)
    
    if solution is None:
        print(format_no_solution(target))
        sys.exit(1)
    
    # Format and display
    structured, readable = format_solution(solution, capacities)
    states = simulate_solution(solution, capacities)
    
    print(f"Soluzione trovata in {len(solution)} passi:")
    print("-" * 50)
    
    for i, (action, description) in enumerate(zip(structured, readable), 1):
        state_before = states[i - 1]
        state_after = states[i]
        print(f"{i}. {description}")
        print(f"   Stato: {state_before} → {state_after}")
    
    print("-" * 50)
    print(f"Stato finale: {states[-1]}")
    print("=" * 50)


if __name__ == "__main__":
    main()
