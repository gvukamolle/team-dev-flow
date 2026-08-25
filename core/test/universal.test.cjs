const test = require("node:test");
const assert = require("node:assert/strict");
const fs = require("node:fs");
const path = require("node:path");

const capabilities = require("../src/capabilities.cjs");
const sdd = require("../src/sdd-flow.cjs");

const root = path.resolve(__dirname, "../..");

test("generic profile resolves only declared provider-neutral capabilities", () => {
  const profile = JSON.parse(fs.readFileSync(path.join(root, "profiles/flow/generic.json"), "utf8"));
  const manifests = fs.readdirSync(path.join(root, "profiles/providers"))
    .filter((name) => name.endsWith(".json"))
    .map((name) => JSON.parse(fs.readFileSync(path.join(root, "profiles/providers", name), "utf8")));
  const result = capabilities.discoverCapabilities(profile, manifests);
  assert.equal(result.profile, "generic");
  assert.equal(result.selected_adapters.includes("codex"), true);
  assert.equal(result.selected_adapters.includes("git-local"), true);
});

test("SDD converge returns confirmation or concrete remaining tasks", () => {
  const complete = sdd.converge([]);
  assert.equal(complete.result, "CONVERGED");
  const incomplete = sdd.converge([{ref: "local:FLOW/TASK-2", title: "Add evidence", acceptance_refs: ["AC-1"]}]);
  assert.equal(incomplete.result, "TASKS_REQUIRED");
  assert.equal(incomplete.tasks.length, 1);
});
