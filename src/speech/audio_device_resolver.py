"""Helpers for resolving audio input devices across platforms."""

from __future__ import annotations

import os
import re
from typing import Any
from collections.abc import Iterable

import sounddevice

from src.core.errors import AdapterError

_NON_ALNUM_PATTERN = re.compile(r"[^a-z0-9]+")
_CARD_SELECTOR_PATTERN = re.compile(r"CARD=([^,\s]+)")
_ALSA_CARD_HEADER_PATTERN = re.compile(
    r"^\s*\d+\s+\[(?P<short_name>[^\]]+)\]:\s+.+?\s+-\s+(?P<card_name>.+?)\s*$"
)


class AudioDeviceResolver:
    """Resolve input-capable sound devices with cross-platform fallbacks."""

    def resolve_input_device(self, selector: str | None) -> int | None:
        """Resolve a configured selector to a sounddevice input device index."""
        if selector is None:
            return None

        selector = selector.strip()
        if not selector:
            return None

        try:
            requested_index = int(selector)
        except ValueError:
            requested_index = None

        devices = self.list_input_devices()
        if requested_index is not None:
            for device in devices:
                if device["index"] == requested_index:
                    return requested_index
            raise AdapterError(
                f"Audio input device index '{selector}' is not a valid available index"
            )

        selector_lower = selector.casefold()
        selector_normalized = self._normalize_label(selector)
        selector_tokens = tuple(self._iter_tokens(selector))

        for matcher in (
            lambda candidate: selector_lower == candidate.casefold(),
            lambda candidate: selector_lower in candidate.casefold(),
            lambda candidate: selector_normalized == self._normalize_label(candidate),
            lambda candidate: selector_normalized in self._normalize_label(candidate),
            lambda candidate: self._all_tokens_match(selector_tokens, candidate),
        ):
            matched_index = self._find_matching_device_index(devices, matcher)
            if matched_index is not None:
                return matched_index

        raise AdapterError(
            f"Audio input device '{selector}' not found. "
            f"Available devices: {self.format_input_devices(devices)}"
        )

    def list_input_devices(self) -> list[dict[str, Any]]:
        """Return input-capable sounddevice entries with platform-safe aliases."""
        hostapis = self._query_hostapis_safe()
        alsa_cards = self._load_alsa_cards()

        available_devices: list[dict[str, Any]] = []
        for fallback_index, raw_device in enumerate(sounddevice.query_devices()):
            device = dict(raw_device)
            device_index = int(device.get("index", fallback_index))
            max_input_channels = int(device.get("max_input_channels", 0) or 0)
            if max_input_channels <= 0:
                continue

            hostapi_name = self._resolve_hostapi_name(device, hostapis)
            aliases = self._build_aliases(device, hostapi_name, alsa_cards)

            available_devices.append(
                {
                    "index": device_index,
                    "name": str(device.get("name", "")).strip(),
                    "hostapi_name": hostapi_name,
                    "aliases": tuple(sorted(aliases)),
                }
            )

        return available_devices

    def format_input_devices(
        self, devices: Iterable[dict[str, Any]]
    ) -> list[tuple[int, str, tuple[str, ...]]]:
        """Build a compact device listing for logs and error messages."""
        return [
            (
                int(device["index"]),
                str(device["name"]).strip(),
                tuple(
                    alias
                    for alias in device.get("aliases", ())
                    if alias and alias != str(device["name"]).strip()
                ),
            )
            for device in devices
        ]

    def list_cli_input_devices(self):
        devices = self.list_input_devices()
        if not devices:
            raise Exception("\nNo input-capable audio devices were found.")

        print("\nAvailable audio input devices:")
        for index, name, aliases in self.format_input_devices(devices):
            details = f"[{index}] {name}"
            if aliases:
                details += f" | aliases: {', '.join(aliases)}"
            print(details)

    def _find_matching_device_index(
        self,
        available_devices: list[dict[str, Any]],
        matcher: Any,
    ) -> int | None:
        for device in available_devices:
            candidates = [device["name"], *device.get("aliases", ())]
            if any(matcher(candidate) for candidate in candidates if candidate):
                return int(device["index"])
        return None

    def _all_tokens_match(self, selector_tokens: tuple[str, ...], candidate: str) -> bool:
        if not selector_tokens:
            return False

        candidate_tokens = set(self._iter_tokens(candidate))
        return all(token in candidate_tokens for token in selector_tokens)

    def _normalize_label(self, value: str) -> str:
        return _NON_ALNUM_PATTERN.sub("", value.casefold())

    def _iter_tokens(self, value: str) -> Iterable[str]:
        for token in _NON_ALNUM_PATTERN.split(value.casefold()):
            if token:
                yield token

    def _query_hostapis_safe(self) -> list[dict[str, Any]]:
        try:
            return [dict(hostapi) for hostapi in sounddevice.query_hostapis()]
        except Exception:
            return []

    def _resolve_hostapi_name(
        self,
        device: dict[str, Any],
        hostapis: list[dict[str, Any]],
    ) -> str:
        hostapi_index = device.get("hostapi")
        if not isinstance(hostapi_index, int):
            return ""
        if hostapi_index < 0 or hostapi_index >= len(hostapis):
            return ""
        return str(hostapis[hostapi_index].get("name", "")).strip()

    def _build_aliases(
        self,
        device: dict[str, Any],
        hostapi_name: str,
        alsa_cards: dict[str, dict[str, str]],
    ) -> set[str]:
        aliases = {str(device.get("name", "")).strip()}

        if hostapi_name:
            aliases.add(hostapi_name)

        device_name = str(device.get("name", "")).strip()
        for card_selector in _CARD_SELECTOR_PATTERN.findall(device_name):
            card_details = alsa_cards.get(card_selector)
            if not card_details:
                continue

            aliases.add(card_selector.strip())
            aliases.add(card_details.get("short_name", "").strip())
            aliases.add(card_details.get("card_name", "").strip())
            aliases.add(card_details.get("description", "").strip())

        return {alias for alias in aliases if alias}

    def _load_alsa_cards(self, path: str = "/proc/asound/cards") -> dict[str, dict[str, str]]:
        if os.name == "nt" or not os.path.exists(path):
            return {}

        try:
            with open(path, encoding="utf-8") as cards_file:
                lines = cards_file.read().splitlines()
        except OSError:
            return {}

        cards: dict[str, dict[str, str]] = {}
        for line_index, line in enumerate(lines):
            match = _ALSA_CARD_HEADER_PATTERN.match(line)
            if match is None:
                continue

            short_name = match.group("short_name").strip()
            description = ""
            if line_index + 1 < len(lines):
                description = lines[line_index + 1].strip()

            cards[short_name] = {
                "short_name": short_name,
                "card_name": match.group("card_name").strip(),
                "description": description,
            }

        return cards
