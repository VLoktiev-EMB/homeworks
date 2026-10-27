# Phase 11: Pilot Homework 1.3 — Finalization - Discussion Log

> **Audit trail only.** Do not use as input to planning, research, or execution agents.
> Decisions are captured in CONTEXT.md — this log preserves the alternatives considered.

**Date:** 2026-10-28
**Phase:** 11-Pilot Homework 1.3 — Finalization
**Areas discussed:** Simulation & Evidence, Measurement Ledger & Report Contract, Schematics Visualization, Generic Infrastructure Decoupling & Finalization

---

## Simulation & Evidence (Wokwi scenario.yaml)

| Option | Description | Selected |
|--------|-------------|----------|
| Повний сценарій | Симуляція натискань кнопки, перевірка перемикання всіх 4 патернів та збір повного serial.log | |
| Смоук-тест | Перевірка старту системи, ініціалізації драйвера та першого такту GPIO4 | |
| Ви вирішуєте | Делеговано агенту | ✓ |

**User's choice:** Ви вирішуєте (You decide)
**Notes:** Автоматизувати сценарій на перевірку старту та переходу режимів за кнопкою, генеруючи `serial.log` у межах 3-5 с.

---

## Measurement Ledger у звіті (Звіт: виміряні vs симульовані дані)

| Option | Description | Selected |
|--------|-------------|----------|
| not measured + transition log | Фізичні виміри залишаємо "not measured" (стенд оффлайн), але додаємо transition logging у прошивку для serial-log | |
| Без змін | Залишити все як є в report.md | |
| Ви вирішуєте | Делеговано агенту | ✓ |

**User's choice:** Ви вирішуєте (You decide)
**Notes:** Чесний інженерний статус `not measured` для бенч-обладнання під час CI; додано transition logging для спостережуваних даних перемикань у `serial.log`.

---

## Візуалізація схеми (Schematics in report & README)

| Option | Description | Selected |
|--------|-------------|----------|
| SVG у звіті + Mermaid у README | Векторний SVG (assets/schematic.svg) у звіті report.md + Mermaid-діаграма у README.md | ✓ |
| SVG + Mermaid в обох файлах | Продублювати обидва формати | |
| Ви вирішуєте | Делеговано агенту | |

**User's choice:** Векторний SVG (assets/schematic.svg) у звіті report.md + Mermaid-діаграма у README.md
**Notes:** Schemdraw векторний SVG вбудовується у Section 5 звіту; Mermaid flowchart у README; `diagram.json` залишається джерелом для Wokwi.

---

## Відв'язування інфраструктури від 1_3 (Generic Decoupling)

| Option | Description | Selected |
|--------|-------------|----------|
| Генералізація шаблонів/скриптів | Очистити templates, scripts, docs від прив'язок до 1_3, а саму 1_3 фіналізувати як звичайну домашку | |
| Повне перестворення | Видалити 1_3 і перестворити наново через new_homework | |
| Ви вирішуєте | Делеговано агенту | ✓ |

**User's choice:** Ви вирішуєте (You decide)
**Notes:** Користувач окремо підкреслив вимогу прибрати будь-які згадки про `1_3` з документації, шаблонів і скриптів: інфраструктура має бути повністю універсальною (`homeworks/<id>`), а `1_3-police-flasher` — просто одна конкретна реалізація, а не хардкоджений еталон.

---

## the agent's Discretion

- Точні часові затримки в `scenario.yaml` та формат повідомлень логера у прошивці.
- Конкретні правки у `scripts/gen_clangd_db.py` та `scripts/gen_schematic.py` для забезпечення динамічного сканування без жорстко заданих назв.

## Deferred Ideas

- None.
