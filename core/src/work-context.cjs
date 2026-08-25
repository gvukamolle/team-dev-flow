"use strict";

const crypto = require("node:crypto");

const WORK_ITEM_KINDS = new Set(["initiative", "epic", "spec", "task", "subtask", "unknown"]);
const STATUS_CATEGORIES = new Set(["backlog", "ready", "in_progress", "blocked", "done", "cancelled", "unknown"]);

function canonical(value) {
  if (Array.isArray(value)) return `[${value.map(canonical).join(",")}]`;
  if (value && typeof value === "object") {
    return `{${Object.keys(value).sort().map((key) => `${JSON.stringify(key)}:${canonical(value[key])}`).join(",")}}`;
  }
  return JSON.stringify(value);
}

function contentHash(value) {
  return crypto.createHash("sha256").update(canonical(value)).digest("hex");
}

function sourceRef(source, nativeId) {
  if (!source?.provider || !source?.instance || !nativeId) throw new Error("source provider, instance, and native id are required");
  return `${source.provider}:${source.instance}:${nativeId}`;
}

function configuredKind(issue, profile) {
  if (issue?.type?.subtask) return "subtask";
  const typeName = issue?.type?.name;
  for (const [kind, names] of Object.entries(profile?.issue_type_semantics || {})) {
    if (WORK_ITEM_KINDS.has(kind) && Array.isArray(names) && names.includes(typeName)) return kind;
  }
  return "unknown";
}

function configuredStatus(issue, profile) {
  const name = issue?.status?.name || "Unknown";
  for (const [category, names] of Object.entries(profile?.status_semantics || {})) {
    if (STATUS_CATEGORIES.has(category) && Array.isArray(names) && names.includes(name)) {
      return {name, category};
    }
  }
  return {name, category: "unknown"};
}

function normalizeWorkItem(issue, source, profile) {
  if (!issue) return null;
  const ref = sourceRef(source, issue.key);
  return {
    schema_version: "team-dev-flow/work-item/v1",
    ref,
    source: {
      provider: source.provider,
      instance: source.instance,
      native_id: issue.key,
      url: source.base_url ? `${source.base_url.replace(/\/$/, "")}/browse/${encodeURIComponent(issue.key)}` : null
    },
    kind: configuredKind(issue, profile),
    title: issue.summary || "",
    body: issue.description || "",
    status: configuredStatus(issue, profile),
    resolution: issue.resolution?.name || null,
    parent_ref: issue.parent?.key ? sourceRef(source, issue.parent.key) : null,
    labels: issue.labels || [],
    relations: (issue.links || []).flatMap((link) => {
      const entries = [];
      if (link.inward_issue?.key) entries.push({type: link.type?.name || "related", direction: "inward", target_ref: sourceRef(source, link.inward_issue.key)});
      if (link.outward_issue?.key) entries.push({type: link.type?.name || "related", direction: "outward", target_ref: sourceRef(source, link.outward_issue.key)});
      return entries;
    }),
    metadata: {
      native_type: issue.type?.name || null,
      native_status: issue.status?.name || null,
      priority: issue.priority?.name || null,
      updated: issue.updated || null
    }
  };
}

function buildWorkContext(legacyContext, source, profile) {
  const primary = normalizeWorkItem(legacyContext.issue, source, profile);
  const candidates = [legacyContext.parent, legacyContext.epic, legacyContext.initiative]
    .filter(Boolean)
    .filter((item, index, all) => item.key !== legacyContext.issue?.key && all.findIndex((other) => other.key === item.key) === index);
  const ancestors = candidates.map((item) => normalizeWorkItem(item, source, profile));
  const children = (legacyContext.issue?.subtasks || []).map((item) => ({
    ref: sourceRef(source, item.key),
    native_id: item.key,
    title: item.summary || "",
    status: item.status || null
  }));
  const updated = [legacyContext.issue, ...candidates]
    .map((item) => item?.updated)
    .filter(Boolean)
    .sort()
    .at(-1) || legacyContext.revision?.updated || null;
  const revision = {updated, content_hash: contentHash({primary, ancestors, children})};
  return {
    schema_version: "team-dev-flow/work-context/v1",
    source: {provider: source.provider, instance: source.instance},
    primary,
    ancestors,
    children,
    revision,
    capabilities: {
      acceptance_criteria: Boolean(profile?.fields?.acceptance_criteria?.id),
      risk: Boolean(profile?.fields?.risk?.id)
    },
    warnings: legacyContext.warnings || []
  };
}

module.exports = {
  buildWorkContext,
  canonical,
  configuredKind,
  configuredStatus,
  contentHash,
  normalizeWorkItem,
  sourceRef
};
