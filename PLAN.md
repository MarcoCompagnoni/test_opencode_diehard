# Water Jug Puzzle Solver - Plan

## Changelog / Status

- [x] **2026-05-07** - Core solver implemented: `models.py` and `solver.py` with BFS algorithm, GCD pre-check, and Google-style docstrings
- [x] **2026-05-07** - Tests implemented: `test_solver.py` with comprehensive test coverage for `can_solve` and `bfs_solve`
- [x] **2026-05-07** - GUI launcher added: `run_gui.py` for launching Streamlit GUI directly from PyCharm
- [x] **2026-05-07** - Streamlit GUI implemented: `app.py` with interactive web interface
- [x] **2026-05-07** - CLI entry point implemented: `main.py` with command-line interface
- [x] **2026-05-07** - Output formatter implemented: `formatter.py` for structured and readable output
- [x] **2026-05-07** - Animated visualization added: `app.py` updated with proportional jug scaling, interactive slider for step navigation, and action animation
- [x] **2026-05-07** - UI fixes in `app.py`: removed unnecessary down arrow emojis, aligned jugs to bottom using spacer divs, added Play button for auto-animation, show initial jugs before solving, added "Nuova Partita" button, increased animation pause to 2.0s
- [x] **2026-05-07** - Fixed IndexError in `app.py`: added input tracking (`last_capacities`, `last_target`) in session state, reset solution when inputs change to prevent index mismatch
- [x] **2026-05-07** - BFS tree visualization implemented: `tree_viz.py` with `create_bfs_tree` function (graphviz) - now featuring real parent-child relationships
- [x] **2026-05-07** - Enhanced solver: added `bfs_solve_with_visited` and `simulate_solution` to `solver.py`
- [x] **2026-05-07** - Tree visualization in GUI: `app.py` now displays real BFS tree with 2-color scheme (light red=visited, blue=solution path)
- [x] **2026-05-07** - Performance optimization: added Streamlit caching (`@st.cache_data`) for BFS results
- [x] **2026-05-07** - Robustness fix: resolved `ValueError` in production related to stale cache data by renaming the cached solver function (forced cache invalidation)
- [x] **2026-05-07** - Code optimization for deployment
- [ ] Add BFS generator variant in `solver.py` for real-time step-by-step search visualization (optional)

## Architecture

```
water_jug_solver/
├── models.py           # State, Action, ActionType enum
├── solver.py           # BFS + pre-check GCD, bfs_solve_with_visited, simulate_solution
├── formatter.py        # Output strutturato + leggibile
├── tree_viz.py         # Visualizzazione albero BFS con graphviz (create_bfs_tree)
├── main.py             # CLI entry point
└── app.py              # Streamlit GUI with animated visualization + BFS tree
```

run_gui.py              # Launcher per avviare Streamlit GUI da PyCharm

### Module Responsibilities

| File | Responsabilità |
|------|----------------|
| `models.py` | `JugState` (tupla immutabile dello stato), `ActionType` (enum: FILL, EMPTY, POUR), `Action` definition |
| `solver.py` | BFS, pre-check GCD, gestione visited states, path reconstruction, `bfs_solve_with_visited()` (returns visited+solution), `simulate_solution()` (intermediate states) |
| `formatter.py` | `format_solution()` → restituisce lista azioni + descrizione testuale |
| `tree_viz.py` | `create_bfs_tree()` → Graphviz visualization with real parent-child hierarchy and 2-color scheme (light red=visited, blue=solution) |
| `main.py` | Parsing input CLI (`capacities: list[int]`, `target: int`), esecuzione, print output |
| `app.py` | Streamlit GUI: input, visualizzazione animata, caching `@st.cache_data`, real BFS tree hierarchy (graphviz) |
| `run_gui.py` | Launcher script per avviare app.py da PyCharm con un clic |

## Mathematical Pre-check

Il problema è risolvibile **sse**:

```
GCD(capacities) divide target  AND  target <= max(capacities)
```

**Perché**: L'invariante è che l'acqua totale in ogni stato è multiplo del MCD delle capacità. Inoltre serve almeno un vaso che possa contenere `target`.

```python
def can_solve(capacities: List[int], target: int) -> bool:
    if target > max(capacities):
        return False
    gcd_all = gcd_list(capacities)  # MCD di tutte le capacità
    return target % gcd_all == 0
```

## Pseudocodice

### 1. Rappresentazione dello Stato

```
State = tuple[int]  // es. (0, 5, 3) = vaso0=0, vaso1=5, vaso2=3
Action = (type, i, j)  // type ∈ {FILL, EMPTY, POUR}, j usato solo per POUR
```

### 2. Generazione Azioni (da uno stato)

```
function get_neighbors(state, capacities):
    neighbors = []
    
    for i in range(len(capacities)):
        // FILL: riempi vaso i
        if state[i] < capacities[i]:
            new_state = state.copy()
            new_state[i] = capacities[i]
            neighbors.append((new_state, ("fill", i)))
        
        // EMPTY: svuota vaso i
        if state[i] > 0:
            new_state = state.copy()
            new_state[i] = 0
            neighbors.append((new_state, ("empty", i)))
        
        // POUR: travasa da i a ogni altro vaso j
        for j in range(len(capacities)):
            if i != j and state[i] > 0 and state[j] < capacities[j]:
                transfer = min(state[i], capacities[j] - state[j])
                new_state = state.copy()
                new_state[i] -= transfer
                new_state[j] += transfer
                neighbors.append((new_state, ("pour", i, j)))
    
    return neighbors
```

