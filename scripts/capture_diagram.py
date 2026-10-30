#!/usr/bin/env python3
"""Capture visual Wokwi canvas screenshot from assets/diagram.json via Playwright.

Usage:
  python3 scripts/capture_diagram.py homeworks/<id>
  python3 scripts/capture_diagram.py --all
"""

from __future__ import annotations

import argparse
import json
import os
import shutil
import subprocess
import tempfile
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]


def get_board_url(diagram: dict) -> str:
    """Determine the best new project template URL on wokwi.com for the board type."""
    for part in diagram.get("parts", []):
        ptype = part.get("type", "")
        if "s3" in ptype.lower():
            return "https://wokwi.com/projects/new/esp32-s3"
        if "esp32" in ptype.lower():
            return "https://wokwi.com/projects/new/esp32"
        if "pi-pico" in ptype.lower() or "rp2040" in ptype.lower():
            return "https://wokwi.com/projects/new/pi-pico"
        if "arduino-uno" in ptype.lower():
            return "https://wokwi.com/projects/new/arduino-uno"
        if "arduino-nano" in ptype.lower():
            return "https://wokwi.com/projects/new/arduino-nano"
    return "https://wokwi.com/projects/new/esp32-s3"


def find_node_path() -> str:
    """Find the global node_modules path containing playwright-core."""
    candidates = []
    npm_cmd = shutil.which("npm")
    if npm_cmd:
        try:
            res = subprocess.run(
                [npm_cmd, "root", "-g"],
                check=True,
                capture_output=True,
                text=True,
            )
            g_root = res.stdout.strip()
            candidates.append(f"{g_root}/@playwright/cli/node_modules")
            candidates.append(g_root)
        except Exception:
            pass

    existing_node_path = os.environ.get("NODE_PATH", "")
    if existing_node_path:
        candidates.append(existing_node_path)

    return ":".join(candidates)


