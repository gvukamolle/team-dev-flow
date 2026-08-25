"use strict";

function nextSddStage(state = {}) {
  if (!state.captured) return "capture";
  if (state.blocking_questions) return "clarify";
  if (state.decision_uncertainty) return "research";
  if (!state.spec_ready) return "specify";
  if (!state.plan_ready) return "plan";
  if (!state.tasks_ready) return "tasks";
  if (!state.implemented) return "implement";
  if (!state.verified) return "verify";
  if (!state.reviewed) return "review";
  return "converge";
}

function converge(gaps = []) {
  if (!Array.isArray(gaps)) throw new Error("convergence gaps must be an array");
  const malformed = gaps.find((gap) => !gap || !String(gap.title || "").trim());
  if (malformed) throw new Error("every convergence gap requires a concrete Task title");
  const concrete = gaps.map((gap, index) => ({
    ref: gap.ref || `draft:converge-${index + 1}`,
    title: String(gap.title).trim(),
    kind: gap.kind || "implementation",
    acceptance_refs: gap.acceptance_refs || [],
    evidence: gap.evidence || ""
  }));
  if (concrete.length === 0) return {result: "CONVERGED", tasks: []};
  return {result: "TASKS_REQUIRED", tasks: concrete};
}

module.exports = {converge, nextSddStage};
