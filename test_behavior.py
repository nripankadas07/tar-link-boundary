import io
import tempfile
from pathlib import Path
import tarfile
import unittest
from tar_link_boundary import analyze, read_tar


def e(name,kind='file',target=None):return {'name':name,'kind':kind,'target':target}


class Tests(unittest.TestCase):
    def test_regular_nested_empty_root(self):
        self.assertEqual(analyze([e('a','dir'),e('a/f')])['hazards'],0)
    def test_direct_parent_escape(self):
        self.assertEqual(analyze([e('../outside')])['members'][0]['reason'],'parent-escapes-root')
    def test_symlink_then_write_has_chain_witness(self):
        r=analyze([e('a','symlink','..'),e('a/secret')]);self.assertEqual(r['hazards'],2);self.assertEqual(r['members'][1]['trace'][0]['link'],'a')
    def test_inward_link_traversal(self):
        r=analyze([e('dir','dir'),e('link','symlink','dir'),e('link/x')]);self.assertEqual(r['hazards'],0);self.assertEqual(r['members'][2]['destination'],'dir/x')
    def test_dotdot_after_symlink_not_lexical_before(self):
        r=analyze([e('a','symlink','x/y'),e('a/../z')]);self.assertEqual(r['members'][1]['destination'],'x/z')
    def test_hardlink_earlier_file(self):
        self.assertEqual(analyze([e('base'),e('h','hardlink','base')])['hazards'],0)
    def test_hardlink_forward_reference_conservative(self):
        self.assertEqual(analyze([e('h','hardlink','future'),e('future')])['hazards'],1)
    def test_link_cycle_no_hang(self):
        r=analyze([e('a','symlink','b'),e('b','symlink','a'),e('a/f')]);self.assertEqual(r['members'][-1]['reason'],'link-cycle-or-depth-limit')
    def test_hardlink_escape_through_symlink_chain(self):
        r=analyze([e('a/b/c/up','symlink','../..'),e('a/b/escape','symlink','c/up/../..'),e('exfil','hardlink','a/b/escape/synthetic')]);self.assertEqual(r['hazards'],2);self.assertEqual(r['members'][-1]['reason'],'parent-escapes-root');self.assertEqual([t['link'] for t in r['members'][-1]['trace']],['a/b/escape','a/b/c/up'])
    def test_duplicates_and_non_directory_parent(self):
        r=analyze([e('a'),e('a'),e('a/f')]);self.assertEqual([x['reason'] for x in r['members'][1:]],['duplicate-or-overwrite-unsupported','non-directory-parent'])
    def test_special_and_platform_paths(self):
        self.assertEqual(analyze([e('dev','special'),e('C:foo'),e('a\\b'),e('/abs')])['hazards'],4)
    def test_actual_tar_metadata_without_extracting(self):
        with tempfile.TemporaryDirectory() as d:
            path=Path(d)/'sample.tar'
            with tarfile.open(path,'w') as t:
                info=tarfile.TarInfo('base');info.size=3;t.addfile(info,io.BytesIO(b'abc'))
                info=tarfile.TarInfo('link');info.type=tarfile.SYMTYPE;info.linkname='../outside';t.addfile(info)
            events,digest=read_tar(path);self.assertEqual(analyze(events)['hazards'],1);self.assertEqual(len(digest),64);self.assertEqual(list(Path(d).iterdir()),[path])
    def test_malformed_tar_and_event_limit(self):
        with tempfile.TemporaryDirectory() as d:
            path=Path(d)/'bad.tar';path.write_bytes(b'not tar')
            with self.assertRaises(tarfile.TarError):read_tar(path)
        with self.assertRaises(ValueError):analyze([e('x')]*10001)


if __name__=='__main__':unittest.main()
