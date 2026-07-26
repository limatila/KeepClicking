"""PyInstaller hook that trims non-runtime sklearn data from production builds."""

from __future__ import annotations

from PyInstaller.utils.hooks import collect_data_files


def _is_runtime_data(data_file: tuple[str, str]) -> bool:
    source_path = data_file[0].replace("/", "\\").casefold()
    return "\\sklearn\\tests\\" not in source_path and "\\sklearn\\datasets\\" not in source_path


datas = [
    data_file
    for data_file in collect_data_files("sklearn")
    if _is_runtime_data(data_file)
]
