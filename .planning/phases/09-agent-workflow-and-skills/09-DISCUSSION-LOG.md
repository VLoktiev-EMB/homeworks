# Phase 9: Agent Workflow and Skills - Discussion Log

> **Audit trail only.** Do not use as input to planning, research, or execution agents.
> Decisions are captured in CONTEXT.md — this log preserves the alternatives considered.

**Date:** 2026-10-26
**Phase:** 9-Agent Workflow and Skills
**Areas discussed:** Дім для скілів, Цикл guided-режиму, Чекпойнти й стан, Контракт скілів

---

## Дім для скілів

| Option | Description | Selected |
|--------|-------------|----------|
| Канон .claude + генератор | `.claude/skills/` — канонічне джерело; `.agents/skills/` генерується і перевіряється на drift | ✓ |
| .agents + symlink | Канонічний `.agents/skills/`, `.claude/skills/<skill>` — symlink | |
| Тільки .claude | Лише `.claude/skills/`, без дзеркала | |

**User's choice:** Канон .claude + генератор.
**Notes:** Claude Code читає лише `.claude/skills/`; решта агентів — `.agents/skills/`.

| Option | Description | Selected |
|--------|-------------|----------|
| Лише переносні шість | `name`, `description`, `license`, `compatibility`, `metadata`, `allowed-tools` | |
| Переносні + Claude-поля | Додати `user-invocable`, `disable-model-invocation`, `model`; генератор вирізає їх у дзеркалі | |
| Без обмежень | Використовувати все, що підтримує Claude Code | ✓ |

**User's choice:** Free text — «використати все що можна для клода, але вирізати для інших».
**Notes:** Канон може використовувати `context: fork`, hooks тощо; дзеркало отримує лише переносну поведінку.

| Option | Description | Selected |
|--------|-------------|----------|
| Явно + читання авто | Write/hardware-скіли — лише `/name`; `course-index` read-only може тригеритись описом | ✓ |
| Усі явно | Усі сім мають `disable-model-invocation: true` | |
| Усі авто | Опис у frontmatter тригерить усі скіли | |

**User's choice:** Явно + читання авто.

| Option | Description | Selected |
|--------|-------------|----------|
| Новий ген-skills | `scripts/gen_skills.py --check` + окремий pre-commit hook | ✓ |
| Розширити gen_views | Додати скіли в `gen_views.py` і `generated.manifest` | |
| Лише тест | `scripts/tests/test_skills.py` генерує в temp і порівнює | |

**User's choice:** Новий ген-skills.

| Option | Description | Selected |
|--------|-------------|----------|
| Комітити обидва | Свіжий checkout має скіли для Antigravity; drift ловиться в CI | ✓ |
| Лише канон | `.agents/skills/` генерується на вимогу й ігнорується | |

**User's choice:** Комітити обидва.

---

## Цикл guided-режиму

| Option | Description | Selected |
|--------|-------------|----------|
| Deliverable-рівень | scaffold → логіка/контролер → native-тести → wiring/diagram → звіт | ✓ |
| Рівень файлу | Один блок на файл | |
| Рівень можливості | Один блок на видиму можливість | |

**User's choice:** Deliverable-рівень.

| Option | Description | Selected |
|--------|-------------|----------|
| Опція на кожній паузі | `[Продовжити | Поясни глибше | Стоп]`; глибина не вгадується | ✓ |
| Лише явний запит | Користувач сам каже «не розумію» | |
| Кілька сигналів | Скіл виводить «застряг» із поведінки | |

**User's choice:** Опція на кожній паузі.

| Option | Description | Selected |
|--------|-------------|----------|
| YAML + тест | `references/question-bank.yaml` з вісьмома темами і тестом повноти | |
| Markdown-проза | `references/question-bank.md` з умовними гілками | ✓ |
| Спільний банк | Один банк на рівні репозиторію | |

**User's choice:** Markdown-проза.
**Notes:** Покриття восьми тем перевіряється review, без prose/doc-sync тесту.

| Option | Description | Selected |
|--------|-------------|----------|
| Питати першим | `mode` — перше питання банку; one-shot без пауз блоків, але з чекпойнтами | ✓ |
| Виводити з фрази | «зроби X» → one-shot, «допоможи зробити X» → guided | |
| Guided за замовчуванням | `--one-shot` як явний прапорець | |

**User's choice:** Питати першим.

| Option | Description | Selected |
|--------|-------------|----------|
| Агент пише | Агент пише код блоку, пояснює, запускає, ставить питання | ✓ |
| Користувач пише | Користувач набирає код за підказками | |
| Гібрид за блоком | Агент пише boilerplate, користувач — ядро | |

**User's choice:** Агент пише.

| Option | Description | Selected |
|--------|-------------|----------|
| Verification step | Кожен некодовий блок має власну перевірку | |
| Пропускати run | Блок завершується поясненням і питаннями | ✓ |
| Ручна перевірка | Користувач оглядає артефакт | |

**User's choice:** Пропускати run.

| Option | Description | Selected |
|--------|-------------|----------|
| Змішано | Одне відкрите «що станеться, якщо…» + опційне multiple-choice | ✓ |
| Лише відкрите | Одне відкрите питання-сценарій на блок | |
| Multiple-choice + why | Короткий вибір з обов'язковим «чому» | |

**User's choice:** Змішано.

| Option | Description | Selected |
|--------|-------------|----------|
| Питає intake | Питає те, що не виводиться з запиту; без пауз блоків і питань на розуміння | ✓ |
| Мінімум питань | Лише id, template, title | |
| Нічого не питає | Виводить усе з фрази | |

**User's choice:** Питає intake.

