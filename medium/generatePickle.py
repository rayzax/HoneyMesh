#!/usr/bin/env python3
"""
generatePickle.py - Cowrie Filesystem Pickle Generator
Adapted from Cowrie's createfs.py for HoneyMesh integration
"""

import fnmatch
import os
import pickle
import sys
from stat import (
    S_ISBLK,
    S_ISCHR,
    S_ISDIR,
    S_ISFIFO,
    S_ISLNK,
    S_ISREG,
    S_ISSOCK,
    ST_MODE,
)

# File structure indices
(
    A_NAME,
    A_TYPE,
    A_UID,
    A_GID,
    A_SIZE,
    A_MODE,
    A_CTIME,
    A_CONTENTS,
    A_TARGET,
    A_REALFILE,
) = range(0, 10)

# File types
T_LINK, T_DIR, T_FILE, T_BLK, T_CHR, T_SOCK, T_FIFO = range(0, 7)

# Blacklist patterns
BLACKLIST_FILES = [
    "/root/fs.pickle",
    "/root/createfs",
    "*cowrie*",
    "*kippo*",
    "*.pickle",
]


def check_blacklist(filepath):
    """Check if file matches blacklist patterns"""
    for pattern in BLACKLIST_FILES:
        if fnmatch.fnmatch(filepath, pattern):
            return True
    return False


def recurse(localroot, root, tree, maxdepth=100, verbose=False):
    """Recursively build filesystem tree"""
    if maxdepth == 0:
        return

    localpath = os.path.join(localroot, root[1:])

    if verbose:
        print(f"Processing: {localpath}")

    if not os.access(localpath, os.R_OK):
        if verbose:
            print(f"Cannot access: {localpath}")
        return

    try:
        items = os.listdir(localpath)
    except PermissionError:
        if verbose:
            print(f"Permission denied: {localpath}")
        return

    for name in items:
        fspath = os.path.join(root, name)
        if check_blacklist(fspath):
            continue

        path = os.path.join(localpath, name)

        try:
            if os.path.islink(path):
                s = os.lstat(path)
            else:
                s = os.stat(path)
        except OSError:
            continue

        entry = [
            name,
            T_FILE,
            s.st_uid,
            s.st_gid,
            s.st_size,
            s.st_mode,
            int(s.st_mtime),
            [],
            None,
            None,
        ]

        if S_ISLNK(s[ST_MODE]):
            if not os.access(path, os.R_OK):
                continue
            realpath = os.path.realpath(path)
            if not realpath.startswith(localroot):
                continue
            else:
                entry[A_TYPE] = T_LINK
                entry[A_TARGET] = realpath[len(localroot):]
        elif S_ISDIR(s[ST_MODE]):
            entry[A_TYPE] = T_DIR
            if maxdepth > 0:
                recurse(localroot, fspath, entry[A_CONTENTS], maxdepth - 1, verbose)
        elif S_ISREG(s[ST_MODE]):
            entry[A_TYPE] = T_FILE
        elif S_ISBLK(s[ST_MODE]):
            entry[A_TYPE] = T_BLK
        elif S_ISCHR(s[ST_MODE]):
            entry[A_TYPE] = T_CHR
        elif S_ISSOCK(s[ST_MODE]):
            entry[A_TYPE] = T_SOCK
        elif S_ISFIFO(s[ST_MODE]):
            entry[A_TYPE] = T_FIFO

        tree.append(entry)


def generate_pickle(source_dir, output_file, maxdepth=15, verbose=False):
    """
    Generate pickle filesystem from source directory
    
    Args:
        source_dir: Directory containing filesystem structure
        output_file: Path to output pickle file
        maxdepth: Maximum recursion depth
        verbose: Enable verbose output
    
    Returns:
        True on success, False on failure
    """
    try:
        if not os.path.isdir(source_dir):
            print(f"Error: Source directory '{source_dir}' does not exist")
            return False

        if os.path.exists(output_file):
            print(f"Error: Output file '{output_file}' already exists")
            return False

        if verbose:
            print(f"Generating pickle from: {source_dir}")
            print(f"Output file: {output_file}")
            print(f"Max depth: {maxdepth}")

        # Create root tree structure
        tree = ["/", T_DIR, 0, 0, 0, 0, 0, [], ""]
        
        # Build filesystem tree
        recurse(source_dir, "/", tree[A_CONTENTS], maxdepth, verbose)

        # Write pickle file
        with open(output_file, 'wb') as f:
            pickle.dump(tree, f)

        if verbose:
            print(f"Successfully created pickle file: {output_file}")
        
        return True

    except Exception as e:
        print(f"Error generating pickle: {str(e)}")
        return False


def main():
    """Command line interface"""
    if len(sys.argv) < 3:
        print("Usage: python3 generatePickle.py <source_dir> <output_file> [maxdepth] [verbose]")
        print("  source_dir: Directory containing filesystem structure")
        print("  output_file: Path to output pickle file")
        print("  maxdepth: Maximum recursion depth (default: 15)")
        print("  verbose: Enable verbose output (1 or 0, default: 0)")
        sys.exit(1)

    source_dir = sys.argv[1]
    output_file = sys.argv[2]
    maxdepth = int(sys.argv[3]) if len(sys.argv) > 3 else 15
    verbose = bool(int(sys.argv[4])) if len(sys.argv) > 4 else False

    success = generate_pickle(source_dir, output_file, maxdepth, verbose)
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()
