"use strict";

const VALID_KINDS = new Set(["agent_host", "task_store", "git_provider"]);
const VALID_MODES = new Set(["read", "preview", "write"]);

function capabilityKey(kind, name, mode) {
  return `${kind}:${name}:${mode}`;
}

function indexCapabilities(manifests = []) {
  const available = new Map();
  const warnings = [];
  for (const manifest of manifests) {
    const kind = manifest?.adapter_kind;
    if (!VALID_KINDS.has(kind)) {
      warnings.push(`ignored manifest with unsupported adapter_kind: ${String(kind)}`);
      continue;
    }
    if (!["supported", "experimental"].includes(manifest.status)) {
      continue;
    }
    for (const capability of manifest.capabilities || []) {
      if (!VALID_MODES.has(capability.mode)) {
        warnings.push(`ignored ${manifest.id} capability with unsupported mode: ${String(capability.mode)}`);
        continue;
      }
      const key = capabilityKey(kind, capability.name, capability.mode);
      if (capability.enabled) available.set(key, {manifest_id: manifest.id, ...capability});
    }
  }
  return {available, warnings};
}

function discoverCapabilities(profile, manifests = []) {
  const selectedIds = new Set(Object.values(profile?.adapters || {}).filter(Boolean));
  const selectedManifests = manifests.filter((manifest) => selectedIds.has(manifest?.id));
  const indexed = indexCapabilities(selectedManifests);
  const operations = {};
  for (const [operation, config] of Object.entries(profile?.operations || {})) {
    const required = config.requires || [];
    const missing = required.filter((key) => !indexed.available.has(key));
    operations[operation] = {available: missing.length === 0, required, missing};
  }
  return {
    schema_version: "team-dev-flow/capability-discovery/v1",
    profile: profile?.id || null,
    operations,
    warnings: indexed.warnings,
    selected_adapters: [...selectedIds].sort()
  };
}

function requireOperation(discovery, operation) {
  const result = discovery?.operations?.[operation];
  if (!result) throw new Error(`operation is not declared by the active FlowProfile: ${operation}`);
  if (!result.available) throw new Error(`missing required capabilities for ${operation}: ${result.missing.join(", ")}`);
  return result;
}

module.exports = {capabilityKey, discoverCapabilities, indexCapabilities, requireOperation};
