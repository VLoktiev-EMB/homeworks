#!/usr/bin/env python3
"""The one duplicate-key-rejecting YAML loader the generators share.

`StrictSafeLoader` used to live in `scripts/metadata/contract.py`, beside the
jsonschema import. The generators (`scripts/gen_views.py` and the board-page
writer) read metadata with PyYAML only, so they import the loader from here
rather than from the validation module (blocking review finding, T-5-28).

This module imports `yaml` and the standard library and nothing else, so a
PyYAML-only environment can import it without jsonschema.
"""

from __future__ import annotations

from collections.abc import Hashable

import yaml
from yaml.constructor import ConstructorError


class StrictSafeLoader(yaml.SafeLoader):
    """A `SafeLoader` that rejects a duplicated mapping key (T-04-20).

    PyYAML silently keeps the last value of a repeated key, so a duplicated
    `source:` or `toolchain:` block would override the first one without a
    trace. This loader turns that into a parse error, which the caller reports
    as an ERROR record at exit 1.
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
