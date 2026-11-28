#!/usr/bin/env node
import fs from "node:fs";
import os from "node:os";
import path from "node:path";
import { fileURLToPath } from "node:url";

const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);
const REPO_ROOT = path.resolve(__dirname, "..");
const SKILLS_SRC = path.join(REPO_ROOT, "skills");
const STUDY_TEMPLATE = path.join(REPO_ROOT, "templates", "STUDY_PAGE_TEMPLATE.html");

const VALID_AGENTS = new Set(["claude", "cursor", "codex", "opencode", "antigravity"]);
const VALID_SCOPES = new Set(["global", "project"]);
const SKILL_NAME_RE = /^[a-z0-9]+(-[a-z0-9]+)*$/;

function printHelp() {
  console.log(`Usage: npx agent-learn-skills [options]

Options:
  -a, --agent <name>     Target agent: claude | cursor | codex | opencode | antigravity (default: claude)
  -s, --scope <scope>    Install scope: global | project (default: global)
  -t, --target <dir>     Custom destination directory (overrides --agent and --scope)
  -k, --skill <name>     Install/uninstall specific skill(s) (repeatable or comma-separated)
  -l, --list             List available skills and exit
      --symlink          Create symlinks instead of copying files
  -f, --force            Overwrite existing skills (or remove external symlinks on uninstall)
      --uninstall        Remove installed repository skills from target
  -h, --help             Show this help message`);
}

function parseArgs(argv) {
  const opts = {
    agent: "claude",
    scope: "global",
    target: "",
    skills: [],
    symlink: false,
    force: false,
    uninstall: false,
    list: false,
    help: false,
  };

  for (let i = 0; i < argv.length; i++) {
    const arg = argv[i];
    switch (arg) {
      case "-a":
      case "--agent":
        opts.agent = argv[++i] ?? "";
        break;
      case "-s":
      case "--scope":
        opts.scope = argv[++i] ?? "";
        break;
      case "-t":
      case "--target":
        opts.target = argv[++i] ?? "";
        break;
      case "-k":
      case "--skill": {
        const raw = argv[++i] ?? "";
        for (const item of raw.split(",")) {
          if (item.trim()) opts.skills.push(item.trim());
        }
        break;
      }
      case "--symlink":
        opts.symlink = true;
        break;
      case "-f":
      case "--force":
        opts.force = true;
        break;
      case "--uninstall":
        opts.uninstall = true;
        break;
      case "-l":
      case "--list":
        opts.list = true;
        break;
      case "-h":
      case "--help":
        opts.help = true;
        break;
      default:
        console.error(`Unknown option: ${arg}`);
        printHelp();
        process.exit(1);
    }
  }
  return opts;
}

function resolveTarget(opts) {
  if (opts.target) return path.resolve(opts.target);
  if (!VALID_SCOPES.has(opts.scope)) {
    console.error(`Invalid scope: '${opts.scope}' (use global or project).`);
    process.exit(1);
  }
  if (!VALID_AGENTS.has(opts.agent)) {
    console.error(`Unknown agent: '${opts.agent}'.`);
    process.exit(1);
  }
  const home = os.homedir();
  const base = opts.scope === "global" ? home : process.cwd();
  switch (opts.agent) {
    case "claude":
      return path.join(base, ".claude", "skills");
    case "cursor":
      return path.join(base, ".cursor", "skills");
    case "codex":
    case "opencode":
      return path.join(base, ".agents", "skills");
    case "antigravity":
      return opts.scope === "global"
        ? path.join(home, ".gemini", "antigravity", "skills")
        : path.join(base, ".agent", "skills");
  }
}

function listAvailableSkills() {
  return fs
    .readdirSync(SKILLS_SRC, { withFileTypes: true })
    .filter((d) => d.isDirectory() && fs.existsSync(path.join(SKILLS_SRC, d.name, "SKILL.md")))
    .map((d) => d.name)
    .sort();
}

function main() {
  const opts = parseArgs(process.argv.slice(2));
  if (opts.help) {
    printHelp();
    return;
  }

  const available = listAvailableSkills();
  if (opts.list) {
    console.log("Available skills:");
    for (const s of available) console.log(`  - ${s}`);
    return;
  }

  const selected = opts.skills.length > 0 ? opts.skills : available;
  for (const name of selected) {
    if (!SKILL_NAME_RE.test(name) || !fs.existsSync(path.join(SKILLS_SRC, name, "SKILL.md"))) {
      console.error(`ERROR: invalid or missing skill '${name}'.`);
      process.exit(1);
    }
  }

  const destDir = resolveTarget(opts);

  if (opts.uninstall) {
    let removed = 0;
    let skipped = 0;
    for (const name of selected) {
      const dst = path.join(destDir, name);
      if (!fs.existsSync(dst)) {
        skipped++;
        continue;
      }
      const stat = fs.lstatSync(dst);
      if (stat.isSymbolicLink() && !opts.force) {
        const realDst = fs.realpathSync(dst);
        const realSrc = fs.realpathSync(path.join(SKILLS_SRC, name));
        if (realDst !== realSrc) {
          console.log(`SKIPPED: ${name} (external symlink at ${dst}; use --force to remove)`);
          skipped++;
          continue;
        }
      }
      fs.rmSync(dst, { recursive: true, force: true });
      console.log(`REMOVED: ${name} <- ${dst}`);
      removed++;
    }
    console.log(`Done: ${removed} removed, ${skipped} skipped in ${destDir}`);
    return;
  }

  fs.mkdirSync(destDir, { recursive: true });
  let installed = 0;
  let skipped = 0;

  for (const name of selected) {
    const src = path.join(SKILLS_SRC, name);
    const dst = path.join(destDir, name);

    if (fs.existsSync(dst)) {
      if (opts.force) {
        fs.rmSync(dst, { recursive: true, force: true });
      } else {
        console.log(`SKIPPED: ${name} (already exists at ${dst}; use --force to replace)`);
        skipped++;
        continue;
      }
    }

    if (opts.symlink) {
      fs.symlinkSync(src, dst, process.platform === "win32" ? "junction" : "dir");
    } else {
      fs.cpSync(src, dst, { recursive: true });
      if (fs.existsSync(STUDY_TEMPLATE)) {
        const assetsDir = path.join(dst, "assets");
        fs.mkdirSync(assetsDir, { recursive: true });
        fs.copyFileSync(STUDY_TEMPLATE, path.join(assetsDir, "STUDY_PAGE_TEMPLATE.html"));
      }
    }

    console.log(`INSTALLED (${opts.symlink ? "symlink" : "copy"}): ${name} -> ${dst}`);
    installed++;
  }

  console.log(`Done: ${installed} installed, ${skipped} skipped in ${destDir}`);
}

main();
