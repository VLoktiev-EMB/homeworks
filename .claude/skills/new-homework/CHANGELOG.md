# Changelog

## 2026-10-26 — 0.2 language follows the framework

- The ESP-IDF template now ships `src/main.c` and `language: c`, so the intake derives
  the language from the framework instead of always recording `cpp`; the Arduino
  template stays C++.

## 2026-10-26 — initial 0.1 contract, phase 9 planning run

- Added the eight-topic intake bank — mode, board, framework, language,
  specification, simulation, tests and deliverables — with each topic's default,
  conditional branch and state key.
- Added the five-block guided loop with the exact `[Продовжити | Поясни глибше | Стоп]`
  pause and the one-shot mode over the same bank.
- Added the three checkpoints that write one state file before the menu, the conflict
  and ambiguity record with its recommended assumption, and the confirmed changelog
  step.
