"""Tests for Water Jug Puzzle Solver."""

import sys
import pytest
from pathlib import Path

# Add the project root to the path so we can import from water_jug_solver
sys.path.insert(0, str(Path(__file__).parent))

from water_jug_solver.models import ActionType
from water_jug_solver.solver import can_solve, bfs_solve
from water_jug_solver.formatter import format_action, format_solution, format_no_solution, simulate_solution


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


class TestFormatter:
    """Tests for formatter module functions."""

    def test_format_action_fill(self):
        """Test format_action for FILL action type."""
        capacities = [3, 5]
        action = (ActionType.FILL, 0)
        result = format_action(action, capacities)
        assert result == "Riempire vaso 0 (capacità: 3)"
        action = (ActionType.FILL, 1)
        result = format_action(action, capacities)
        assert result == "Riempire vaso 1 (capacità: 5)"

    def test_format_action_empty(self):
        """Test format_action for EMPTY action type."""
        capacities = [3, 5]
        action = (ActionType.EMPTY, 0)
        result = format_action(action, capacities)
        assert result == "Svuotare vaso 0"
        action = (ActionType.EMPTY, 1)
        result = format_action(action, capacities)
        assert result == "Svuotare vaso 1"

    def test_format_action_pour(self):
        """Test format_action for POUR action type."""
        capacities = [3, 5]
        action = (ActionType.POUR, 1, 0)
        result = format_action(action, capacities)
        assert result == "Travasare vaso 1 → vaso 0"
        action = (ActionType.POUR, 0, 1)
        result = format_action(action, capacities)
        assert result == "Travasare vaso 0 → vaso 1"

    def test_format_solution(self):
        """Test format_solution returns correct structured and readable outputs."""
        capacities = [3, 5]
        actions = [(ActionType.FILL, 0), (ActionType.EMPTY, 0)]
        structured, readable = format_solution(actions, capacities)
        assert structured == actions
        assert readable[0] == "Riempire vaso 0 (capacità: 3)"
        assert readable[1] == "Svuotare vaso 0"
        assert len(structured) == len(readable) == 2

    def test_format_no_solution(self):
        """Test format_no_solution returns proper error message."""
        result = format_no_solution(4)
        assert result == "Errore: nessuna soluzione esiste per raggiungere il target 4."
        result = format_no_solution(10)
        assert result == "Errore: nessuna soluzione esiste per raggiungere il target 10."

    def test_simulate_solution_known_case(self):
        """Test simulate_solution returns correct state sequence for [3,5] target 4."""
        capacities = [3, 5]
        target = 4
        solution = bfs_solve(capacities, target)
        assert solution is not None
        expected_states = [
            (0, 0),
            (0, 5),
            (3, 2),
            (0, 2),
            (2, 0),
            (2, 5),
            (3, 4)
        ]
        actual_states = simulate_solution(solution, capacities)
        assert actual_states == expected_states
        assert target in actual_states[-1]


class TestRunGUI:
    """Tests for run_gui.py launcher."""

    def test_run_gui_exists_and_valid_syntax(self):
        """Test run_gui.py exists and has valid Python syntax."""
        gui_path = Path(__file__).parent / "run_gui.py"
        # Check existence
        assert gui_path.exists(), f"run_gui.py not found at {gui_path}"
        # Check syntax validity
        import py_compile
        try:
            py_compile.compile(str(gui_path), doraise=True)
        except py_compile.PyCompileError as e:
            pytest.fail(f"run_gui.py has invalid syntax: {e}")

    def test_app_path_constructed_with_pathlib(self):
        """Test app_path is correctly built using pathlib.Path."""
        gui_path = Path(__file__).parent / "run_gui.py"
        content = gui_path.read_text()
        # Check pathlib is imported
        assert "from pathlib import Path" in content, "pathlib.Path not imported in run_gui.py"
        # Check app_path assignment uses Path(__file__).parent / "app.py"
        assert 'app_path = Path(__file__).parent / "app.py"' in content, "app_path not constructed correctly with pathlib"