---

## Чекпойнти й стан

| Option | Description | Selected |
|--------|-------------|----------|
| Untracked файл | `.skill-state/<id>.json`, ignored; переживає нову сесію | ✓ |
| Лише розмовний гейт | Нічого не пишеться; після `/clear` intake губиться | |
| Комітований запис | Рішення в `task.md` або звіті | |

**User's choice:** Untracked файл.

| Option | Description | Selected |
|--------|-------------|----------|
| Мінімум + audit | Mode, intake, блоки, наступний блок, припущення, час і commit | ✓ |
| Багатий стан | Плюс diff-и, вивід команд, тайминги | |
| Лише intake | Intake і поточний блок | |

**User's choice:** Мінімум + audit.

| Option | Description | Selected |
|--------|-------------|----------|
| Пауза + перегляд | Підсумок + `[Продовжити | Переробити | Стоп]`; стан пишеться завжди | ✓ |
| Тихий запис | Стан пишеться, робота продовжується | |
| Лише code/report | Intake без окремого гейта | |

**User's choice:** Пауза + перегляд.

| Option | Description | Selected |
|--------|-------------|----------|
| Стан + звіт | Одразу в стан; блок звіту переносить у `assumptions` | ✓ |
| Лише звіт | Писати в звіт у момент конфлікту | |
| Окремий assumptions.md | Журнал у homework | |

**User's choice:** Стан + звіт.

---

## Контракт скілів

| Option | Description | Selected |
|--------|-------------|----------|
| Frontmatter + 2 файли | `metadata.version: 0.1`; `CHANGELOG.md` і `LESSONS.md` | ✓ |
| Усе в SKILL.md | Секції в кінці тіла | |
| Frontmatter + 1 файл | Один `CHANGELOG.md` на два сенси | |

**User's choice:** Frontmatter + 2 файли.

| Option | Description | Selected |
|--------|-------------|----------|
| Пропозиція + підтвердження | Датований запис + `[Записати | Не зараз]` | ✓ |
| Автодопис | Скіл дописує сам | |
| Лише при промоції | Вручну при промоції або дефекті | |

**User's choice:** Пропозиція + підтвердження.

| Option | Description | Selected |
|--------|-------------|----------|
| check_skills.py + тест | Frontmatter, версія, файли, stub-маркер, drift | |
| Лише drift | Перевіряється лише рівність дзеркала | ✓ |
| Review-only | Жодного скрипта | |

**User's choice:** Лише drift.
**Notes:** Решта контракту — review-enforced, у дусі ceremony-trim.

| Option | Description | Selected |
|--------|-------------|----------|
| metadata.status + банер | Портативне поле плюс банер у тілі | ✓ |
| Лише банер | Текст у тілі SKILL.md | |
| STUB.md замість SKILL.md | Скіл не завантажується | |

**User's choice:** metadata.status + банер.

| Option | Description | Selected |
|--------|-------------|----------|
| Мінімальний реальний | Підтвердження → upload → serial capture; решта чотири — заглушки | ✓ |
| Теж заглушка | Лише `new-homework` і `hw-build` реалізовані | |
| Повний | Flash + capture + розбір логу | |

**User's choice:** Мінімальний реальний.

| Option | Description | Selected |
|--------|-------------|----------|
| Спільний _shared | `.claude/skills/_shared/guardrails.md`; скіли посилаються | ✓ |
| Копія в кожному | Блок у кожному SKILL.md | |
| Лише AGENTS.md | Guardrails у rulebook | |

**User's choice:** Спільний _shared.

| Option | Description | Selected |
|--------|-------------|----------|
| Dry-run у temp | `new-homework` на тимчасовому root, `hw-build` на 1_3, `hw-flash` до gate | ✓ |
| Лише структура | Наявність файлів і рівність дзеркала | |
| Реальний новий homework | Справжній homework через скіл | |

**User's choice:** Dry-run у temp.

| Option | Description | Selected |
|--------|-------------|----------|
| Готовий до контексту | Записати CONTEXT.md і DISCUSSION-LOG.md | ✓ |
| Дослідити ще | Ще одна область або додаткові питання | |

**User's choice:** Готовий до контексту.

---

## Claude's Discretion

- Точні назви файлів у `references/`, форма CLI генератора, формат маніфесту, id
  pre-commit hook.
- Схема `.skill-state/<id>.json` за умови, що вона містить усі поля D-13.
- Точні формулювання меню пауз, підтверджень і повідомлень ескалації.
- Чи видаляти state-файл після фінального чекпойнта (default: видаляти після успіху,
  зберігати після abort).
- Структура записів `CHANGELOG.md` і `LESSONS.md` за умови дати й посилання на run.
- Яку заглушку підвищувати першою і точний текст stub-банера.
- Чи `course-index` читає згенерований README, `homework.yaml`, чи обидва.

## Deferred Ideas

- Trigger evals і benchmark mode (10–20 `should_trigger` prompts) — після першого
  реального використання.
- Повний `scripts/check_skills.py` — відхилено на користь drift-only; повернутись, якщо
  дефект frontmatter проскочить.
- Повний розбір serial-логу в `hw-flash` — після першого заліза.
- Промоція `hw-report`, `schematic`, `simulate`, `course-index` — після першого
  реального використання.
- Формат і перевірка `assumptions` у звіті — Phase 10.
- Реальний end-to-end `new-homework` на живому завданні — Phase 11 або сам курс.
- Окремий `assumptions.md` у homework — відхилено.
- Symlink-реле для `.agents` — відхилено.
- Спільний question bank — відхилено.
- Тюнінг описів скілів за бенчмарками — пізніше.
