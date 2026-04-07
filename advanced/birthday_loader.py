from __future__ import annotations

from datetime import date
from pathlib import Path

import pandas as pd


class BirthdayLoader:
    """Loads birthdays from a CSV and filters to today's matches."""

    def __init__(self, csv_path: Path) -> None:
        self._csv_path = csv_path

    def load(self) -> pd.DataFrame:
        """Read and validate the CSV. Returns a clean DataFrame.

        Raises:
            FileNotFoundError: if the CSV does not exist.
            ValueError: if required columns are missing.
        """
        if not self._csv_path.exists():
            raise FileNotFoundError(f"Birthday CSV not found: {self._csv_path}")

        df = pd.read_csv(self._csv_path)
        df.columns = [c.strip().lower() for c in df.columns]

        required = {"name", "email", "year", "month", "day"}
        missing = required - set(df.columns)
        if missing:
            raise ValueError(f"CSV is missing required columns: {missing}")

        df["month"] = pd.to_numeric(df["month"], errors="coerce")
        df["day"] = pd.to_numeric(df["day"], errors="coerce")

        bad = df[df[["name", "email", "month", "day"]].isna().any(axis=1)]
        if not bad.empty:
            print(f"Skipping {len(bad)} invalid row(s):")
            print(bad[["name", "email", "year", "month", "day"]])

        df = df.dropna(subset=["name", "email", "month", "day"]).copy()
        df["name"] = df["name"].astype(str).str.strip()
        df["email"] = df["email"].astype(str).str.strip()
        df["month"] = df["month"].astype(int)
        df["day"] = df["day"].astype(int)
        return df

    def today_birthdays(self, df: pd.DataFrame) -> pd.DataFrame:
        """Filter DataFrame to rows whose month/day match today.

        Returns:
            A (possibly empty) DataFrame of today's birthday people.
        """
        today = date.today()
        return df[(df["month"] == today.month) & (df["day"] == today.day)].copy()
