"""
Compatibility helpers for pytest >= 9 + pytest-asyncio 1.3.x
----------------------------------------------------------------

Pytest 9 removed a handful of internal attributes (`collector.obj`,
`FixtureDef.unittest`) that older versions of pytest-asyncio still rely on.
Upstream fixes are pending, so we apply a local shim to keep the existing pins
working without downgrading pytest.
"""

from __future__ import annotations

import types
from typing import Any


def ensure_pytest_asyncio_compat() -> None:
    """Patch pytest-asyncio so it cooperates with pytest 9."""
    try:
        import pytest_asyncio.plugin as plugin  # type: ignore[attr-defined]
        from _pytest.fixtures import FixtureDef  # type: ignore
    except Exception:
        return

    _patch_collectstart(plugin)

    if not hasattr(FixtureDef, "unittest"):
        FixtureDef.unittest = False  # type: ignore[attr-defined]


def _patch_collectstart(plugin: Any) -> None:
    hook = getattr(plugin, "pytest_collectstart", None)
    if hook is None or getattr(hook, "__dict__", {}).get("_focus_kraliki_patched"):
        return

    original = types.FunctionType(
        hook.__code__,
        hook.__globals__,
        name=hook.__name__,
        argdefs=hook.__defaults__,
        closure=hook.__closure__,
    )
    original.__kwdefaults__ = hook.__kwdefaults__

    def safe_collectstart(collector, _orig=original):
        if not hasattr(collector, "obj"):
            return None
        return _orig(collector)

    hook.__code__ = safe_collectstart.__code__
    hook.__defaults__ = safe_collectstart.__defaults__
    hook.__kwdefaults__ = safe_collectstart.__kwdefaults__
    hook.__dict__["_focus_kraliki_patched"] = True
