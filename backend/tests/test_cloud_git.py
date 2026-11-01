from pathlib import Path
import subprocess
import shutil
import pytest

pytestmark=pytest.mark.skipif(not shutil.which("bash") or not shutil.which("git"),reason="Git/Bash required for cloud publication test")

def git(*args,cwd):
    return subprocess.run(['git',*args],cwd=cwd,check=True,capture_output=True,text=True)

def test_public_state_push_rebases_over_unrelated_concurrent_edit(tmp_path):
    remote=tmp_path/'remote.git';a=tmp_path/'a';b=tmp_path/'b'
    git('init','--bare',str(remote),cwd=tmp_path)
    git('clone',str(remote),str(a),cwd=tmp_path)
    for path in [a]:
        git('config','user.email','fixture@example.org',cwd=path);git('config','user.name','Synthetic fixture',cwd=path)
    git('checkout','-b','main',cwd=a)
    (a/'README.md').write_text('Synthetic initial repo')
    git('add','README.md',cwd=a);git('commit','-m','initial',cwd=a);git('push','-u','origin','main',cwd=a)
    git('clone','-b','main',str(remote),str(b),cwd=tmp_path)
    git('config','user.email','fixture@example.org',cwd=b);git('config','user.name','Synthetic fixture',cwd=b)
    (a/'state.json').write_text('{"synthetic":true}')
    git('add','state.json',cwd=a);git('commit','-m','state',cwd=a)
    (b/'README.md').write_text('Synthetic concurrent edit')
    git('add','README.md',cwd=b);git('commit','-m','human edit',cwd=b);git('push',cwd=b)
    script=Path(__file__).resolve().parents[2]/'cloud/push-state.sh'
    subprocess.run(['bash',str(script),'main'],cwd=a,check=True,capture_output=True,text=True)
    assert git('show','HEAD:README.md',cwd=a).stdout=='Synthetic concurrent edit'
    assert git('show','HEAD:state.json',cwd=a).stdout=='{"synthetic":true}'
