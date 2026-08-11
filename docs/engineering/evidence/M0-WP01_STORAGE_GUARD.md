# M0-WP01 storage-guard evidence

- Source commit: `aedd217fd9f899bc9e0fdb0961c8704ab87ef2a1`
- Captured: `2026-08-11T17:30:13+08:00`
- Data class: `no_health_content`
- Review roles: `TECH`, `QA`

Commands:

```powershell
powershell -NoProfile -ExecutionPolicy Bypass -File .\tool\verify_storage_guard.ps1
powershell -NoProfile -ExecutionPolicy Bypass -File .\tool\run_ci.ps1 -Offline
```

Result: `pass`.

- storage-guard self-test passed with `0 MiB` observed and persistent C-drive growth;
- offline Strict CI format, analysis and four package suites passed;
- Strict CI observed and persistent C-drive growth was `3.46 MiB`, below the `100 MiB` hard stop;
- project caches resolved under `.local/`; Windows compatibility temp resolved under
  `D:/DevCaches/YunMom/tmp`;
- no SDK, IDE, emulator image or toolchain was installed or upgraded.

The ignored `.local/audit/storage-guard.jsonl` retains operational history, including the earlier
failed measurement. This evidence does not grant release approval.
