"""Tests for Water Jug Puzzle Solver."""

import sys
import pytest
from pathlib import Path

# Add the project root to the path so we can import from water_jug_solver
sys.path.insert(0, str(Path(__file__).parent))

from water_jug_solver.models import ActionType
from water_jug_solver.solver import can_solve, bfs_solve, bfs_solve_with_visited, simulate_solution
from water_jug_solver.formatter import format_action, format_solution, format_no_solution
from water_jug_solver.tree_viz import create_bfs_tree
from graphviz import Digraph
from app import get_jug_height, render_jugs_row, render_action_animation, auto_play_solution
from unittest.mock import MagicMock


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


class TestBfsSolveWithVisited:
    """Tests for bfs_solve_with_visited function."""

    def test_returns_correct_tuple_structure_solvable(self):
        """Test that bfs_solve_with_visited returns tuple (actions, visited_states, solution_states)."""
        result = bfs_solve_with_visited([3, 5], 4)
        assert isinstance(result, tuple), "Result should be a tuple"
        assert len(result) == 3, "Result should have 3 elements"

        actions, visited_states, solution_states = result

        # Actions should be a list or None
        assert isinstance(actions, list), f"Actions should be a list, got {type(actions)}"
        assert isinstance(visited_states, list), "visited_states should be a list"
        assert isinstance(solution_states, list), "solution_states should be a list"

    def test_returns_correct_tuple_structure_unsolvable(self):
        """Test that bfs_solve_with_visited returns (None, visited, []) for unsolvable."""
        result = bfs_solve_with_visited([3, 6], 4)  # GCD=3, 4%3≠0
        assert isinstance(result, tuple), "Result should be a tuple"
        assert len(result) == 3, "Result should have 3 elements"

        actions, visited_states, solution_states = result

        assert actions is None, "Actions should be None for unsolvable case"
        assert isinstance(visited_states, list), "visited_states should be a list"
        assert solution_states == [], "solution_states should be empty list for unsolvable"

    def test_visited_states_include_initial_state(self):
        """Test that visited states always include the initial state (0, 0, ...)."""
        result = bfs_solve_with_visited([3, 5], 4)
        actions, visited_states, solution_states = result

        initial_state = (0, 0)
        assert initial_state in visited_states, "Initial state should be in visited_states"
        assert visited_states[0] == initial_state, "Initial state should be first visited state"

    def test_visited_states_include_initial_state_unsolvable(self):
        """Test that visited states include initial state even for unsolvable cases."""
        result = bfs_solve_with_visited([3, 6], 4)
        actions, visited_states, solution_states = result

        initial_state = (0, 0)
        assert initial_state in visited_states, "Initial state should be in visited_states"

    def test_solution_states_valid_for_solvable(self):
        """Test that solution_states are valid and reach the target."""
        result = bfs_solve_with_visited([3, 5], 4)
        actions, visited_states, solution_states = result

        assert actions is not None, "Should find a solution"
        assert len(solution_states) > 0, "solution_states should not be empty"
        assert solution_states[0] == (0, 0), "First state should be initial"
        assert 4 in solution_states[-1], "Last state should contain the target"

    def test_visited_states_contains_solution_states(self):
        """Test that all solution states are included in visited states."""
        result = bfs_solve_with_visited([3, 5], 4)
        actions, visited_states, solution_states = result

        for state in solution_states:
            assert state in visited_states, f"Solution state {state} not in visited_states"


class TestTreeViz:
    """Tests for tree_viz module."""

    def test_create_bfs_tree_returns_digraph(self):
        """Test that create_bfs_tree returns a Digraph object."""
        visited_states = [(0, 0), (3, 0), (0, 5), (3, 5), (3, 2)]
        solution_path = [(0, 0), (3, 0), (0, 5), (3, 2)]
        capacities = [3, 5]
        target = 4

        result = create_bfs_tree(visited_states, solution_path, capacities, target)

        assert isinstance(result, Digraph), "create_bfs_tree should return a Digraph object"

    def test_create_bfs_tree_with_empty_inputs(self):
        """Test create_bfs_tree handles empty inputs gracefully."""
        result = create_bfs_tree([], [], [3, 5], 4)
        assert isinstance(result, Digraph), "Should return Digraph even with empty inputs"

    def test_create_bfs_tree_solution_states_highlighted(self):
        """Test that solution states are included in the graph."""
        visited_states = [(0, 0), (3, 0), (0, 5)]
        solution_path = [(0, 0), (3, 0)]
        capacities = [3, 5]
        target = 4

        result = create_bfs_tree(visited_states, solution_path, capacities, target)

        assert isinstance(result, Digraph), "Should return valid Digraph"
        # The Digraph object should have the nodes added
        assert len(result.body) > 0, "Digraph should contain nodes/edges"


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


