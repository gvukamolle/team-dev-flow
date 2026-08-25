"use strict";

const TERMINAL = new Set(["done", "cancelled"]);
const STAGES = new Set(["discovery", "specifying", "planning", "implementing", "verifying", "reviewing", "done"]);

function projectParentProgress(children = [], stage = "discovery") {
  if (!STAGES.has(stage)) throw new Error(`unsupported delivery stage: ${stage}`);
  const required = children.filter((child) => child.required !== false);
  const completed = required.filter((child) => TERMINAL.has(child.status)).length;
  const active = required.some((child) => ["active", "blocked", "done", "cancelled"].includes(child.status));
  const allCancelled = required.length > 0 && required.every((child) => child.status === "cancelled");
  let status = "backlog";
  if (required.length > 0 && completed === required.length) status = allCancelled ? "cancelled" : "done";
  else if (active) status = "in_progress";

  let health = "unknown";
  if (required.some((child) => child.status === "blocked" || child.blocked === true)) health = "blocked";
  else if (required.some((child) => child.overdue === true || child.at_risk === true)) health = "at_risk";
  else if (required.length > 0) health = "on_track";

  return {
    schema_version: "team-dev-flow/parent-progress/v1",
    status,
    health,
    stage: status === "done" ? "done" : stage,
    completed_required: completed,
    total_required: required.length,
    percent: required.length === 0 ? 0 : Math.round((completed / required.length) * 100)
  };
}

module.exports = {projectParentProgress};
