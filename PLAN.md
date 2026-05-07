# Water Jug Puzzle Solver - Plan

## Changelog / Status

- [x] **2026-05-07** - Core solver implemented: `models.py` and `solver.py` with BFS algorithm, GCD pre-check, and Google-style docstrings
- [x] **2026-05-07** - Tests implemented: `test_solver.py` with comprehensive test coverage for `can_solve` and `bfs_solve`
- [ ] **Next Step** - Implement `formatter.py` for output formatting (structured + readable)
- [ ] Implement `main.py` CLI entry point
- [ ] Implement `visualization.py` for Streamlit jug rendering
- [ ] Implement `tree_viz.py` for BFS tree visualization
- [ ] Implement `app.py` Streamlit GUI with real-time BFS generator
- [ ] Add BFS generator variant in `solver.py` for Streamlit real-time updates

## Architecture

```
water_jug_solver/
├── models.py           # State, Action, ActionType enum
├── solver.py           # BFS + pre-check GCD, generator for real-time
├── formatter.py        # Output strutturato + leggibile
├── visualization.py    # Funzioni per rendering jugs (streamlit)
├── tree_viz.py         # Visualizzazione albero BFS (graphviz/networkx)
├── main.py             # CLI entry point
└── app.py              # Streamlit GUI
```

### Module Responsibilities

| File | Responsabilità |
|------|----------------|
| `models.py` | `JugState` (tupla immutabile dello stato), `ActionType` (enum: FILL, EMPTY, POUR), `Action` definition |
| `solver.py` | BFS, pre-check GCD, gestione visited states, path reconstruction, generator per Streamlit |
| `formatter.py` | `format_solution()` → restituisce lista azioni + descrizione testuale |
| `visualization.py` | Rendering dei vasi per Streamlit GUI |
| `tree_viz.py` | Visualizzazione albero BFS con graphviz |
| `main.py` | Parsing input CLI (`capacities: list[int]`, `target: int`), esecuzione, print output |
| `app.py` | Streamlit GUI con input, visualizzazione real-time, albero BFS |

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
│  Progress:                          │
│  ● Exploring state: (0, 0, 0)      │
│  ● Expanded: 15 states              │
├─────────────────────────────────────┤
│  Jug Visualization (real-time):     │
│  [████░░░] Vaso 0: 4/7             │
│  [░░░░░░░] Vaso 1: 0/5             │
├─────────────────────────────────────┤
│  BFS Tree (graphviz):               │
│  (0,0,0) → (7,0,0) → (7,5,0)...   │
├─────────────────────────────────────┤
│  Solution:                          │
│  1. Riempire vaso 0                 │
│  2. Travasare vaso 0 → vaso 1      │
└─────────────────────────────────────┘
```

### Librerie per GUI
- `streamlit` - framework base
- `graphviz` - per albero BFS
- `streamlit-agraph` (opzionale) per grafi interattivi

## Dipendenze (`requirements.txt`)
```
streamlit
graphviz
pytest
```
