#!/usr/bin/env python3
"""Record a bounded PhotoCraft qualification command and its exact combined output."""
import datetime, json, os, pathlib, subprocess, sys, time
root = pathlib.Path(__file__).resolve().parents[5]
name, cwd, seconds, *command = sys.argv[1:]
out = root / 'docs/reviews/GR-082/checks' / ('photocraft-qualification-' + name + '.txt')
env = os.environ.copy()
env['PATH'] = '/home/roddy/.rustup/toolchains/1.95.0-x86_64-unknown-linux-gnu/bin:' + env['PATH']
env['TMPDIR'] = '/home/roddy/.cache/artcraft-storage-lab/upstream-refresh-sources/photocraft/temp/cargo-tmp'
env['CARGO_BUILD_JOBS'] = '1'
with out.open('w') as log:
    log.write(json.dumps({'command':command,'cwd':cwd,'started':datetime.datetime.now(datetime.timezone.utc).isoformat(),'env':{k:env[k] for k in ['PATH','TMPDIR','CARGO_BUILD_JOBS']}})+'\n'); log.flush()
    p = subprocess.Popen(command,cwd=cwd,env=env,stdout=log,stderr=subprocess.STDOUT,start_new_session=True)
    try: code=p.wait(timeout=int(seconds))
    except subprocess.TimeoutExpired:
        import signal
        os.killpg(p.pid,signal.SIGTERM); p.wait(); code=124
        log.write('\nTIMEOUT: process group terminated at configured bound\n')
    log.write('\nRECORDED_EXIT='+str(code)+'\n')
print(str(out), 'exit', code)
sys.exit(code)
