"""Shell degli script remoti: su Windows usa Git Bash, non il launcher WSL."""

import os
from pathlib import Path
import shutil


def trova_bash():
    if os.name != "nt":
        return shutil.which("bash")
    git = shutil.which("git")
    if git:
        candidato = Path(git).resolve().parent.parent / "bin" / "bash.exe"
        if candidato.is_file():
            return str(candidato)
    candidato = shutil.which("bash")
    if candidato and "system32" not in Path(candidato).parts[-2].lower():
        return candidato
    return None


def percorso_shell(percorso):
    return str(percorso).replace("\\", "/")
