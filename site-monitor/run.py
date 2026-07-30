"""Site Drift Detector — detect DOM changes on SauceDemo."""

from __future__ import annotations

import json
import sys
from pathlib import Path

import click

from monitor.fetcher import fetch_page, fetch_js_bundle
from monitor.extractor import extract_from_html, extract_from_js, build_snapshot
from monitor.comparator import compare, check_monitored, DriftReport
from monitor.reporter import generate_markdown, create_github_issue
from monitor.datadog import send_drift_metrics


@click.command()
@click.option("--url", default="https://www.saucedemo.com", help="Target URL to monitor")
@click.option("--baseline", default="baseline.json", help="Path to baseline snapshot")
@click.option("--update-baseline", is_flag=True, help="Overwrite baseline with current snapshot")
@click.option("--auto-issue", is_flag=True, help="Create GitHub issue on drift")
@click.option("--output", default=None, help="Write report to file")
def main(url: str, baseline: str, update_baseline: bool, auto_issue: bool, output: str | None) -> None:
    """Run the site drift detector."""
    baseline_path = Path(baseline)
    registry_path = Path(__file__).parent / "selectors.json"

    # Fetch current state
    print(f"[INFO] Fetching {url}...")
    try:
        html = fetch_page(url)
    except Exception as exc:
        print(f"[ERROR] Failed to fetch page: {exc}", file=sys.stderr)
        sys.exit(1)

    js_content, js_bundle_path = fetch_js_bundle(html, url)
    if js_content:
        print(f"[INFO] Fetched JS bundle: {js_bundle_path}")
    else:
        print("[WARN] No JS bundle found. Extracting from HTML only.")

    # Extract selectors
    html_selectors = extract_from_html(html)
    js_selectors = extract_from_js(js_content) if js_content else {"ids": set(), "classes": set(), "data_test": set()}

    snapshot = build_snapshot(html_selectors, js_selectors, url, js_bundle_path)
    print(
        f"[INFO] Found {len(snapshot['ids'])} IDs, "
        f"{len(snapshot['classes'])} classes, "
        f"{len(snapshot['data_test'])} data-test attributes"
    )

    # Update baseline mode
    if update_baseline:
        baseline_path.write_text(json.dumps(snapshot, indent=2), encoding="utf-8")
        print(f"[INFO] Baseline updated: {baseline_path}")
        return

    # Compare against baseline
    if not baseline_path.exists():
        print(f"[ERROR] Baseline not found: {baseline_path}", file=sys.stderr)
        print("Run with --update-baseline to generate one.", file=sys.stderr)
        sys.exit(1)

    with open(baseline_path, encoding="utf-8") as f:
        baseline_data = json.load(f)

    report: DriftReport = compare(baseline_data, snapshot)
    affected = check_monitored(report, registry_path)

    # Generate report
    markdown = generate_markdown(report, affected)

    if output:
        Path(output).write_text(markdown, encoding="utf-8")
        print(f"[INFO] Report written to {output}")
    else:
        print("\n" + markdown)

    # GitHub issue on critical drift
    if auto_issue and report.severity == "critical":
        title = f"[Site Drift] {report.total_removed} selector(s) removed from saucedemo.com"
        create_github_issue(title, markdown)

    # Send DataDog metrics
    send_drift_metrics(
        drift_detected=report.has_drift,
        selectors_removed=report.total_removed,
        selectors_added=report.total_added,
    )

    # Exit status
    if report.has_drift:
        status = "DRIFT DETECTED" if report.severity == "critical" else "New selectors found (info)"
        print(f"\n[RESULT] {status}")
    else:
        print("\n[RESULT] No drift detected.")


if __name__ == "__main__":
    main()
