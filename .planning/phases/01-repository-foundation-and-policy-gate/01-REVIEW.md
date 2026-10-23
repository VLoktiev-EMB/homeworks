---
phase: 01-repository-foundation-and-policy-gate
reviewed: 2026-10-23T17:27:00Z
depth: standard
files_reviewed: 38
files_reviewed_list:
  - .claude/CLAUDE.md
  - .gitattributes
  - .github/PULL_REQUEST_TEMPLATE/docs.md
  - .github/PULL_REQUEST_TEMPLATE/homework.md
  - .github/PULL_REQUEST_TEMPLATE/infra.md
  - .github/workflows/security.yml
  - .gitignore
  - .pre-commit-config.yaml
  - AGENTS.md
  - LICENSE
  - LICENSES/CC-BY-4.0.txt
  - LICENSES/MIT.txt
  - NOTICE
  - README.md
  - REUSE.toml
  - docs/decisions/0001-monorepo-with-independent-projects.md
  - docs/decisions/0002-ports-and-adapters-no-universal-hal.md
  - docs/decisions/0003-git-policy-and-protected-main.md
  - docs/decisions/0004-license-and-attribution.md
  - docs/decisions/0005-asset-and-lfs-policy.md
  - docs/decisions/README.md
  - docs/decisions/template.md
  - policy/repository.json
  - policy/ruleset-main.json
  - scripts/check_policy.py
  - scripts/check_pr_templates.py
  - scripts/tag_homework.sh
  - scripts/tests/__init__.py
  - scripts/tests/fixtures/ruleset-live.json
  - scripts/tests/test_adrs.py
  - scripts/tests/test_agents_md.py
  - scripts/tests/test_check_policy.py
  - scripts/tests/test_check_pr_templates.py
  - scripts/tests/test_gitignore.py
  - scripts/tests/test_homework_id.py
  - scripts/tests/test_license_hygiene.py
  - scripts/tests/test_security_workflow.py
  - scripts/tests/test_tag_homework.py
findings:
  critical: 0
  warning: 6
  info: 7
  total: 13
status: issues_found
---

# Phase 01: Code Review Report

**Reviewed:** 2026-10-23T17:27:00Z
**Depth:** standard
**Files Reviewed:** 38
**Status:** issues_found

## Summary

Переглянуто весь приріст фази 01 (48 комітів після `ccf4224`): два Python-чекери,
bash-скрипт тегування, полісі-як-код, secret-gate, ліцензійну декларацію, ADR,
PR-шаблони, rulebook і тестовий набір. Перевірку зроблено не лише читанням: тестовий
набір виконано (99 тестів, OK), `reuse lint`/`reuse spdx` прогнано для перевірки
фактичного ліцензійного розподілу, `gitleaks git --redact --verbose --log-opts="--all"`
виконано на реальній історії (no leaks found), а два підозрювані дефекти підтверджено
цілеспрямованими експериментами в тимчасових git-репозиторіях.

Загальна оцінка: ядро політики коректне і fail-closed. `check_policy.py` виявляє дрейф у
всіх перевірених напрямках (відсутнє правило, зайве правило, вимкнене enforcement,
розширені conditions), а проєкція не пропускає відсутні в live поля. Однак два guard-и
мають реальні fail-open прогалини: чекер PR-шаблонів не бачить усіх шляхів, які GitHub
використовує для default-шаблону, а `tag_homework.sh` перевіряє наявність homework у
робочому дереві, але тегує зовсім інший коміт. Крім того, частина тегів
`[ENFORCED: ...]` у AGENTS.md заявляє механізми, яких у репозиторії немає.

Критичних (BLOCKER) дефектів не знайдено.

## Warnings

### WR-01: Чекер PR-шаблонів не виявляє default-шаблон у root `PULL_REQUEST_TEMPLATE/`

