from __future__ import annotations

import logging
from logging.handlers import RotatingFileHandler
from pathlib import Path


def setup_logging(verbosity: int = 0, log_path: Path | None = None) -> None:
    level = logging.WARNING
    if verbosity >= 2:
        level = logging.DEBUG
    elif verbosity == 1:
        level = logging.INFO

    log_dir = Path("log")
    log_dir.mkdir(parents=True, exist_ok=True)
    logfile = log_path or (log_dir / "codex-sniper.log")

    fmt = logging.Formatter("%(asctime)s %(levelname)s %(name)s: %(message)s")

    # Console handler
    ch = logging.StreamHandler()
    ch.setLevel(level)
    ch.setFormatter(fmt)

    # Rotating file handler (5 files x 1MB)
    fh = RotatingFileHandler(logfile, maxBytes=1_000_000, backupCount=5, encoding="utf-8")
    fh.setLevel(level)
    fh.setFormatter(fmt)

    root = logging.getLogger()
    # Clear existing handlers to avoid duplicate logs in repeated runs/tests
    for h in list(root.handlers):
        root.removeHandler(h)
    root.setLevel(level)
    root.addHandler(ch)
    root.addHandler(fh)

