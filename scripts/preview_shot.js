/* Headless screenshots of the local site for design review.
 * Usage: node scripts/preview_shot.js
 */
const BUNDLED_MODULES =
  "C:/Users/Administrator/.cache/codex-runtimes/codex-primary-runtime/dependencies/node/node_modules";

function loadPlaywright() {
  try {
    return require("playwright");
  } catch (error) {
    return require(BUNDLED_MODULES + "/playwright");
  }
}

const { chromium } = loadPlaywright();
const { pathToFileURL } = require("url");
const path = require("path");
const fs = require("fs");

const ROOT = path.resolve(__dirname, "..");
const OUT = path.join(ROOT, ".review");
const EDGE = "C:\\Program Files (x86)\\Microsoft\\Edge\\Application\\msedge.exe";
const URL = pathToFileURL(path.join(ROOT, "index.html")).href;

async function settle(page) {
  await page.waitForTimeout(500);
  await page.evaluate(() => {
    window.scrollTo(0, 0);
  });
  await page.waitForLoadState("load");
  await page.waitForTimeout(1800);
}

async function main() {
  fs.mkdirSync(OUT, { recursive: true });
  const browser = await chromium.launch({ executablePath: EDGE, headless: true });

  const shots = [
    { name: "shot-hero-1440", width: 1440, height: 900, scroll: 0 },
    { name: "shot-hero-1920", width: 1920, height: 1080, scroll: 0 },
    { name: "shot-work-1440", width: 1440, height: 900, anchor: "#work" },
    { name: "shot-about-1440", width: 1440, height: 900, anchor: "#about" },
    { name: "shot-mobile-hero", width: 390, height: 844, scroll: 0 },
    { name: "shot-mobile-work", width: 390, height: 844, anchor: "#work" },
  ];

  for (const shot of shots) {
    const page = await browser.newPage({
      viewport: { width: shot.width, height: shot.height },
      deviceScaleFactor: 1,
    });
    const errors = [];
    page.on("pageerror", (error) => errors.push(String(error)));
    page.on("console", (message) => {
      if (message.type() === "error") {
        errors.push("console: " + message.text());
      }
    });
    await page.goto(URL, { waitUntil: "load" });
    await settle(page);
    if (shot.anchor) {
      await page.evaluate((selector) => {
        document.querySelector(selector).scrollIntoView();
      }, shot.anchor);
      await page.waitForTimeout(2200);
    }
    await page.screenshot({ path: path.join(OUT, shot.name + ".png") });
    console.log("captured", shot.name, errors.length ? errors.join(" | ") : "no page errors");
    await page.close();
  }

  await browser.close();
}

main().catch((error) => {
  console.error(error);
  process.exit(1);
});