**File:** `scripts/check_pr_templates.py:40-49`, `scripts/check_pr_templates.py:182-191`
**Issue:** `DEFAULT_TEMPLATE_PATHS` перелічує вісім шляхів, але GitHub підтримує
`PULL_REQUEST_TEMPLATE/` як у `.github/`, так і в корені репозиторію та в `docs/`, і
використовує файл `default.md` з цієї теки як типовий шаблон. Шляхи
`PULL_REQUEST_TEMPLATE/default.md` і `docs/PULL_REQUEST_TEMPLATE/default.md` (а також
будь-яке інше написання, якщо файлова система CI регістрозалежна) не перевіряються.
Перевірено експериментально: у тимчасовому дереві з копією трьох шаблонів і доданим
`PULL_REQUEST_TEMPLATE/default.md` у корені скрипт вивів
`PASS default-template: no default PR template at any fallback path` і завершився з
кодом 0. Тобто інваріант «chooser cannot be suppressed» (заявлений у 01-05-SUMMARY)
фактично не виконується: контриб'ютор може додати дефолтний шаблон і чекер цього не
помітить, а GitHub мовчки перестане показувати вибір шаблону.
**Fix:** перелічити всі задокументовані локації, а не вибіркові, і порівнювати імена без
урахування регістру; краще — сканувати три підтримувані теки, а не фіксований список:

```python
SUPPORTED_DIRS = ("", "docs", ".github")
for base in SUPPORTED_DIRS:
    directory = root / base / "PULL_REQUEST_TEMPLATE"
    if directory.is_dir():
        for child in directory.iterdir():
            if child.name.lower() == "default.md":
                present.append(child.relative_to(root).as_posix())
```

та додати відповідні негативні фікстури до `test_stray_default_template_exits_1`.

### WR-02: `tag_homework.sh` перевіряє homework у робочому дереві, але тегує `origin/<default>`

**File:** `scripts/tag_homework.sh:104-110`, `scripts/tag_homework.sh:161-180`
**Issue:** Прекондиція 2 перевіряє `-d "$REPO_ROOT/homeworks/$id"`, тобто *поточне робоче
дерево* (можливо, гілку `hw/<id>`), а тег створюється на `refs/remotes/origin/$DEFAULT_BRANCH`.
Це різні коміти. Перевірено експериментально: у тимчасовому репозиторії `origin/main` не
містить `homeworks/9_9-ghost-homework`, гілка `hw/9_9-ghost-homework` містить; скрипт
вивів `PASS homework: ... exists`, створив і запушив тег, і
`git cat-file -e hw/9_9-ghost-homework:homeworks/9_9-ghost-homework/README.md` завершився
невдачею. У реальному режимі це частково прикриває перевірка merged-PR, але вона не
вимагає, щоб PR було змерджено саме в default branch, тому тег може вказати на коміт без
homework. Оскільки тег — публічний і незмінний артефакт (ADR-0003), помилка стає
постійним хибним посиланням.
**Fix:** після обчислення `base` перевіряти вміст саме цього коміту і вимагати, щоб
merged PR мав базою default branch:

```bash
if ! git -C "$REPO_ROOT" cat-file -e "$base:homeworks/$id"; then
  echo "FAIL homework: homeworks/$id is absent from $DEFAULT_BRANCH ($base)" >&2
  exit 1
fi
```

і додати `--base "$DEFAULT_BRANCH"` до `gh pr list` (після того, як default branch
визначено; порядок прекондицій доведеться переставити).

### WR-03: `[ENFORCED: pre-commit]` для generated files не має жодного enforcement-механізму

**File:** `AGENTS.md:153-155`
**Issue:** Правило «Generated files are never committed: `compile_commands.json`, `site/`,
`.pio/`» позначене `[MUST] [ENFORCED: pre-commit]`, але `.pre-commit-config.yaml`
містить лише gitleaks, trailing-whitespace, end-of-file-fixer, check-merge-conflict і
check-added-large-files. Ніщо з цього не перевіряє відслідковані шляхи; `.gitignore`
запобігає лише випадковому `git add .`, а `git add -f compile_commands.json` пройде всі
хуки. Rulebook — канонічний артефакт фази, і його enforcement-теги за визначенням
машиночитні та перевірювані, тому хибний тег гірший за його відсутність.
**Fix:** або змінити тег на `[ENFORCED: review]`, або додати реальний хук, наприклад
локальний `repo: local` з `entry: bash -c 'git ls-files -ci --exclude-standard
compile_commands.json site .pio | grep . && exit 1 || exit 0'`.