def capture_diagram_for_homework(homework_dir: Path) -> Path:
    """Load homework diagram.json into Wokwi in browser and save screenshot."""
    diagram_path = homework_dir / "assets" / "diagram.json"
    output_path = homework_dir / "assets" / "wiring.png"

    if not diagram_path.is_file():
        raise FileNotFoundError(f"Diagram file not found: {diagram_path}")

    node_cmd = shutil.which("node")
    if not node_cmd:
        raise RuntimeError("Node.js is required on PATH to capture Wokwi diagram.")

    diagram_content = diagram_path.read_text(encoding="utf-8")
    diagram = json.loads(diagram_content)
    target_url = get_board_url(diagram)

    print(f"[{homework_dir.name}] Capturing Wokwi canvas in high resolution (Retina 2x)...")

    # Node.js script using playwright-core for headless high-DPI capture with tight clipping
    js_script = f"""const pw = require("playwright-core");

(async () => {{
    const diagram = {json.dumps(diagram)};
    const browser = await pw.chromium.launch({{
        channel: "chrome",
        headless: true
    }});
    const context = await browser.newContext({{
        viewport: {{ width: 1600, height: 1000 }},
        deviceScaleFactor: 2,
        colorScheme: "dark"
    }});
    const page = await context.newPage();

    await page.goto("{target_url}", {{ waitUntil: "domcontentloaded" }});
    await page.waitForSelector('button:has-text("diagram.json")', {{ timeout: 25000 }});

    // Dark mode check and activation
    const darkBtn = await page.$('button[aria-label="toggle dark mode"]');
    const isDark = await page.evaluate(() => {{
        const bg = window.getComputedStyle(document.body).backgroundColor;
        return bg.includes("rgb(51") || bg.includes("rgb(34") || bg.includes("rgb(18");
    }});
    if (!isDark && darkBtn) {{
        await darkBtn.click();
        await page.waitForTimeout(400);
    }}

    // Mount diagram.json Monaco model
    await page.click('button:has-text("diagram.json")');
    await page.waitForFunction(
        () => window.monaco && window.monaco.editor.getModels().some(
            m => m.uri.toString().includes("diagram.json")
        ),
        {{ timeout: 10000 }}
    );

    // Inject diagram JSON
    await page.evaluate((content) => {{
        const model = window.monaco.editor.getModels().find(
            m => m.uri.toString().includes("diagram.json")
        );
        if (model) {{
            model.setValue(content);
        }}
    }}, JSON.stringify(diagram));

    // Wait for viewer canvas and rendered parts
    await page.waitForSelector('div[class*="viewer"]', {{ timeout: 15000 }});
    await page.waitForTimeout(1000);

    // Fit diagram into viewport
    const zoomBtn = await page.$('button[aria-label="Zoom, grid, and more"]');
    if (zoomBtn) {{
        await zoomBtn.click();
        await page.waitForSelector('[role="menuitem"]:has-text("Fit")', {{ timeout: 5000 }});
        const fitBtn = await page.$('[role="menuitem"]:has-text("Fit")');
        if (fitBtn) {{
            await fitBtn.click();
            await page.waitForTimeout(400);
        }}
        await page.keyboard.press("Escape");
        await page.waitForTimeout(200);
        await page.keyboard.press("Escape");
    }}

    // Deselect any selected component
    const viewerBox = await page.$eval('div[class*="viewer"]', el => {{
        const rect = el.getBoundingClientRect();
        return {{ x: rect.left + 50, y: rect.top + 50 }};
    }});
    await page.mouse.click(viewerBox.x, viewerBox.y);

    // Hide UI FAB buttons
    await page.evaluate(() => {{
        document.querySelectorAll("button.MuiFab-root").forEach(b => {{
            b.style.display = "none";
        }});
    }});
    await page.waitForTimeout(300);

    // Compute tight bounding box of all circuit elements
    const clip = await page.evaluate(() => {{
        const elements = Array.from(
            document.querySelectorAll(
                '[class*="diagram-part_diagramItem"], div[class*="viewer"] svg path'
            )
        );
        if (elements.length === 0) return null;
        let minX = Infinity, minY = Infinity, maxX = -Infinity, maxY = -Infinity;
        for (const el of elements) {{
            const rect = el.getBoundingClientRect();
            if (rect.width > 0 && rect.height > 0) {{
                minX = Math.min(minX, rect.left);
                minY = Math.min(minY, rect.top);
                maxX = Math.max(maxX, rect.right);
                maxY = Math.max(maxY, rect.bottom);
            }}
        }}
        const padding = 28;
        return {{
            x: Math.max(0, Math.floor(minX - padding)),
            y: Math.max(0, Math.floor(minY - padding)),
            width: Math.ceil((maxX - minX) + padding * 2),
            height: Math.ceil((maxY - minY) + padding * 2)
        }};
    }});

    if (clip) {{
        await page.screenshot({{ path: "{output_path.resolve()}", clip }});
    }} else {{
        const viewer = await page.$('div[class*="viewer"]');
        if (viewer) {{
            await viewer.screenshot({{ path: "{output_path.resolve()}" }});
        }}
    }}

    await browser.close();
}})();
"""

    env = dict(os.environ)
    env["NODE_PATH"] = find_node_path()

    with tempfile.NamedTemporaryFile("w+", suffix=".js", delete=False, encoding="utf-8") as tmp:
        tmp.write(js_script)
        tmp_path = Path(tmp.name)

    try:
        subprocess.run(
            [node_cmd, str(tmp_path)],
            env=env,
            check=True,
            capture_output=True,
            text=True,
        )
    except subprocess.CalledProcessError as exc:
        print(f"Error output from node: {exc.stderr}")
        raise
    finally:
        tmp_path.unlink(missing_ok=True)

    if not output_path.is_file():
        raise RuntimeError(f"Failed to generate {output_path}")

    size_kb = output_path.stat().st_size / 1024
    print(f"[{homework_dir.name}] Successfully saved {output_path} ({size_kb:.1f} kB)")
    return output_path


def main() -> None:
    parser = argparse.ArgumentParser(description="Capture visual Wokwi wiring screenshot.")
    parser.add_argument(
        "homework", nargs="?", help="Homework path (e.g. homeworks/1_3-police-flasher)"
    )
    parser.add_argument(
        "--all", action="store_true", help="Capture for all homeworks with diagram"
    )
    args = parser.parse_args()

    if args.all:
        for d in sorted((REPO_ROOT / "homeworks").iterdir()):
            if d.is_dir() and (d / "assets" / "diagram.json").is_file():
                capture_diagram_for_homework(d)
        return

    if not args.homework:
        parser.error("Specify homework path or --all")

    target = Path(args.homework)
    if not target.is_absolute():
        target = REPO_ROOT / target
    capture_diagram_for_homework(target)


if __name__ == "__main__":
    main()
