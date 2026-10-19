#!/usr/bin/env python3
"""Read-only *metadata/lint* checks for a Repo Factory project, NOT proof of acceptance.

Checks can detect missing documents and inconsistent self-reported release states.
They cannot prove code is correct, authorization exists or hosted CI actually passed.
"""
import argparse
import json
import re
from pathlib import Path
from urllib.parse import urlparse

DOCS = [
    'AGENTS.md', 'GOAL.md', 'README.md',
    *[f'docs/{n:02d}-{suffix}.md' for n, suffix in [
        (1, 'product-brief'), (2, 'architecture'), (3, 'contracts'),
        (4, 'acceptance'), (5, 'fixtures'), (6, 'test-plan'),
        (7, 'build-plan'), (8, 'release'), (9, 'decisions')]],
    'docs/IMPLEMENTATION-STATUS.md', 'docs/REPO-FACTORY-STATUS.json',
]
ORDER = ['DRAFT', 'IDEA_SELECTED', 'SPEC_READY', 'M0_PASS', 'IN_PROGRESS',
         'LOCAL_READY', 'AUDIT_PASS', 'INITIAL_PUSH_AUTHORIZED',
         'PUSHED_CI_PENDING', 'RELEASE_READY']
SHA = re.compile(r'^[a-fA-F0-9]{40}$')
AC = re.compile(r'^AC-\d{2,}$')


def check(project_dir: Path, phase: str):
    project_dir = project_dir.expanduser().resolve()
    errors, warnings = [], []
    for name in DOCS:
        if not (project_dir / name).is_file():
            errors.append(f'Missing required contract file: {name}')
    if errors:
        return errors, warnings
    try:
        state = json.loads((project_dir / 'docs/REPO-FACTORY-STATUS.json').read_text(encoding='utf-8'))
    except (OSError, ValueError) as exc:
        return [f'Status JSON invalid: {exc}'], warnings
    if state.get('schema_version') != 1:
        errors.append('Unknown status schema_version')
    actual = state.get('phase')
    if actual not in ORDER:
        errors.append(f'Unknown lifecycle phase: {actual}')
    requested = {'spec': 'SPEC_READY', 'preflight': 'M0_PASS', 'local': 'LOCAL_READY',
                 'audit': 'AUDIT_PASS', 'release': 'RELEASE_READY'}[phase]
    if actual in ORDER and ORDER.index(actual) < ORDER.index(requested):
        errors.append(f'Phase {actual} cannot satisfy {requested}')

    for name in DOCS:
        if not name.endswith('.md'):
            continue
        text = (project_dir / name).read_text(encoding='utf-8')
        if re.search(r'\bTODO\b|\{\{(?:TITLE|SLUG|PROFILE)\}\}', text, re.IGNORECASE):
            errors.append(f'Unresolved placeholder in {name}')

    acceptance = state.get('acceptance')
    if not isinstance(acceptance, list) or not acceptance:
        errors.append('Status must have nonempty acceptance array')
        acceptance = []
    ids = []
    for item in acceptance:
        if not isinstance(item, dict) or not AC.fullmatch(str(item.get('id', ''))):
            errors.append('Invalid acceptance ID')
            continue
        ids.append(item['id'])
        if item.get('status') not in {'NOT_RUN', 'PASS', 'FAIL', 'PENDING_HOSTED_CI'}:
            errors.append(f"Unknown AC state for {item['id']}")
        if phase in {'local', 'audit', 'release'}:
            allowed = {'PASS'} if phase == 'release' else {'PASS', 'PENDING_HOSTED_CI'}
            if item.get('status') not in allowed:
                errors.append(f"Missing local acceptance result for {item['id']}")
            if item.get('status') == 'PASS' and not item.get('evidence'):
                errors.append(f"Missing evidence references for {item['id']}")
    if len(ids) != len(set(ids)):
        errors.append('Duplicate AC IDs in status')
    if phase in {'local', 'audit', 'release'}:
        checks = state.get('checks')
        if not isinstance(checks, list) or not checks:
            errors.append('No executed check records')
        else:
            for c in checks:
                if not isinstance(c, dict) or not c.get('command') or c.get('exit_code') != 0 or not c.get('evidence'):
                    errors.append('Invalid check: requires command, exit_code=0, evidence reference')
        audit = state.get('audit') or {}
        if phase in {'audit', 'release'}:
            if audit.get('status') != 'PASS' or not audit.get('candidate_fingerprint') or audit.get('findings'):
                errors.append('Independent audit PASS on current candidate is required (metadata only)')
    if phase == 'release':
        auth = state.get('authorization') or {}
        host = state.get('hosted_ci') or {}
        sha = state.get('final_commit_sha')
        if auth.get('initial_push') is not True or not auth.get('remote') or auth.get('visibility') not in {'public', 'private'}:
            errors.append('Missing explicit initial push authorization metadata')
        if not isinstance(sha, str) or not SHA.fullmatch(sha):
            errors.append('final_commit_sha must be 40 hex digits')
        if host.get('status') != 'PASS' or host.get('conclusion') != 'success' or host.get('head_sha') != sha:
            errors.append('Hosted CI success must match final intended commit SHA')
        url = host.get('run_url')
        p = urlparse(url) if isinstance(url, str) else None
        if not p or p.scheme != 'https' or p.hostname != 'github.com' or not re.fullmatch(r'/[^/]+/[^/]+/actions/runs/\d+', p.path):
            errors.append('Hosted GitHub Actions run URL missing or invalid')
    warnings.append('Metadata-only validation: verify source, commands, external CI and authorization independently.')
    return errors, warnings


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--project-dir', type=Path, required=True)
    parser.add_argument('--phase', choices=['spec', 'preflight', 'local', 'audit', 'release'], required=True)
    args = parser.parse_args()
    errors, warnings = check(args.project_dir, args.phase)
    print(json.dumps({'phase': args.phase, 'metadata_check': 'FAIL' if errors else 'PASS',
                      'errors': errors, 'warnings': warnings}, indent=2))
    raise SystemExit(2 if errors else 0)


if __name__ == '__main__':
    main()