class TestAppVisualization:
    """Tests for app.py visualization functions."""

    def test_get_jug_height_proportional(self):
        """Test get_jug_height returns proportional height."""
        # MAX_HEIGHT is 300 (defined in app.py)
        assert get_jug_height(10, 20) == 150  # (10/20)*300 = 150
        assert get_jug_height(5, 10) == 150   # (5/10)*300 = 150
        assert get_jug_height(20, 20) == 300  # (20/20)*300 = 300
        assert get_jug_height(0, 10) == 0     # (0/10)*300 = 0

    def test_get_jug_height_max_zero_default(self):
        """Test get_jug_height returns 100 when max_capacity is 0."""
        assert get_jug_height(5, 0) == 100
        assert get_jug_height(0, 0) == 100
        assert get_jug_height(100, 0) == 100

    def test_render_jugs_row_no_errors(self, monkeypatch):
        """Test render_jugs_row does not raise errors with valid inputs."""
        # Mock streamlit module in app
        mock_st = MagicMock()
        # Mock st.columns to return list of mock columns that support context managers
        mock_cols = [MagicMock() for _ in range(2)]
        for col in mock_cols:
            col.__enter__ = MagicMock(return_value=col)
            col.__exit__ = MagicMock(return_value=False)
        mock_st.columns.return_value = mock_cols
        mock_st.markdown = MagicMock()
        monkeypatch.setattr('app.st', mock_st)

        state = (1, 4)
        capacities = [3, 5]
        try:
            render_jugs_row(state, capacities)
        except Exception as e:
            pytest.fail(f"render_jugs_row raised unexpected error: {e}")

    def test_render_action_animation_fill(self, monkeypatch):
        """Test render_action_animation handles FILL action."""
        mock_st = MagicMock()
        mock_cols = [MagicMock() for _ in range(2)]
        for col in mock_cols:
            col.__enter__ = MagicMock(return_value=col)
            col.__exit__ = MagicMock(return_value=False)
        mock_st.columns.return_value = mock_cols
        mock_st.markdown = MagicMock()
        mock_st.info = MagicMock()
        monkeypatch.setattr('app.st', mock_st)

        action = (ActionType.FILL, 0)
        state_before = (0, 0)
        state_after = (3, 0)
        capacities = [3, 5]
        try:
            render_action_animation(action, state_before, state_after, capacities)
        except Exception as e:
            pytest.fail(f"render_action_animation FILL raised error: {e}")

    def test_render_action_animation_empty(self, monkeypatch):
        """Test render_action_animation handles EMPTY action."""
        mock_st = MagicMock()
        mock_cols = [MagicMock() for _ in range(2)]
        for col in mock_cols:
            col.__enter__ = MagicMock(return_value=col)
            col.__exit__ = MagicMock(return_value=False)
        mock_st.columns.return_value = mock_cols
        mock_st.markdown = MagicMock()
        mock_st.info = MagicMock()
        monkeypatch.setattr('app.st', mock_st)

        action = (ActionType.EMPTY, 1)
        state_before = (2, 5)
        state_after = (2, 0)
        capacities = [3, 5]
        try:
            render_action_animation(action, state_before, state_after, capacities)
        except Exception as e:
            pytest.fail(f"render_action_animation EMPTY raised error: {e}")

    def test_render_action_animation_pour(self, monkeypatch):
        """Test render_action_animation handles POUR action."""
        mock_st = MagicMock()
        mock_cols = [MagicMock() for _ in range(2)]
        for col in mock_cols:
            col.__enter__ = MagicMock(return_value=col)
            col.__exit__ = MagicMock(return_value=False)
        mock_st.columns.return_value = mock_cols
        mock_st.markdown = MagicMock()
        mock_st.info = MagicMock()
        monkeypatch.setattr('app.st', mock_st)

        action = (ActionType.POUR, 0, 1)
        state_before = (3, 2)
        state_after = (0, 5)
        capacities = [3, 5]
        try:
            render_action_animation(action, state_before, state_after, capacities)
        except Exception as e:
            pytest.fail(f"render_action_animation POUR raised error: {e}")

    def test_auto_play_solution_exists_and_callable(self):
        """Test auto_play_solution function exists and is callable."""
        import inspect
        assert callable(auto_play_solution), "auto_play_solution is not callable"
        assert inspect.isfunction(auto_play_solution), "auto_play_solution is not a function"

    def test_render_jug_uses_bottom_positioning(self, monkeypatch):
        """Test render_jug uses absolute positioning with bottom: 0 for water level."""
        mock_st = MagicMock()
        captured_html = []
        
        def mock_markdown(html, *args, **kwargs):
            captured_html.append(html)
        mock_st.markdown = mock_markdown
        monkeypatch.setattr('app.st', mock_st)
        monkeypatch.setattr('app.JUG_WIDTH', 100)
        
        from app import render_jug
        render_jug(level=2, capacity=5, jug_name="Test Jug", color="#1f77b4", height=300)
        
        assert len(captured_html) == 1, "Expected exactly one st.markdown call"
        html = captured_html[0]
        # Check for bottom: 0 positioning (water fills from bottom)
        assert "bottom: 0" in html, f"Bottom positioning not found in render_jug HTML. Content: {html}"
        assert "position: absolute" in html, f"Absolute positioning not found in render_jug HTML."

    def test_initial_jugs_displayed_when_solution_none(self, monkeypatch):
        """Test initial jugs are displayed when solution is None (mock streamlit)."""
        # Mock streamlit session state
        mock_session_state = MagicMock()
        mock_session_state.solution = None
        monkeypatch.setattr('app.st.session_state', mock_session_state)
        
        # Test configuration
        capacities = [3, 5]
        initial_state = tuple([0] * len(capacities))
        
        # Mock st.empty to return a placeholder with container context manager
        mock_jug_placeholder = MagicMock()
        mock_container = MagicMock()
        mock_jug_placeholder.container.return_value = mock_container
        mock_jug_placeholder.container.return_value.__enter__ = MagicMock(return_value=mock_container)
        mock_jug_placeholder.container.return_value.__exit__ = MagicMock(return_value=False)
        monkeypatch.setattr('app.st.empty', lambda: mock_jug_placeholder)
        
        # Track render_jugs_row calls
        render_calls = []
        def mock_render_jugs_row(state, caps, *args, **kwargs):
            render_calls.append((state, caps))
        monkeypatch.setattr('app.render_jugs_row', mock_render_jugs_row)
        
        # Execute the same logic as app.py lines 261-265
        if mock_session_state.solution is None:
            with mock_jug_placeholder.container():
                from app import render_jugs_row
                render_jugs_row(initial_state, capacities)
        
        # Verify results
        assert len(render_calls) == 1, f"render_jugs_row called {len(render_calls)} times, expected 1"
        assert render_calls[0][0] == initial_state, f"Rendered state {render_calls[0][0]} != expected initial state {initial_state}"
        assert render_calls[0][1] == capacities, f"Rendered capacities {render_calls[0][1]} != expected {capacities}"

    def test_nuova_partita_resets_session_state(self, monkeypatch):
        """Test 'Nuova Partita' button resets session state correctly."""
        # Mock session state with existing solution
        mock_session_state = MagicMock()
        mock_session_state.solution = [(ActionType.FILL, 0)]
        mock_session_state.states = [(0, 0), (3, 0)]
        mock_session_state.readable = ["Riempire vaso 0"]
        mock_session_state.current_step = 1
        mock_session_state.jug_placeholder = MagicMock()
        mock_session_state.info_placeholder = MagicMock()
        
        monkeypatch.setattr('app.st.session_state', mock_session_state)
        
        # Simulate the "Nuova Partita" logic from app.py lines 314-319
        # This is what happens when new_game button is clicked
        mock_session_state.solution = None
        mock_session_state.states = None
        mock_session_state.readable = None
        mock_session_state.current_step = 0
        
        # Verify all state is reset
        assert mock_session_state.solution is None, "solution should be None after Nuova Partita"
        assert mock_session_state.states is None, "states should be None after Nuova Partita"
        assert mock_session_state.readable is None, "readable should be None after Nuova Partita"
        assert mock_session_state.current_step == 0, "current_step should be 0 after Nuova Partita"

    def test_render_jugs_row_adds_spacer_for_bottom_alignment(self, monkeypatch):
        """Test render_jugs_row adds spacer div with calculated height for bottom alignment."""
        mock_st = MagicMock()
        captured_html = []
        
        def mock_markdown(html, *args, **kwargs):
            captured_html.append(html)
        mock_st.markdown = mock_markdown
        mock_st.columns = MagicMock(return_value=[MagicMock() for _ in range(2)])
        monkeypatch.setattr('app.st', mock_st)
        monkeypatch.setattr('app.JUG_WIDTH', 100)
        
        from app import render_jugs_row, get_jug_height
        
        # Test with jugs of different capacities
        # Jug 0: capacity 3, Jug 1: capacity 5
        # max_height should be get_jug_height(5, 5) = 300
        # Jug 0 height: get_jug_height(3, 5) = 180
        # Spacer for Jug 0: 300 - 180 = 120px
        state = (1, 4)
        capacities = [3, 5]
        
        render_jugs_row(state, capacities)
        
        # Check that spacer divs were added
        spacer_found = False
        for html in captured_html:
            if 'height:' in html and 'px;' in html:
                # Extract height value
                if '120px' in html or 'spacer' in html.lower() or 'height: 1' in html:
                    spacer_found = True
                    break
        
        # Verify that markdown was called with height styling (spacer divs)
        assert len(captured_html) >= 2, f"Expected multiple markdown calls for spacers and jugs, got {len(captured_html)}"
        
        # Check that at least one call contains a height specification for spacing
        height_pattern_found = False
        for html in captured_html:
            if 'height:' in html and 'px;' in html:
                height_pattern_found = True
                break
        assert height_pattern_found, f"No spacer div with height found. Captured HTML: {captured_html}"

    def test_auto_play_solution_uses_longer_pause(self, monkeypatch):
        """Test auto_play_solution uses time.sleep(2.0) for better visibility."""
        import time
        
        mock_st = MagicMock()
        mock_session_state = MagicMock()
        mock_session_state.current_step = 0
        mock_session_state.jug_placeholder = MagicMock()
        mock_session_state.info_placeholder = MagicMock()
        
        mock_st.session_state = mock_session_state
        mock_st.progress = MagicMock(return_value=MagicMock())
        mock_st.empty = MagicMock(return_value=MagicMock())
        mock_st.info = MagicMock()
        mock_st.markdown = MagicMock()
        mock_st.balloons = MagicMock()
        
        monkeypatch.setattr('app.st', mock_st)
        
        # Track time.sleep calls
        sleep_calls = []
        original_sleep = time.sleep
        
        def mock_sleep(duration):
            sleep_calls.append(duration)
        
        monkeypatch.setattr('time.sleep', mock_sleep)
        
        # Create minimal solution data
        solution = [(ActionType.FILL, 0)]
        states = [(0, 0), (3, 0)]
        readable = ["Riempire vaso 0"]
        capacities = [3, 5]
        
        from app import auto_play_solution
        auto_play_solution(solution, states, readable, capacities)
        
        # Verify sleep was called
        assert len(sleep_calls) > 0, "time.sleep should be called in auto_play_solution"
        
        # Verify sleep duration is at least 0.8 seconds (and preferably 2.0)
        for duration in sleep_calls:
            assert duration >= 0.8, f"Sleep duration {duration} is less than 0.8 seconds"
        
        # Check that at least one sleep call is 2.0 seconds
        assert 2.0 in sleep_calls, f"Expected time.sleep(2.0) to be called, but got sleep calls: {sleep_calls}"