### WR-04: `[ENFORCED: CI]` для ліцензійного розподілу до Phase 8

**File:** `AGENTS.md:159-161`
**Issue:** Правило про MIT/CC-BY-4.0 має тег `[ENFORCED: CI]`, хоча в тому ж реченні
сказано, що `reuse lint` «joins the pull-request pipeline in Phase 8», а єдиний workflow
у репозиторії — `security.yml` (gitleaks). Сьогодні ліцензійний розподіл не перевіряє
жоден CI-джоб, отже тег описує майбутній, а не поточний стан.
**Fix:** до Phase 8 поставити `[ENFORCED: review]`, або додати job `reuse lint` у
`security.yml` і тим зробити тег правдивим. Те саме стосується формулювання в
рядках 84-87: `check_policy.py --check` сьогодні не входить до CI, його запускає лише
людина/агент.

### WR-05: gitleaks-бінарник у CI виконується без перевірки цілісності

**File:** `.github/workflows/security.yml:17-28`
**Issue:** `curl -sSfL .../gitleaks_8.30.1_linux_x64.tar.gz | tar -xz` завантажує і
негайно розпаковує архів, після чого бінарник встановлюється в `/usr/local/bin` і
запускається. Немає ні SHA-256, ні підпису, ні `--proto '=https'`; скомпрометований
release-артефакт або підміна на рівні CDN виконується з правами CI-джоба. Pinned версія
обмежує поверхню, але не доводить цілісність. Додатково `actions/checkout@v7` — рухомий
major-тег, а не незмінний SHA.
**Fix:** зафіксувати digest і перевіряти його перед розпакуванням, а `checkout` пінити
на commit SHA:

```yaml
echo "<sha256>  $RUNNER_TEMP/gitleaks.tar.gz" | sha256sum -c -
```

### WR-06: `READ_ONLY` не застосовується, а тест «strips read-only keys» не може провалитися

**File:** `scripts/check_policy.py:36-48`, `scripts/tests/test_check_policy.py:87-96`
**Issue:** Константа `READ_ONLY` ніде не використовується: `project()` будує результат,
ітеруючи лише ключі `desired`, тому server-side поля не можуть потрапити в проєкцію
незалежно від вмісту `READ_ONLY`. Відповідний тест перевіряє
`assertNotIn(key, projected)` для ключів, яких у `committed_ruleset()` немає, отже
перевірка істинна за побудовою — навіть якщо `READ_ONLY` видалити або зламати. Це
мертвий код плюс тест, що створює хибну впевненість у перевірці server-полів.
**Fix:** або видалити `READ_ONLY` і відповідну перевірку, або зробити її справжньою:
явно відкидати read-only ключі з live-тіла перед проєкцією та тестувати на синтетичному
`live`, що *містить* ці ключі, а також перевіряти, що сама `policy/` не містить
read-only полів (це запобігатиме невдалому `--apply`).

## Info

### IN-01: Успішний шлях `tag_homework.sh` не покритий тестами

**File:** `scripts/tests/test_tag_homework.py:97-180`
**Issue:** Усі чотири тести завершуються до створення тега (`TAG_HOMEWORK_SKIP_REMOTE=1`
плюс відсутність `origin` у фікстурі). Гілка `git fetch` → `resolve_default_branch` →
`git tag` → `git push` не виконується жодного разу; 01-08-SUMMARY це визнає. Саме там
живе дефект WR-02 і залежність від `origin/HEAD`.
**Fix:** додати фікстуру з локальним bare-remote (`git init --bare`), кількома комітами і
перевіркою, що тег створено на `origin/main` та запушено рівно один раз.

### IN-02: `section_order` може пропустити відсутню MADR-секцію

