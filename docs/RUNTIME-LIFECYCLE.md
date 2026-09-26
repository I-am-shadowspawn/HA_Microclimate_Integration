# Runtime lifecycle and resource ownership — 1.4.2

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
- Batch deadline: `45 + 80 × planned_write_count` seconds. This accounts for preflight/final reads, each guarded read and each bounded write primitive, plus five seconds of overhead. A maximum eight-point schedule changing both values has 16 writes and a 1,325-second budget; additional alarm/ramp edits extend it by the same bounded per-step allowance. Zero-change jobs get 45 seconds.
- Deadline expiry stops the job and reports confirmed/unsent/uncertain fields. It does not imply rollback or permission to retry an uncertain write.

## Errors and validation

Read failures keep whitelisted `unavailable`, `invalid_payload` and `rate_limited` classifications through HTTP, entry reads, coordinator/setup and job results. Authentication remains the existing reauthentication path. Transport URLs, tokens and response bodies are never included in these errors. Config forms and native controls have actionable translations; WebSocket errors and job messages explain the next safe action while retaining stable machine-readable reason codes.

Regression coverage includes permission revocation, duplicate request IDs, no-op jobs, cancellation, failed setup/unload/reload, poll/write serialization, maximum schedule size with delayed readback, cross-entry job isolation, history/subscription/admission bounds, and error classification. Tests use mocked traffic; no live device write is required for this cleanup.
