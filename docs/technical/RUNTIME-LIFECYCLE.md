# Runtime lifecycle and resource ownership

This is an unofficial, independent integration, not affiliated with, endorsed by or supported by Microclimate. Product names identify compatibility only.

## Ownership and data flow

Before V2-16/V2-21, the coordinator owned poll/write locks and native writes, but CardAPI also performed reads, accessed those private locks, attached `_card_*` fields dynamically, and owned job history alongside WebSocket subscriptions. Entry entities resolved their coordinator through a global dictionary. Read adapters discarded useful error categories. Jobs had a fixed 600-second deadline regardless of size, history had only a per-entry bound, and subscriptions had no integration limit.

The implementation now has these concrete owners:

| Owner | Responsibility |
| --- | --- |
| Config entry `runtime_data` | Its typed `MicroclimateCoordinator`, consumed by entity platforms. The existing domain entry index remains for discovery and diagnostics; it references the same object. |
| Coordinator | One polling/normalization owner, I/O lock, write lock, tracked write/refresh tasks, explicit generation/context/active-job state, native write validation and readback. Batch jobs use `async_batch`, `async_read_locked`, `async_write_locked` and `track_write_task`. |
| `CardJobs` | Bounded typed job records, admission/idempotency, sequential execution of `EditPlan`, stop/completion/history. Both WebSocket saves and HA schedule actions use this same manager. |
| `CardAPI` | Authentication/routing, permission-filtered snapshots, bounded WebSocket subscriptions, static bundle registration. No vendor reads or private coordinator lock access. |
| `edit_plan.py` | Existing pure validation and frozen-source planning, unchanged. |

Polling, a native entity write, and a card/service batch all serialize I/O through the same coordinator. There is no new poller or generic runtime framework. A batch still validates fresh state and permissions, sends each update once, confirms readback, stops on failure, and never automatically replays or rolls back. Revisions and generation guards remain; the per-pin revision expectation is now an explicit argument.

## Lifecycle

Setup assigns the coordinator to the entry before forwarding platforms. Failed setup closes it; unload cancels and awaits tracked work before removing platforms. Failed unload reopens the same coordinator as before. Reload creates a new runtime generation. Device subscriptions detach from unavailable runtimes and rebind when the entry returns; disconnect removes all associated listeners. Job subscriptions retain operation IDs, not job objects. Unknown/expired operations require observing the controller again rather than replaying automatically.

Job completion is idempotent, including tasks cancelled before their coroutine starts. HA service waits shield the shared completion future, so cancelling a caller cannot cancel other observers' result. Permission checks also cover fresh preflight and final readback for no-op jobs.

### Coordinator hook decision

HA Core 2026.9.3 publishes fetched data after `_async_update_data` returns. Its supported fetch hook alone cannot hold the I/O lock through publication. The small `_async_refresh` lock wrapper is retained deliberately to prevent an older poll overwriting a confirmed write. The supported `_async_refresh_finished` callback is too late to acquire an asynchronous lock and does not replace that protection. The existing stale-poll/unload regressions remain. Re-evaluate this wrapper if HA adds a supported lock-through-publication hook; do not introduce a second polling mechanism.

## Limits and deadlines

- One active batch per entry; at most 32 active jobs integration-wide. Busy/capacity rejection sends nothing and creates no queued replay.
- At most 20 completed jobs per entry, 200 completed jobs globally, and one-hour retained history. History is pruned on access and completion; inactive expired records may remain until the next access, within those fixed bounds. Active jobs are never evicted.
- At most 32 Microclimate subscriptions per connection and 256 globally. Other integrations' subscriptions do not count against the per-connection allowance. Unsubscribe/disconnect frees capacity.
- Existing HTTP read timeout: 20 seconds; existing per-pin operation timeout: 60 seconds. No extra update retry is introduced.
- Batch deadline: `45 + 80 × planned_write_count` seconds. This conservative budget retains the former separate guarded-read allowance after V2-19 shares that read with the write primitive. A maximum eight-point schedule changing both values has 16 writes and a 1,325-second budget; additional alarm/ramp edits extend it by the same bounded per-step allowance. Zero-change jobs get 45 seconds.
- Deadline expiry stops the job and reports confirmed/unsent/uncertain fields. It does not imply rollback or permission to retry an uncertain write.

## Errors and validation

Read failures keep whitelisted `unavailable`, `invalid_payload` and `rate_limited` classifications through HTTP, entry reads, coordinator/setup and job results. Authentication remains the existing reauthentication path. Transport URLs, tokens and response bodies are never included in these errors. Config forms and native controls have actionable translations; WebSocket errors and job messages explain the next safe action while retaining stable machine-readable reason codes.

