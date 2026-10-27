#!/usr/bin/env python3
"""The one duplicate-key-rejecting YAML loader the generators share.

`StrictSafeLoader` used to live in `scripts/metadata/contract.py`, beside the
jsonschema import. The generators (`scripts/gen_views.py` and the board-page
writer) read metadata with PyYAML only, so they import the loader from here
rather than from the validation module (blocking review finding, T-5-28).

The loader also bounds nesting depth. PyYAML's composer recurses once per
nested sequence or mapping, so a small document with a thousand nested flow
sequences would otherwise exhaust the Python stack. The bound sits far above
any legitimate metadata document and raises `ComposerError`, a
`yaml.YAMLError`, so every caller's existing `except yaml.YAMLError` renders a
content error instead of a traceback (T-10-28).

This module imports `yaml` and the standard library and nothing else, so a
PyYAML-only environment can import it without jsonschema.
"""

from __future__ import annotations

from collections.abc import Hashable

import yaml
from yaml.composer import ComposerError
from yaml.constructor import ConstructorError


class DepthBoundedLoaderMixin:
    """A mixin for PyYAML loaders that bounds composer recursion depth (CR-01, CR-05).

    PyYAML's composer recurses once per nested sequence or mapping. A document
    with many nested flow sequences exhausts the Python recursion limit. This
    mixin bounds nesting depth at `MAX_DEPTH` (default 64) and raises
    `ComposerError`, a `yaml.YAMLError`.
    """

    MAX_DEPTH = 64

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._node_depth = 0

    def compose_node(self, parent, index):
        """Compose one node, refusing a document deeper than `MAX_DEPTH`.

        The counter rises once per nested node and is restored in `finally`, so
        siblings do not accumulate depth. Raising here is deliberate: a
        `ComposerError` is a `yaml.YAMLError`, the type every caller already
        renders as a content error.
        """
        self._node_depth += 1
        try:
            if self._node_depth > self.MAX_DEPTH:
                raise ComposerError(
                    None, None, f"nesting depth exceeds {self.MAX_DEPTH}", None
                )
            return super().compose_node(parent, index)
        finally:
            self._node_depth -= 1


class StrictSafeLoader(DepthBoundedLoaderMixin, yaml.SafeLoader):
    """A `SafeLoader` that rejects a duplicated mapping key and deep nesting.

    PyYAML silently keeps the last value of a repeated key, so a duplicated
    `source:` or `toolchain:` block would override the first one without a
    trace. This loader turns that into a parse error, which the caller reports
    as an ERROR record at exit 1.

    Nesting is bounded at `MAX_DEPTH` (inherited from `DepthBoundedLoaderMixin`),
    which is generous for a metadata document (the deepest shipped block is about
    four levels). A document that needs more is a contract change, not a reason
    to raise the bound quietly.
    """

    def construct_mapping(self, node, deep=False):
        seen = set()
        for key_node, _ in node.value:
            key = self.construct_object(key_node, deep=deep)
            # A composed (sequence or mapping) key is not hashable, so the
            # membership test below would raise TypeError and escape as a
            # traceback. Delegate to BaseConstructor.construct_mapping, which
            # raises ConstructorError ("found unhashable key") — a
            # yaml.YAMLError the caller renders as an ERROR record at exit 1
            # (T-04-24).
            if not isinstance(key, Hashable):
                return super().construct_mapping(node, deep=deep)
            if key in seen:
                raise ConstructorError(
                    "while constructing a mapping",
                    node.start_mark,
                    f"found duplicate key {key!r}",
                    key_node.start_mark,
                )
            seen.add(key)
        return super().construct_mapping(node, deep=deep)
