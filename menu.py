import os
import subprocess
import sys
from pathlib import Path

from art import LOGO

ORIGINAL = Path(__file__).parent / "original" / "main.py"
ADVANCED = Path(__file__).parent / "advanced" / "main.py"

while True:
    os.system("cls" if os.name == "nt" else "clear")
    print(LOGO)
    print("Birthday Email Bot — Day 32")
    print("=" * 40)
    print("1. Original build  (course version)")
    print("2. Advanced build  (OOP + config)")
    print("q. Quit")
    print()

    choice = input("Select an option: ").strip().lower()

    if choice == "1":
        subprocess.run([sys.executable, str(ORIGINAL)], cwd=str(ORIGINAL.parent))
        input("\nPress Enter to return to menu...")
    elif choice == "2":
        subprocess.run([sys.executable, str(ADVANCED)], cwd=str(ADVANCED.parent))
        input("\nPress Enter to return to menu...")
    elif choice == "q":
        break
    else:
        print("Invalid choice. Try again.")