### 3. Algoritmo BFS (Base)

```
function bfs_solve(capacities, target):
    if not can_solve(capacities, target):
        return None
        
    initial_state = tuple([0] * len(capacities))
    queue = deque([initial_state])
    visited = {initial_state}
    parent = {initial_state: None}        // stato precedente
    action_map = {initial_state: None}    // azione che ha portato qui
    
    while queue not empty:
        current = queue.popleft()
        
        // Controllo goal: almeno un vaso contiene esattamente target
        if target in current:
            return reconstruct_path(current, parent, action_map)
        
        for (next_state, action) in get_neighbors(current, capacities):
            if next_state not in visited:
                visited.add(next_state)
                parent[next_state] = current
                action_map[next_state] = action
                queue.append(next_state)
    
    return None  // nessuna soluzione
```

### 4. Ricostruzione Percorso

```
function reconstruct_path(goal_state, parent, action_map):
    path = []
    state = goal_state
    
    while parent[state] is not None:
        path.append(action_map[state])
        state = parent[state]
    
    path.reverse()
    return path
```

### 5. BFS Generator (per Streamlit Real-time)

```
function bfs_solve_generator(capacities, target):
    if not can_solve(capacities, target):
        yield ("not_found", None)
        return
        
    initial_state = tuple([0] * len(capacities))
    queue = deque([initial_state])
    visited = {initial_state}
    parent = {initial_state: None}
    action_map = {initial_state: None}
    
    while queue not empty:
        current = queue.popleft()
        
        yield ("visiting", current, len(parent))  // per GUI
        
        if target in current:
            yield ("found", reconstruct_path(current, parent, action_map))
            return
        
        for (next_state, action) in get_neighbors(current, capacities):
            if next_state not in visited:
                visited.add(next_state)
                parent[next_state] = current
                action_map[next_state] = action
                queue.append(next_state)
                yield ("expanded", current, next_state, action)
    
    yield ("not_found", None)
```

### 6. Formattazione Output

```
function format_solution(path, capacities):
    structured = path  // [(fill, 0), (pour, 0, 1), ...]
    
    readable = []
    for action in path:
        if action[0] == "fill":
            readable.append(f"Riempire vaso {action[1]}")
        elif action[0] == "empty":
            readable.append(f"Svuotare vaso {action[1]}")
        elif action[0] == "pour":
            readable.append(f"Travasare vaso {action[1]} → vaso {action[2]}")
    
    return structured, readable
```

## Streamlit GUI (`app.py`)

### Layout
```
┌─────────────────────────────────────┐
│  Input: Capacities [3, 5, 8]       │
│  Target: 4                          │
│  [Solve Button]                     │
├─────────────────────────────────────┤
│  Visualizzazione Vasi (animated):   │
│  ┌────┐  ┌────┐  ┌────┐           │
│  │████│  │░░░░│  │██░░│ ← colored  │
│  │ 4  │  │ 0  │  │ 3  │   jugs    │
│  │ /7 │  │ /5 │  │ /8 │ (proportional│
│  └────┘  └────┘  └────┘   height)  │
├─────────────────────────────────────┤
│  Slider: Naviga tra i passaggi     │
│  ◄────●────► Step 2/5              │
├─────────────────────────────────────┤
│  Dettagli Azione:                   │
│  🟢 Travaso da vaso 0 a vaso 1...  │
│  Prima: (0, 0, 0)                  │
│  Dopo:  (4, 0, 0)                  │
├─────────────────────────────────────┤
│  🌳 Albero BFS (expandable):        │
│  Grigio: visitati | Rosso: soluzione│
│  Blu: target (graphviz)              │
├─────────────────────────────────────┤
│  Solution:                          │
│  1. Riempire vaso 0                 │
│  2. Travasare vaso 0 → vaso 1      │
└─────────────────────────────────────┘
```

### Animation Features

- **Proportional jug scaling**: Jug height proportional to capacity (max jug = 300px)
- **Interactive slider**: Navigate through solution steps with real-time jug visualization
- **Action animation**: Color-coded animation for FILL (🔵), EMPTY (🟠), POUR (🟢) actions
- **Step details**: Display action description, state before/after for each step
- **BFS Tree visualization**: Expandable Graphviz tree with real parent-child links and 2-color scheme:
  - **Light Red**: States visited during BFS exploration
  - **Blue**: States in the solution path (with thicker blue edges)
- **Performance**: Streamlit caching (`@st.cache_data`) for instant result retrieval on re-runs
- **Complete summary**: Expandable section with all steps
- **New Game button**: Reset and start fresh instantly

### Librerie per GUI
- `streamlit` - framework base
- `graphviz` - per albero BFS (integratione nativa con Streamlit)
- `streamlit-agraph` (opzionale) per grafi interattivi

## Dipendenze (`requirements.txt`)
```
streamlit
graphviz
pytest
```