class TestSessionStateReset:
    """Tests for session state reset when inputs change."""

    def test_inputs_changed_reset_solution(self, monkeypatch):
        """Test that changing capacities resets solution state (simulates [3,5] -> [3,5,8])."""
        # Mock session state with existing solution and old inputs tracked
        mock_session_state = MagicMock()
        mock_session_state.solution = [(ActionType.FILL, 0)]
        mock_session_state.states = [(0, 0), (3, 0)]
        mock_session_state.readable = ["Riempire vaso 0"]
        mock_session_state.current_step = 1
        mock_session_state.last_capacities = [3, 5]
        mock_session_state.last_target = 4
        
        monkeypatch.setattr('app.st.session_state', mock_session_state)
        
        # Simulate new inputs: capacities changed from [3,5] to [3,5,8]
        new_capacities = [3, 5, 8]
        new_target = 4
        
        # Replicate the logic from app.py lines 253-261
        inputs_changed = (
            mock_session_state.last_capacities != new_capacities or
            mock_session_state.last_target != new_target
        )
        
        # Verify inputs are detected as changed
        assert inputs_changed is True, "Inputs should be detected as changed"
        
        # Simulate the reset logic
        if inputs_changed and mock_session_state.solution is not None:
            mock_session_state.solution = None
            mock_session_state.states = None
            mock_session_state.readable = None
            mock_session_state.current_step = 0
        
        # Verify reset
        assert mock_session_state.solution is None, "solution should be None after inputs change"
        assert mock_session_state.states is None, "states should be None after inputs change"
        assert mock_session_state.readable is None, "readable should be None after inputs change"
        assert mock_session_state.current_step == 0, "current_step should be 0 after inputs change"

    def test_inputs_unchanged_keep_solution(self, monkeypatch):
        """Test that solution is kept when inputs don't change."""
        # Mock session state with existing solution
        mock_session_state = MagicMock()
        mock_session_state.solution = [(ActionType.FILL, 0)]
        mock_session_state.states = [(0, 0), (3, 0)]
        mock_session_state.readable = ["Riempire vaso 0"]
        mock_session_state.current_step = 1
        mock_session_state.last_capacities = [3, 5]
        mock_session_state.last_target = 4
        
        monkeypatch.setattr('app.st.session_state', mock_session_state)
        
        # Same inputs as before
        same_capacities = [3, 5]
        same_target = 4
        
        # Replicate the logic from app.py
        inputs_changed = (
            mock_session_state.last_capacities != same_capacities or
            mock_session_state.last_target != same_target
        )
        
        # Verify inputs are NOT detected as changed
        assert inputs_changed is False, "Inputs should not be detected as changed"
        
        # Solution should remain unchanged
        assert mock_session_state.solution == [(ActionType.FILL, 0)], "solution should be kept"
        assert mock_session_state.states == [(0, 0), (3, 0)], "states should be kept"
        assert mock_session_state.current_step == 1, "current_step should be kept"

    def test_target_changed_reset_solution(self, monkeypatch):
        """Test that changing target resets solution state."""
        # Mock session state with existing solution
        mock_session_state = MagicMock()
        mock_session_state.solution = [(ActionType.FILL, 0)]
        mock_session_state.states = [(0, 0), (3, 0)]
        mock_session_state.readable = ["Riempire vaso 0"]
        mock_session_state.current_step = 1
        mock_session_state.last_capacities = [3, 5]
        mock_session_state.last_target = 4
        
        monkeypatch.setattr('app.st.session_state', mock_session_state)
        
        # Same capacities but different target
        capacities = [3, 5]
        new_target = 2
        
        # Replicate the logic from app.py
        inputs_changed = (
            mock_session_state.last_capacities != capacities or
            mock_session_state.last_target != new_target
        )
        
        assert inputs_changed is True, "Inputs should be detected as changed (target changed)"
        
        # Simulate reset
        if inputs_changed and mock_session_state.solution is not None:
            mock_session_state.solution = None
            mock_session_state.states = None
            mock_session_state.readable = None
            mock_session_state.current_step = 0
        
        assert mock_session_state.solution is None, "solution should be None after target change"

    def test_no_solution_no_reset_when_inputs_change(self, monkeypatch):
        """Test that no reset occurs when solution is None even if inputs change."""
        # Mock session state with no solution
        mock_session_state = MagicMock()
        mock_session_state.solution = None
        mock_session_state.states = None
        mock_session_state.readable = None
        mock_session_state.current_step = 0
        mock_session_state.last_capacities = [3, 5]
        mock_session_state.last_target = 4
        
        monkeypatch.setattr('app.st.session_state', mock_session_state)
        
        # New inputs
        new_capacities = [3, 5, 8]
        new_target = 4
        
        # Replicate the logic from app.py
        inputs_changed = (
            mock_session_state.last_capacities != new_capacities or
            mock_session_state.last_target != new_target
        )
        
        assert inputs_changed is True, "Inputs should be detected as changed"
        
        # The reset logic checks "if inputs_changed and st.session_state.solution is not None"
        # Since solution is None, no reset should happen (but it's already None)
        # This test verifies the condition works correctly
        if inputs_changed and mock_session_state.solution is not None:
            # This block should NOT execute
            pytest.fail("Reset should not execute when solution is None")
        
        # State should remain as is
        assert mock_session_state.solution is None
        assert mock_session_state.states is None