Regression coverage includes permission revocation, duplicate request IDs, no-op jobs, cancellation, failed setup/unload/reload, poll/write serialization, maximum schedule size with delayed readback, cross-entry job isolation, history/subscription/admission bounds, and error classification. Tests use mocked traffic; no live device write is required for this cleanup.

## V2-19 measurement and decision — 27 September 2026

Measured the released `v1.4.5-delta2` baseline (`4f6d4cc`) before changing runtime code, then repeated the same workloads with the shared baseline. `tests/test_save_measurements.py` uses real HA entities, normalization, coordinator, planner and jobs with mocked API reads/updates. The synthetic Evo Connect III Yellow channel starts with 2 or 8 populated points; each target increases by one native degree and, in the full-save case, each time increases by 600 seconds. All other readings remain stable. Startup/setup, initial subscriptions and teardown are excluded. Diagnostic entities retain the normal disabled defaults. Read counts are `getAll` calls; write counts are pin-update calls.

| Workload | Writes, before/after | Reads before | Reads after | HA state events, before/after | Coordinator notifications, before/after | Card snapshots, before/after | Job notifications, before/after |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| 2 points, Day/Night, targets only | 2 | 8 | 6 | 4 | 6 | 6 | 6 |
| 2 points, Multi, targets only | 2 | 8 | 6 | 4 | 6 | 6 | 6 |
| 8 points, Multi, targets only | 8 | 26 | 18 | 16 | 18 | 18 | 18 |
| 2 points, Day/Night, times and targets | 4 | 14 | 10 | 8 | 10 | 10 | 10 |
| 2 points, Multi, times and targets | 4 | 14 | 10 | 8 | 10 | 10 | 10 |
| 8 points, Multi, times and targets | 16 | 50 | 34 | 32 | 34 | 34 | 34 |
| 3 unchanged idle polls | 0 | 3 | 3 | 0 | 0 | 0 | 0 |
| 3 idle polls changing measured v0 to 24, 25, 26 | 0 | 3 | 3 | 7 | 3 | 3 | 0 |

HA state events count `state_changed` for entities belonging to the entry. Card counts use one actual CardAPI device subscription; job counts use one job listener (initial operation-subscription acknowledgement excluded). These are deterministic fixture counts, not universal event totals: enabled diagnostics, subscription counts and naturally varying observations affect real installations. No hardware latency or controller durability claims are made.

**Decision: implement baseline sharing.** A successful N-pin batch with immediate confirmation drops from `3N+2` to `2N+2` reads and retains N updates. The full two/eight-point saves eliminate 4/16 cloud reads (28.6%/32% of reads; 22.2%/24.2% of total requests). This is a material reduction for two small runtime changes. There is no measured notification saving for stable readings, so notification suppression/debounce is deferred: unchanged snapshots already suppress publication, while progress and confirmed observations remain useful.

The coordinator still fetches a fresh baseline inside the batch's write/I/O locks. Its write primitive checks the expected settings revision, semantic context, capability, current credentials/options and permission after the awaited read, then dispatches once. It returns a copy of that baseline only after confirmation. The job uses the returned observation to calculate the expected post-write revision, replacing its own duplicate read. No caller-supplied baseline, cached observation, readback or previous step can be used as the next step's pre-dispatch baseline. Standalone entity writes retain their own read and existing return behavior.

The whole batch holds the same locks through preflight, all writes/readbacks and final confirmation. Permission/context changes during the shared read prevent dispatch. An expected-revision mismatch there is a known pre-dispatch `conflict`, not an uncertain write. Changes to other fields during readback or final confirmation still stop/fail the job. Delayed confirmation adds only bounded read attempts; it never repeats an update. The external API still cannot prevent a vendor-app edit between a fresh read and dispatch; the former additional read did not make this atomic either.

Reproduce the measurement with `python -m pytest -c pytest-review.ini tests/test_save_measurements.py -q -s` inside the supported HA test environment. To reproduce the original baseline, use a separate checkout of `4f6d4cc` with this measurement test and its read-count expectation changed to `3 * steps + 2`; all event/write expectations remain identical. Focused safety regressions are in `tests/test_save_baseline.py`, with existing compact permission, runtime and lifecycle regressions retained.

Validation: the baseline measurement checkout passed all 8 workloads; the implementation passed 63 measurement/card/compact tests and 12 additional baseline safety tests. After the change stabilized, the complete HA Core 2026.9.3 / Python 3.14.7 release-gate Python suite passed once: **789 passed, no skips, 96% integration coverage**. No live controller calls were made.
