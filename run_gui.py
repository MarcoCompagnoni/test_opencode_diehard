"""Launcher for Water Jug Puzzle Streamlit GUI.

Run this file from PyCharm to start the Streamlit web interface.
"""

import subprocess
import sys
from pathlib import Path

def main() -> None:
    """Launch the Streamlit GUI."""
    # Get the path to app.py (same directory as this file)
    app_path = Path(__file__).parent / "app.py"
    
    if not app_path.exists():
        print(f"Errore: {app_path} non trovato.")
        sys.exit(1)
    
    print("Avvio Water Jug Puzzle GUI...")
    print(f"Streamlit app: {app_path}")
    print("-" * 50)
    
    # Launch streamlit
    cmd = [sys.executable, "-m", "streamlit", "run", str(app_path)]
    
    try:
        subprocess.run(cmd, check=True)
    except KeyboardInterrupt:
        print("\nGUI arrestata.")
    except FileNotFoundError:
        print("Errore: Streamlit non installato. Esegui: pip install streamlit")
        sys.exit(1)
    except Exception as e:
        print(f"Errore nell'avvio: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
