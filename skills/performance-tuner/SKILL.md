---
name: performance-tuner
description: >-
  Find and fix slow code with evidence instead of hunches. Measures a baseline,
  profiles to locate the real bottleneck, fixes the biggest one first, measures
  again, and reports before and after numbers. Covers CPU hotspots, N+1 database
  queries, memory growth, slow page loads and inefficient algorithms. Use this
  skill whenever the user says this is slow, takes too long, speed this up,
  optimize this, high CPU or memory, or the page loads slowly, and for Dutch
  phrases such as "dit is traag", "maak dit sneller", "waarom duurt dit zo lang"
  or "performance verbeteren".
license: "MIT"
metadata:
  author: "prompt"
  category: "code"
  tags: "performance, profiling, optimization, speed, benchmark, bottleneck, traag, sneller, prestaties"
  version: "1.0.0"
  summary_nl: "Meet eerst, vindt de grootste vertraging in je code, lost die op en toont de tijden van voor en na."
---

# Performance tuner

Intuition about performance is wrong surprisingly often. The loop you suspect takes 2 percent of the time; the real cost is a database call inside it. This skill follows a strict measure, change, measure loop so every optimization is backed by numbers, and so effort goes to the one bottleneck that matters.

## Workflow

1. **Define slow and the target.** Which operation, how slow now, and how fast is fast enough? "Export takes 40 s, should be under 5 s" gives a finish line. Without a target, optimization never ends.
2. **Build a repeatable measurement.** Use realistic data size and run it several times, discarding the first (warm-up, caches). Examples:
   - Shell: `hyperfine 'python export.py --rows 100000'`
   - Python: `python -m timeit`, or `time.perf_counter()` around the section
   - Node: `console.time` / `performance.now()`, or a benchmark library
   - Go: `go test -bench=. -benchmem`
   - HTTP: `curl -w '%{time_total}\n' -o /dev/null -s URL` repeated, or a load tool such as k6 or autocannon
   - Browser: Lighthouse and the Performance panel in DevTools
   Record the baseline: median and spread, plus environment.
3. **Profile to find where time goes.** Do not optimize yet.
   - Python: `python -m cProfile -s cumtime script.py`, or `py-spy record`
   - Node: `node --cpu-prof app.js` and open the profile in DevTools
   - Go: `pprof`; Java: async-profiler or JFR; .NET: dotnet-trace
   - Databases: enable query logging and run `EXPLAIN ANALYZE` on the slow queries
   - Memory: heap snapshots, `tracemalloc`, `--inspect` heap profiler
4. **Pick the biggest bottleneck.** Rank by share of total time. Fixing something that takes 5 percent can save at most 5 percent, however clever the fix.
5. **Fix it with the least invasive change that works.** Typical fixes in rough order of payoff:
   - Remove repeated work: N+1 queries (batch or join), recomputation inside loops, repeated parsing
   - Better algorithm or data structure: list lookup in a loop becomes a set or dict, O(n squared) becomes O(n log n)
   - Add a missing database index, or select only needed columns
   - Batch I/O, stream instead of loading everything into memory
   - Run independent I/O concurrently
   - Cache, but only with a clear invalidation rule
6. **Check correctness.** Run the tests. A faster wrong answer is a bug.
7. **Measure again** with the same benchmark and compare. If the gain is within noise, revert; complexity without measurable gain is a cost.
8. **Repeat or stop.** Re-profile, since the bottleneck moves. Stop when the target is met and tell the user.

## Output format

```markdown
**Target:** order export under 5 s for 100k rows

| Step | Change | Median | Speedup |
|---|---|---|---|
| Baseline | - | 41.2 s | 1x |
| 1 | Batch customer lookups (N+1, 100k queries to 1) | 6.8 s | 6.1x |
| 2 | Index on orders.created_at | 3.9 s | 10.6x |

Measured with hyperfine, 10 runs, local Postgres 16, same dataset each run.
Tests: full suite green after each step.
Profile before: 83% of time in `get_customer` (cProfile). After: 41% in CSV writing; not worth further work at this target.
```

## Pitfalls and when to ask

- Never report a speedup you did not measure. If you could not run the benchmark, say the improvement is expected and explain why.
- Micro-benchmarks lie when the data is tiny or the JIT optimizes the work away. Use realistic inputs.
- Caching and concurrency add bugs; ask before introducing a cache layer, a new service, or parallelism with shared state.
- Ask before adding indexes or schema changes on production databases; they can lock tables.
- Readability matters. If a fix makes code much harder to read for a small gain, present the trade-off and let the user decide.

## Scope

For speed and resource use. For crashes and wrong results use debug-detective; for structural cleanup without a speed goal use refactor-safely.
