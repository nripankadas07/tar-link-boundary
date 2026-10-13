import io
import json
from pathlib import Path
import shutil
import subprocess
import tarfile
import tempfile


def main():
    command=shutil.which('tar-link-boundary')
    assert command, 'install the console command first'
    with tempfile.TemporaryDirectory() as d:
        path=Path(d)/'synthetic.tar'
        with tarfile.open(path,'w') as archive:
            info=tarfile.TarInfo('link');info.type=tarfile.SYMTYPE;info.linkname='..';archive.addfile(info)
            info=tarfile.TarInfo('link/outside');info.size=3;archive.addfile(info,io.BytesIO(b'abc'))
        run=subprocess.run([command,str(path)],cwd=d,capture_output=True,text=True)
        assert run.returncode==1,run.stderr
        report=json.loads(run.stdout);assert report['hazards']==2
        assert report['members'][1]['trace'][0]['link']=='link'
        assert list(Path(d).iterdir())==[path], 'diagnostic extracted something'
        print(json.dumps(report,indent=2))
        path.write_bytes(b'not a tar')
        failed=subprocess.run([command,str(path)],cwd=d,capture_output=True,text=True)
        assert failed.returncode==2 and failed.stderr.startswith('error:'),failed


if __name__=='__main__':main()
