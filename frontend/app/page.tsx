'use client';

import { FormEvent, useState } from 'react';
import {
  AlertCircle,
  Bot,
  CheckCircle2,
  ClipboardCheck,
  Code2,
  FileCode2,
  GitBranch,
  Hash,
  Loader2,
  Play,
  Search,
  ShieldCheck,
  Terminal,
} from 'lucide-react';

type Operation = {
  file_path: string;
  line_number?: number;
  search?: string;
  replacement: string;
};

type AuditCandidate = {
  file_path: string;
  line_number: number;
  search: string;
  replacement: string;
  description: string;
};

type AuditResult = {
  repository_path: string;
  bug_description: string;
  candidates: AuditCandidate[];
  total_found: number;
};

type Run = {
  run_id: string;
  status: string;
  repository_summary: string;
  affected_files: string[];
  root_cause: string;
  proposed_fix: string;
  patch_preview: string;
  pull_request_summary: string;
  llm_mode: string;
  candidate_operations: Operation[];
  journey: { agent: string; status: string; summary: string }[];
  validation: EvidenceData;
  regression: EvidenceData;
};

type EvidenceData = { passed: boolean; output: string; command: string; isolation: string };

const API = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';

const EXAMPLE_OPERATION = [
  {
    file_path: 'analytics.py',
    line_number: 3,
    search: '    return (conversions / total_visitors) * 100.0',
    replacement:
      '    if total_visitors == 0:\n        return 0.0\n    return (conversions / total_visitors) * 100.0',
  },
];

type Mode = 'analyze' | 'audit';

