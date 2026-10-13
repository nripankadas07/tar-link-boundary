"""Ordered virtual path witnesses for an uncompressed TAR; never extract."""
import argparse
import hashlib
import io
import json
from pathlib import Path
import re
import sys
import tarfile


class BoundaryError(ValueError):
    pass


def parts(name):
    if not isinstance(name, str) or not name or '\x00' in name:
        raise BoundaryError('invalid-empty-or-NUL-path')
    if name.startswith('/') or '\\' in name or re.match(r'^[A-Za-z]:', name):
        raise BoundaryError('absolute-or-nonportable-path')
    return name.split('/')


def resolve(tokens, nodes, trace, base=(), final_link=True):
    queue, stack, traversals = list(tokens), list(base), 0
    while queue:
        token = queue.pop(0)
        if token in ('', '.'):
            continue
        if token == '..':
            if not stack:
                raise BoundaryError('parent-escapes-root')
            stack.pop()
            continue
        stack.append(token)
        key = '/'.join(stack)
        node = nodes.get(key)
        if node and node['kind'] in ('symlink', 'hardlink') and (queue or final_link):
            traversals += 1
            if traversals > 40:
                raise BoundaryError('link-cycle-or-depth-limit')
            trace.append({'link': key, 'target': node['target'], 'kind': node['kind']})
            target = parts(node['target'])
            stack = stack[:-1] if node['kind'] == 'symlink' else []
            queue = target + queue
        elif node and node['kind'] == 'file' and queue:
            raise BoundaryError('non-directory-parent')
    return '/'.join(stack)


def analyze(events):
    if not isinstance(events, list) or len(events) > 10000:
        raise ValueError('events must be an array of at most 10000 members')
    nodes, rows = {}, []
    for index, e in enumerate(events):
        if not isinstance(e, dict):
            raise ValueError('member must be an object')
        name, kind, target = e.get('name'), e.get('kind'), e.get('target')
        if kind not in ('file', 'dir', 'symlink', 'hardlink', 'special'):
            raise ValueError('unknown member kind')
        trace, dest, reason = [], None, None
        try:
            dest = resolve(parts(name), nodes, trace, final_link=False)
            if not dest:
                if kind != 'dir':
                    raise BoundaryError('non-directory-root-member')
            if dest in nodes:
                raise BoundaryError('duplicate-or-overwrite-unsupported')
            if kind == 'special':
                raise BoundaryError('special-member-unsupported')
            if kind in ('symlink', 'hardlink'):
                base = tuple(dest.split('/')[:-1]) if kind == 'symlink' else ()
                resolved_target = resolve(parts(target), nodes, trace, base)
                if kind == 'hardlink' and (resolved_target not in nodes or nodes[resolved_target]['kind'] != 'file'):
                    raise BoundaryError('hardlink-target-not-earlier-regular-file')
                if resolved_target == dest:
                    raise BoundaryError('self-link')
        except BoundaryError as error:
            reason = str(error)
        rows.append({'index': index, 'member': name, 'kind': kind, 'destination': dest, 'state': 'hazard' if reason else 'within-model', 'reason': reason, 'trace': trace})
        # Preserve even outward link declarations in the virtual model, so a
        # later write through one has an explicit chain witness. No real node
        # or file is created. Rejected overwrites do not replace earlier nodes.
        if dest and dest not in nodes and kind in ('file', 'dir', 'symlink', 'hardlink'):
            if kind in ('symlink', 'hardlink'):
                try:
                    parts(target)
                except BoundaryError:
                    continue
            nodes[dest] = {'kind': kind, 'target': target}
    return {'schema': 'tar-link-boundary/v1', 'members': rows, 'hazards': sum(r['state'] == 'hazard' for r in rows),
            'limits': 'Virtual empty POSIX root, ordered links, no extraction; conservative duplicate/special-member rejection. Not a proof for any extractor, existing destination, permissions, race, Windows, sparse or compressed archive.'}


def read_tar(path):
    p = Path(path)
    if not p.is_file() or p.stat().st_size > 64 * 1024 * 1024:
        raise ValueError('TAR must be a regular file no larger than 64 MiB')
    events = []
    raw = p.read_bytes()
    if len(raw) > 64 * 1024 * 1024:
        raise ValueError('TAR grew beyond 64 MiB')
    with tarfile.open(fileobj=io.BytesIO(raw), mode='r:') as archive:
        for member in archive:
            if len(events) == 10000:
                raise ValueError('TAR exceeds 10000 members')
            kind = ('file' if member.isfile() else 'dir' if member.isdir() else 'symlink' if member.issym() else 'hardlink' if member.islnk() else 'special')
            events.append({'name': member.name, 'kind': kind, 'target': member.linkname if kind in ('symlink', 'hardlink') else None})
    return events, hashlib.sha256(raw).hexdigest()


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('tar')
    args = p.parse_args()
    try:
        events, digest = read_tar(args.tar)
        result = analyze(events)
        result['archive_sha256'] = digest
        print(json.dumps(result, indent=2, sort_keys=True))
        return 1 if result['hazards'] else 0
    except (ValueError, TypeError, KeyError, OSError, tarfile.TarError) as error:
        print('error: ' + str(error), file=sys.stderr)
        return 2


if __name__ == '__main__':
    raise SystemExit(main())
