# Build prompt: Optimization and Acceleration pass (GridPlayer Alabaster)

## Your role: you are the expert, so let it rip
You're the expert here: superoptimizer, bug stomper and security hardener. The owner and his earlier assistant have already reviewed this code, and they assume they missed things. Your job is to find what they overlooked. Everything listed below is a floor, not a ceiling: the known findings, the measurements and the checks are where you start, not the scope. Add your own checks, challenge our assumptions and findings, and report anything you think matters, including areas we never mentioned. The only fixed limits are the owner's hard requirements and the report-first rule. If your report shows gaps, the owner will point you at specific targets in a follow-up.

Owner: XDevMatt. Run this after the security fixes are merged so it doesn't reopen anything. Phase 1 is a measurement report only. Change nothing until the owner approves.

## Rules
- The security and privacy rules in `audit-security-privacy.md` still apply. No optimization may add a listener, a network call or a cookie.
- Measure before and after every change; no change without a number.
- Hardware: Windows 10, Intel Iris Plus (Quick Sync). Prefer hardware decoding.

## Measure
1. **Soak test:** a 4x4 grid of local files looping for 60 minutes. Record private bytes and handles per process (main process and each VLC player process) every minute. Flag anything that keeps growing.
2. **Python leaks:** `tracemalloc` snapshots at 5, 30 and 60 minutes in the main process, top growth by line.
3. **Open and close churn:** load and close a 16-video playlist 50 times. Memory and handle counts must return to baseline.
4. **Startup time:** cold and warm, to first frame with a 4-video playlist.
5. **Seek and sync:** seek latency per cell, and drift between cells in synced playback.
6. **CPU and GPU:** usage during 4 and 16 cells at 1080p HEVC (HLG test files are listed in the owner's `Zowey-HLG-compare.gpls` playlist).

## Deliverable
`docs/audit/performance-findings.md`: each measurement with the method, numbers, suspected cause (file and line) and the proposed fix ranked by payoff. Stop there and wait for approval.
## Acceleration, not just cleanup
Think like an application-acceleration consultancy, not only a profiler: startup and first-frame time, decode and render paths (Quick Sync hardware decode, zero-copy where possible), thread and process layout across many cells, I/O patterns, prefetching, lazy imports and anything else that makes the app feel faster. Propose ideas we haven't asked about.

## Settings must be defined before tuning
Every setting this pass touches gets a written definition in `docs/settings-reference.md`: what it controls, units, default, the owner's current value, and the measured effect. Review every setting under Settings > Performance, Streaming and Cache, plus any libVLC options the app sets or leaves at defaults. For each one, recommend whether it should stay user-facing, move to an advanced ini-only value, or become a fixed constant, and why.