export default function Home() {
  const [mode, setMode] = useState<Mode>('analyze');

  // ── Analyze state ──────────────────────────────────────────────────────────
  const [repositoryPath, setRepositoryPath] = useState('');
  const [bugDescription, setBugDescription] = useState('');
  const [testCommand, setTestCommand] = useState('pytest');
  const [candidateOperations, setCandidateOperations] = useState('[]');
  const [run, setRun] = useState<Run | null>(null);
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(false);
  const [approvalConfirmed, setApprovalConfirmed] = useState(false);
  const [applyMessage, setApplyMessage] = useState('');

  // ── Audit state ────────────────────────────────────────────────────────────
  const [auditRepoPath, setAuditRepoPath] = useState('');
  const [auditBugDescription, setAuditBugDescription] = useState('');
  const [auditResult, setAuditResult] = useState<AuditResult | null>(null);
  const [auditError, setAuditError] = useState('');
  const [auditLoading, setAuditLoading] = useState(false);

  // ── Analyze submit ─────────────────────────────────────────────────────────
  async function submit(event: FormEvent) {
    event.preventDefault();
    setLoading(true);
    setError('');
    setRun(null);
    try {
      const operations = JSON.parse(candidateOperations);
      if (!Array.isArray(operations)) throw new Error('Candidate edits must be a JSON array.');
      const response = await fetch(`${API}/api/v1/fixes/analyze`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          repository_path: repositoryPath,
          bug_description: bugDescription,
          test_command: testCommand,
          candidate_operations: operations,
        }),
      });
      const payload = await response.json();
      if (!response.ok) throw new Error(payload.detail || 'The analysis request failed.');
      setRun(payload);
    } catch (caught) {
      setError(caught instanceof Error ? caught.message : 'Unable to connect to the backend.');
    } finally {
      setLoading(false);
    }
  }

  // ── Audit submit ───────────────────────────────────────────────────────────
  async function submitAudit(event: FormEvent) {
    event.preventDefault();
    setAuditLoading(true);
    setAuditError('');
    setAuditResult(null);
    try {
      const response = await fetch(`${API}/api/v1/fixes/audit`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          repository_path: auditRepoPath,
          bug_description: auditBugDescription,
        }),
      });
      const payload = await response.json();
      if (!response.ok) throw new Error(payload.detail || 'The audit request failed.');
      setAuditResult(payload);
    } catch (caught) {
      setAuditError(caught instanceof Error ? caught.message : 'Unable to connect to the backend.');
    } finally {
      setAuditLoading(false);
    }
  }

  async function applyApprovedFix() {
    if (!run) return;
    setApplyMessage('Applying approved candidate to a new Git branch...');
    try {
      const response = await fetch(`${API}/api/v1/fixes/apply-approved`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          repository_path: repositoryPath,
          candidate_operations: run.candidate_operations,
          approval_confirmed: approvalConfirmed,
          branch_name: `autofix/${run.run_id.slice(0, 8)}`,
          commit_message: 'fix: apply approved AutoFix candidate',
        }),
      });
      const payload = await response.json();
      if (!response.ok) throw new Error(payload.detail || 'Could not apply the approved fix.');
      setApplyMessage(`Committed ${payload.commit_sha.slice(0, 8)} on ${payload.branch_name}.`);
    } catch (caught) {
      setApplyMessage(caught instanceof Error ? caught.message : 'Could not apply the approved fix.');
    }
  }

  const loadExampleOperations = () => {
    setCandidateOperations(JSON.stringify(EXAMPLE_OPERATION, null, 2));
  };

  return (
    <main className="min-h-screen bg-[#090d16] text-slate-100">
      <header className="border-b border-slate-800 bg-slate-950/70 px-6 py-5">
        <div className="mx-auto flex max-w-6xl items-center gap-3">
          <div className="rounded-xl bg-indigo-600 p-2">
            <Bot />
          </div>
          <div>
            <h1 className="text-xl font-bold">AutoFix AI</h1>
            <p className="text-sm text-slate-400">Autonomous AI Bug Fixing Assistant</p>
          </div>
        </div>
      </header>

      <section className="mx-auto max-w-6xl px-6 py-10">
        <div className="mb-8 max-w-3xl">
          <p className="mb-3 text-sm font-semibold text-indigo-300">SAFE, REVIEW-FIRST WORKFLOW</p>
          <h2 className="text-4xl font-bold tracking-tight">Diagnose, validate, and document a bug fix.</h2>
          <p className="mt-4 leading-7 text-slate-400">
            AutoFix scans a local repository, investigates the report, drafts line-specific fixes, and validates
            edits in isolated disposable workspaces.
          </p>
        </div>

        {/* ── Mode tabs ── */}
        <div className="mb-6 flex gap-1 rounded-xl border border-slate-800 bg-slate-900/70 p-1 w-fit">
          <button
            onClick={() => setMode('analyze')}
            className={`flex items-center gap-2 rounded-lg px-4 py-2 text-sm font-medium transition-colors ${
              mode === 'analyze'
                ? 'bg-indigo-600 text-white'
                : 'text-slate-400 hover:text-slate-200'
            }`}
          >
            <Play size={15} /> Analyze &amp; Validate
          </button>
          <button
            onClick={() => setMode('audit')}
            className={`flex items-center gap-2 rounded-lg px-4 py-2 text-sm font-medium transition-colors ${
              mode === 'audit'
                ? 'bg-indigo-600 text-white'
                : 'text-slate-400 hover:text-slate-200'
            }`}
          >
            <Search size={15} /> Audit Repository
          </button>
        </div>

        {/* ══ AUDIT MODE ══════════════════════════════════════════════════════ */}
        {mode === 'audit' && (
          <>
            <form
              onSubmit={submitAudit}
              className="rounded-2xl border border-slate-800 bg-slate-900/70 p-6 shadow-2xl"
            >
              <p className="mb-4 text-sm text-slate-400">
                Point AutoFix at any repository and describe the bug. It will{' '}
                <strong className="text-slate-200">scan every source file</strong> for the matching
                pattern and return exact <span className="font-mono text-indigo-300">file:line</span>{' '}
                locations — no manual file path needed.
              </p>
              <div className="grid gap-5 md:grid-cols-1">
                <label className="text-sm font-medium">
                  Local repository path
                  <input
                    required
                    value={auditRepoPath}
                    onChange={(e) => setAuditRepoPath(e.target.value)}
                    placeholder="C:\projects\my-service"
                    className="mt-2 w-full rounded-lg border border-slate-700 bg-slate-950 px-3 py-2.5 text-sm outline-none focus:border-indigo-500"
                  />
                </label>
              </div>
              <label className="mt-5 block text-sm font-medium">
                Bug description or error log
                <textarea
                  required
                  minLength={10}
                  value={auditBugDescription}
                  onChange={(e) => setAuditBugDescription(e.target.value)}
                  placeholder="e.g. ZeroDivisionError when total_visitors is 0, or KeyError when email is missing"
                  rows={4}
                  className="mt-2 w-full rounded-lg border border-slate-700 bg-slate-950 px-3 py-2.5 font-mono text-sm outline-none focus:border-indigo-500"
                />
              </label>
              <button
                disabled={auditLoading}
                className="mt-5 flex items-center gap-2 rounded-lg bg-indigo-600 px-5 py-2.5 text-sm font-semibold hover:bg-indigo-500 disabled:opacity-60"
              >
                {auditLoading ? <Loader2 className="animate-spin" size={17} /> : <Search size={17} />}
                {auditLoading ? 'Scanning repository...' : 'Audit for bug location'}
              </button>
            </form>

            {auditError && (
              <div className="mt-6 flex gap-2 rounded-xl border border-rose-800 bg-rose-950/40 p-4 text-rose-200">
                <AlertCircle /> {auditError}
              </div>
            )}

            {auditResult && (
              <section className="mt-8 space-y-6">
                <div className="flex flex-wrap items-center justify-between gap-3 rounded-xl border border-slate-800 bg-slate-900 p-5">
                  <div>
                    <p className="text-sm text-slate-400">Repository: {auditResult.repository_path}</p>
                    <h3 className="mt-1 text-xl font-semibold">
                      {auditResult.total_found > 0
                        ? `Found ${auditResult.total_found} suspicious location${auditResult.total_found > 1 ? 's' : ''}`
                        : 'No matching patterns found'}
                    </h3>
                  </div>
                  <span className="rounded-full border border-amber-500/40 bg-amber-500/10 px-3 py-1 text-sm text-amber-200">
                    Audit scan
                  </span>
                </div>

                {auditResult.total_found > 0 && (
                  <Card icon={<FileCode2 />} title="Bug Locations Found">
                    <div className="space-y-4">
                      {auditResult.candidates.map((c, idx) => (
                        <div key={idx} className="rounded-lg border border-slate-800 bg-slate-950/80 p-4 text-xs">
                          <div className="mb-2 flex flex-wrap items-center justify-between gap-2 border-b border-slate-800/80 pb-2">
                            <span className="font-mono font-semibold text-indigo-300">{c.file_path}</span>
                            <span className="flex items-center gap-1 rounded bg-indigo-950 px-2 py-0.5 text-[11px] font-semibold text-indigo-300 border border-indigo-700/50">
                              <Hash size={12} /> Line {c.line_number}
                            </span>
                          </div>
                          {c.description && (
                            <p className="mb-2 text-amber-300 text-[11px]">⚠ {c.description}</p>
                          )}
                          <div className="mb-2">
                            <span className="text-slate-400">Vulnerable line:</span>
                            <pre className="mt-1 overflow-x-auto rounded bg-slate-900 p-2 text-rose-300">{c.search}</pre>
                          </div>
                          <div>
                            <span className="text-slate-400">Suggested fix:</span>
                            <pre className="mt-1 overflow-x-auto rounded bg-slate-900 p-2 text-emerald-300">{c.replacement}</pre>
                          </div>
                        </div>
                      ))}
                    </div>
                  </Card>
                )}

                {auditResult.total_found === 0 && (
                  <Card icon={<CheckCircle2 />} title="Clean scan">
                    <p className="text-slate-400">
                      No patterns matching the bug description were found in any production source files.
                      Try rephrasing the bug description or switch to the Analyze &amp; Validate tab to run
                      tests.
                    </p>
                  </Card>
                )}
              </section>
            )}
          </>
        )}

        {/* ══ ANALYZE MODE ════════════════════════════════════════════════════ */}
        {mode === 'analyze' && (
          <>
            <form onSubmit={submit} className="rounded-2xl border border-slate-800 bg-slate-900/70 p-6 shadow-2xl">
              <div className="grid gap-5 md:grid-cols-2">
                <label className="text-sm font-medium">
                  Local repository path
                  <input
                    required
                    value={repositoryPath}
                    onChange={(e) => setRepositoryPath(e.target.value)}
                    placeholder="C:\projects\my-service"
                    className="mt-2 w-full rounded-lg border border-slate-700 bg-slate-950 px-3 py-2.5 text-sm outline-none focus:border-indigo-500"
                  />
                </label>
                <label className="text-sm font-medium">
                  Safe test command
                  <input
                    required
                    value={testCommand}
                    onChange={(e) => setTestCommand(e.target.value)}
                    className="mt-2 w-full rounded-lg border border-slate-700 bg-slate-950 px-3 py-2.5 font-mono text-sm outline-none focus:border-indigo-500"
                  />
                </label>
              </div>

              <label className="mt-5 block text-sm font-medium">
                Bug description or error log
                <textarea
                  required
                  minLength={10}
                  value={bugDescription}
                  onChange={(e) => setBugDescription(e.target.value)}
                  placeholder="Paste the stack trace, failing test, or expected behavior..."
                  rows={5}
                  className="mt-2 w-full rounded-lg border border-slate-700 bg-slate-950 px-3 py-2.5 font-mono text-sm outline-none focus:border-indigo-500"
                />
              </label>

              <div className="mt-5">
                <div className="flex flex-wrap items-center justify-between gap-2">
                  <label className="text-sm font-medium">
                    Candidate edits JSON{' '}
                    <span className="font-normal text-slate-500">(specify file_path, line_number, search &amp; replacement)</span>
                  </label>
                  <button
                    type="button"
                    onClick={loadExampleOperations}
                    className="text-xs text-indigo-400 hover:text-indigo-300 hover:underline"
                  >
                    + Insert line-based example
                  </button>
                </div>
                <textarea
                  value={candidateOperations}
                  onChange={(e) => setCandidateOperations(e.target.value)}
                  placeholder='[{"file_path": "app.py", "line_number": 12, "search": "old_code", "replacement": "new_code"}]'
                  rows={5}
                  className="mt-2 w-full rounded-lg border border-slate-700 bg-slate-950 px-3 py-2.5 font-mono text-xs outline-none focus:border-indigo-500"
                />
              </div>

              <button
                disabled={loading}
                className="mt-5 flex items-center gap-2 rounded-lg bg-indigo-600 px-5 py-2.5 text-sm font-semibold hover:bg-indigo-500 disabled:opacity-60"
              >
                {loading ? <Loader2 className="animate-spin" size={17} /> : <Play size={17} />}
                {loading ? 'Running agents...' : 'Analyze and validate'}
              </button>
            </form>

            {error && (
              <div className="mt-6 flex gap-2 rounded-xl border border-rose-800 bg-rose-950/40 p-4 text-rose-200">
                <AlertCircle /> {error}
              </div>
            )}

            {run && (
              <section className="mt-8 space-y-6">
                <div className="flex flex-wrap items-center justify-between gap-3 rounded-xl border border-slate-800 bg-slate-900 p-5">
                  <div>
                    <p className="text-sm text-slate-400">Run {run.run_id}</p>
                    <h3 className="mt-1 text-xl font-semibold">
                      {run.status === 'ready_for_review' ? 'Ready for human review' : 'Validation needs attention'}
                    </h3>
                  </div>
                  <span className="rounded-full border border-indigo-500/40 bg-indigo-500/10 px-3 py-1 text-sm text-indigo-200">
                    {run.llm_mode === 'openai_compatible' ? 'LLM-assisted proposal' : 'Heuristic fallback'}
                  </span>
                </div>

                <div className="grid gap-6 lg:grid-cols-2">
                  <Card icon={<Code2 />} title="Root cause">
                    <p>{run.root_cause}</p>
                    <h4 className="mt-4 font-semibold">Affected files</h4>
                    <ul className="mt-2 list-inside list-disc text-sm text-slate-400">
                      {run.affected_files.length ? (
                        run.affected_files.map((x) => <li key={x}>{x}</li>)
                      ) : (
                        <li>No file could be localized from the report.</li>
                      )}
                    </ul>
                  </Card>
                  <Card icon={<ClipboardCheck />} title="Proposed fix">
                    <p>{run.proposed_fix}</p>
                    <pre className="mt-4 overflow-x-auto rounded-lg border border-slate-800 bg-slate-950 p-4 text-xs text-emerald-300">
                      {run.patch_preview}
                    </pre>
                  </Card>
                </div>

                {run.candidate_operations.length > 0 && (
                  <Card icon={<FileCode2 />} title="Candidate Operations — File &amp; Line Breakdown">
                    <div className="space-y-4">
                      {run.candidate_operations.map((op, idx) => (
                        <div key={idx} className="rounded-lg border border-slate-800 bg-slate-950/80 p-4 text-xs">
                          <div className="mb-2 flex flex-wrap items-center justify-between gap-2 border-b border-slate-800/80 pb-2">
                            <span className="font-mono font-semibold text-indigo-300">{op.file_path}</span>
                            {op.line_number != null && (
                              <span className="flex items-center gap-1 rounded bg-indigo-950 px-2 py-0.5 text-[11px] font-semibold text-indigo-300 border border-indigo-700/50">
                                <Hash size={12} /> Line {op.line_number}
                              </span>
                            )}
                          </div>
                          {op.search && (
                            <div className="mb-2">
                              <span className="text-slate-400">Search block:</span>
                              <pre className="mt-1 overflow-x-auto rounded bg-slate-900 p-2 text-rose-300">{op.search}</pre>
                            </div>
                          )}
                          <div>
                            <span className="text-slate-400">Replacement content:</span>
                            <pre className="mt-1 overflow-x-auto rounded bg-slate-900 p-2 text-emerald-300">{op.replacement}</pre>
                          </div>
                        </div>
                      ))}
                    </div>
                  </Card>
                )}

                {run.candidate_operations.length === 0 && (
                  <Card icon={<AlertCircle />} title="No candidate operations">
                    <p className="text-slate-400 text-sm">
                      The heuristic engine could not automatically locate the bug in the source files.
                      Try switching to <strong className="text-slate-200">Audit Repository</strong> mode, or
                      provide candidate operations manually in the form above.
                    </p>
                  </Card>
                )}

                <Card icon={<Bot />} title="Debugging journey">
                  <div className="space-y-3">
                    {run.journey.map((step) => (
                      <div key={step.agent} className="flex gap-3 rounded-lg bg-slate-950/70 p-3">
                        <CheckCircle2
                          className={step.status === 'completed' ? 'text-emerald-400' : 'text-amber-400'}
                          size={19}
                        />
                        <div>
                          <p className="font-medium">{step.agent}</p>
                          <p className="text-sm text-slate-400">{step.summary}</p>
                        </div>
                      </div>
                    ))}
                  </div>
                </Card>

                <div className="grid gap-6 lg:grid-cols-2">
                  <Evidence title="Validation run" data={run.validation} />
                  <Evidence title="Regression run" data={run.regression} />
                </div>

                <Card icon={<ShieldCheck />} title="Approval and pull request summary">
                  <p>{run.pull_request_summary}</p>
                  {run.candidate_operations.length > 0 && (
                    <div className="mt-4 border-t border-slate-800 pt-4">
                      <label className="flex items-center gap-2 text-sm">
                        <input
                          type="checkbox"
                          checked={approvalConfirmed}
                          onChange={(e) => setApprovalConfirmed(e.target.checked)}
                        />
                        I reviewed this candidate and approve committing it to a new AutoFix branch.
                      </label>
                      <button
                        onClick={applyApprovedFix}
                        disabled={!approvalConfirmed}
                        className="mt-3 flex items-center gap-2 rounded-lg bg-emerald-600 px-4 py-2 text-sm font-semibold disabled:opacity-50"
                      >
                        <GitBranch size={16} /> Apply approved fix and commit
                      </button>
                      {applyMessage && <p className="mt-3 text-sm text-slate-300">{applyMessage}</p>}
                    </div>
                  )}
                  <p className="mt-3 text-sm text-slate-500">Approval is the only action that writes to the supplied repository.</p>
                </Card>
              </section>
            )}
          </>
        )}
      </section>
    </main>
  );
}

function Card({ title, icon, children }: { title: string; icon: React.ReactNode; children: React.ReactNode }) {
  return (
    <article className="rounded-xl border border-slate-800 bg-slate-900/70 p-5">
      <h3 className="mb-4 flex items-center gap-2 font-semibold text-indigo-200">
        {icon}
        {title}
      </h3>
      {children}
    </article>
  );
}

function Evidence({ title, data }: { title: string; data: EvidenceData }) {
  return (
    <Card icon={<Terminal />} title={title}>
      <p className={data.passed ? 'text-emerald-300' : 'text-amber-300'}>
        {data.passed ? 'Passed' : 'Failed'} - {data.isolation}
      </p>
      <p className="mt-2 font-mono text-xs text-slate-400">$ {data.command}</p>
      <pre className="mt-3 max-h-56 overflow-auto rounded-lg bg-slate-950 p-3 text-xs text-slate-300">
        {data.output || 'No output.'}
      </pre>
    </Card>
  );
}
