import lizard
import os
import fnmatch
import json
from typing import Optional
import argparse

def _get_args():
    parser = argparse.ArgumentParser(
        description="Calculate average cyclomatic complexity with lizard for files or directories."
    )
    parser.add_argument(
        "paths",
        nargs="*",
        default=["."],
        help="Files or directories to scan. Defaults to ./Thunder when omitted.",
    )
    return parser.parse_args()


def _should_ignore(path: str, ignore_patterns: list[str]) -> bool:
    return any(
        fnmatch.fnmatch(os.path.basename(path), pattern) or fnmatch.fnmatch(path, pattern)
        for pattern in ignore_patterns
    )


def _analyze_file(file_path: str):
    analysis = lizard.analyze_file(file_path)
    if not analysis.function_list:
        return 0, 0, None

    total_complexity = sum(
        fn.cyclomatic_complexity for fn in analysis.function_list
    )
    total_functions = len(analysis.function_list)
    return total_complexity, total_functions, {
        "path": file_path,
        "avg_ccn": round(total_complexity / total_functions, 2),
    }


def scan_with_lizard(dir_path: str, ignore_patterns: Optional[list[str]] = None):
    """Scan a directory with Lizard to calculate cyclomatic complexity via recursion.

    Args:
        dir_path (str): The path to the directory to scan.
        ignore_patterns (list[str], optional): A list of patterns to ignore.

    Returns:
        tuple:
        A tuple containing the total cyclomatic complexity, the total
        number of functions, and per-file average complexity results.
        
    """
    if ignore_patterns is None:
        ignore_patterns = ["*.pyc", ".git", "*.md", "*.txt", "*.json", "*.yml", "*.yaml", "*.lock", "node_modules/*"]

    total_complexity = 0
    total_functions = 0
    file_results = []

    files = os.scandir(dir_path)

    for file in files:
        if _should_ignore(file.path, ignore_patterns):
            continue

        if file.is_dir(follow_symlinks=False):
            dir_complexity, dir_functions, dir_results = scan_with_lizard(
                dir_path=file.path,
                ignore_patterns=ignore_patterns,
            )
            total_complexity += dir_complexity
            total_functions += dir_functions
            file_results.extend(dir_results)
        else:
            file_complexity, file_functions, file_result = _analyze_file(file.path)
            total_complexity += file_complexity
            total_functions += file_functions
            if file_result is not None:
                file_results.append(file_result)

    return total_complexity, total_functions, file_results


def scan_path(path: str, ignore_patterns: Optional[list[str]] = None):
    if ignore_patterns is None:
        ignore_patterns = ["*.pyc", ".git", "*.md", "*.txt", "*.json", "*.yml", "*.yaml", "*.lock", "node_modules/*"]

    if not os.path.exists(path):
        raise FileNotFoundError(f"Path does not exist: {path}")

    if _should_ignore(path, ignore_patterns):
        return 0, 0, []

    if os.path.isdir(path):
        return scan_with_lizard(path, ignore_patterns)

    file_complexity, file_functions, file_result = _analyze_file(path)
    if file_result is None:
        return 0, 0, []

    return file_complexity, file_functions, [file_result]

def main():
    args = _get_args()

    total_complexity = 0
    total_functions = 0
    files = []

    for path in args.paths:
        path_complexity, path_functions, path_files = scan_path(path)
        total_complexity += path_complexity
        total_functions += path_functions
        files.extend(path_files)

    overall_mean_ccn = round(
        sum(file_result["avg_ccn"] for file_result in files) / len(files),
        2,
    ) if files else 0

    payload = {
        "overall_mean_ccn": overall_mean_ccn,
        "files": files,
    }

    print(json.dumps(payload))

if __name__ == "__main__":
    main()
