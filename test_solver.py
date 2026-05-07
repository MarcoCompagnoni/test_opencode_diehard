"""Tests for Water Jug Puzzle Solver."""

import sys
from pathlib import Path

# Add the project root to the path so we can import from water_jug_solver
sys.path.insert(0, str(Path(__file__).parent))

from water_jug_solver.models import ActionType
from water_jug_solver.solver import can_solve, bfs_solve


class TestCanSolve:
    """Tests for can_solve pre-check function."""

    def test_impossible_case_gcd(self):
        """Impossible case: capacities [3,6], target 4 → False (GCD=3, 4%3≠0)"""
        assert can_solve([3, 6], 4) is False

    def test_possible_case(self):
        """Possible case: capacities [3,5], target 4 → True"""
        assert can_solve([3, 5], 4) is True

    def test_target_exceeds_max_capacity(self):
        """Target > max capacity: capacities [3,5], target 6 → False"""
        assert can_solve([3, 5], 6) is False

    def test_target_zero(self):
        """Target 0 is always solvable (empty jugs initially)"""
        assert can_solve([3, 5], 0) is True
        assert can_solve([3, 6], 0) is True

    def test_single_jug_exact(self):
        """Single jug with target equal to capacity"""
        assert can_solve([5], 5) is True

    def test_empty_capacities(self):
        """Empty capacities list"""
        assert can_solve([], 0) is False
        assert can_solve([], 5) is False


class TestBfsSolve:
    """Tests for bfs_solve function."""

    def test_die_hard_classic(self):
        """Classic Die Hard case: [3,5], target 4 → valid action path"""
        result = bfs_solve([3, 5], 4)
        assert result is not None
        assert len(result) > 0
        # Verify path leads to target by simulating
        state = (0, 0)
        capacities = (3, 5)
        for action in result:
            if action[0] == ActionType.FILL:
                jug = action[1]
                state = list(state)
                state[jug] = capacities[jug]
                state = tuple(state)
            elif action[0] == ActionType.EMPTY:
                jug = action[1]
                state = list(state)
                state[jug] = 0
                state = tuple(state)
            elif action[0] == ActionType.POUR:
                from_jug, to_jug = action[1], action[2]
                transfer = min(state[from_jug], capacities[to_jug] - state[to_jug])
                state = list(state)
                state[from_jug] -= transfer
                state[to_jug] += transfer
                state = tuple(state)
        assert 4 in state

    def test_impossible_case(self):
        """Impossible case: [3,6], target 4 → None"""
        assert bfs_solve([3, 6], 4) is None

    def test_single_jug_exact_capacity(self):
        """Single jug: [5], target 5 → [(ActionType.FILL, 0)]"""
        result = bfs_solve([5], 5)
        assert result == [(ActionType.FILL, 0)]

    def test_target_zero(self):
        """Target 0: initial state already matches → empty list"""
        assert bfs_solve([3, 5], 0) == []
        assert bfs_solve([5], 0) == []

    def test_empty_capacities(self):
        """Edge case: empty capacities → None"""
        assert bfs_solve([], 0) is None
        assert bfs_solve([], 5) is None

    def test_duplicate_capacities(self):
        """Edge case: duplicate capacities [3,3], target 3"""
        result = bfs_solve([3, 3], 3)
        assert result is not None
        assert len(result) > 0

    def test_larger_jugs(self):
        """Test with larger jug capacities"""
        result = bfs_solve([7, 11], 6)
        assert result is not None
        assert len(result) > 0

    def test_verify_solution_validity(self):
        """Verify that returned solution actually reaches target"""
        test_cases = [
            ([3, 5], 4),
            ([5, 8], 3),
            ([7, 11], 6),
        ]
        for capacities, target in test_cases:
            result = bfs_solve(capacities, target)
            if result is not None:
                # Simulate the solution
                state = tuple([0] * len(capacities))
                for action in result:
                    if action[0] == ActionType.FILL:
                        jug = action[1]
                        state = list(state)
                        state[jug] = capacities[jug]
                        state = tuple(state)
                    elif action[0] == ActionType.EMPTY:
                        jug = action[1]
                        state = list(state)
                        state[jug] = 0
                        state = tuple(state)
                    elif action[0] == ActionType.POUR:
                        from_jug, to_jug = action[1], action[2]
                        transfer = min(state[from_jug], capacities[to_jug] - state[to_jug])
                        state = list(state)
                        state[from_jug] -= transfer
                        state[to_jug] += transfer
                        state = tuple(state)
                assert target in state, f"Solution for {capacities}, target {target} failed"
