#! /usr/bin/env python3

from pathlib import Path
from datetime import datetime
import shutil

def copy_with_timestamp(src_file, dest_dir):
    src_file = Path(src_file)
    dest_dir = Path(dest_dir)

    # Ensure destination directory exists
    dest_dir.mkdir(parents=False, exist_ok=True)

    # Build timestamped filename
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    dest_file = dest_dir / f"{src_file.stem}_{timestamp}{src_file.suffix}"

    # Copy file
    shutil.copy2(src_file, dest_file)

    return