**File:** `scripts/tests/test_adrs.py:112-115`, `scripts/tests/test_adrs.py:216-225`
**Issue:** `lines.index(heading)` бере перше входження, а перевірка обмежується
`len(indices) == len(MADR_SECTIONS)`. Якщо один заголовок продубльовано, а інший
відсутній, кількість збігається і тест проходить.
**Fix:** перевіряти унікальність кожного заголовка (`text.count(heading) == 1`) і
порівнювати позиції, обчислені за єдиним проходом.

### IN-03: Перевірка «no configured git identity» може хибно падати

**File:** `scripts/tests/test_license_hygiene.py:198-210`
**Issue:** `assertNotIn(value, text)` для `git config user.name` спрацює на будь-якому
короткому імені (наприклад `A` або `MIT`), яке трапляється в тексті `LICENSE`/`NOTICE`.
Канонічна команда `python3 -m unittest discover -s scripts/tests` тоді падає з причини,
не пов'язаної з витоком PII.
**Fix:** перевіряти лише `user.email` (він унікальний) або вимагати мінімальну довжину
значення / збіг цілого слова з межами.

### IN-04: Hook `language: golang` тягне незафіксований Go toolchain

**File:** `.pre-commit-config.yaml:5-8`
**Issue:** Upstream-визначення gitleaks має `language: golang`; якщо `go` немає в `PATH`,
pre-commit завантажує *останню* версію Go з `go.dev`/`dl.google.com` під час
встановлення хука. Це суперечить зафіксованому toolchain-курсу (PlatformIO/espressif32/
clang-format) і робить перший `pre-commit run` залежним від мережі та пливучим у часі.
**Fix:** або задокументувати це як відому властивість, або використати
`id: gitleaks-system` з уже встановленим бінарником 8.30.1 (brew/CI), або `language:
docker_image`.

### IN-05: «Next number: 0006 (reserved …)» суперечить правилу нумерації

**File:** `docs/decisions/README.md:10-16`, `docs/decisions/README.md:30`
**Issue:** Індекс стверджує, що номери присвоюються послідовно *на момент прийняття* і що
наступний номер — «highest existing + 1», але потім «резервує» 0006 за рішенням Phase 2.
Резервування не передбачене правилами і створює конфлікт, якщо Phase 2 прийме інше
рішення першим.
**Fix:** замінити на «Next free number: 0006».

### IN-06: Клас ASCII-символів ширший за шаблон ID

**File:** `AGENTS.md:100-107`
**Issue:** Правило ID — `^[0-9]+_[0-9]+-[a-z0-9-]+$`, а наступне правило дозволяє для
«IDs and paths» клас `[a-z0-9_.-]`. ID `1_3-a.b` задовольняє ASCII-правило, але не
задовольняє шаблон ID; читач, який реалізує обидва правила, отримає різні результати.
**Fix:** розділити: ID — точний regex, шляхи — `[a-z0-9_.-]`.

### IN-07: Проєкція `--check` не бачить полів, яких немає в committed-файлі

**File:** `scripts/check_policy.py:144-162`, `docs/decisions/0003-git-policy-and-protected-main.md:122-127`
**Issue:** Перевірено: якщо live `require_extra_approval_for_unattributed_changes`
змінити з `true` на `false`, `--check` усе одно повертає 0, бо поле не оголошене в
`policy/ruleset-main.json`. ADR-0003 це прямо документує як неперевірене припущення, тому
це не дефект реалізації, але це справжня fail-open прогалина drift-чекера: послаблення
захисту, зроблене поза оголошеним підмножиною, не детектується.
**Fix:** після першого `--apply` зафіксувати фактичні значення
`require_extra_approval_for_unattributed_changes`, `required_reviewers` і
`dismissal_restriction` у committed-файлі (або явно їх забороняти), щоб `--check`
порівнював і їх.

---

_Reviewed: 2026-10-23T17:27:00Z_
_Reviewer: Claude (gsd-code-reviewer)_
_Depth: standard_
