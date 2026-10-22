"""Durable private compiler inputs, append-only phases, and SHA gates.

Only NEW task-owned paths are created. Inputs are written once, fsynced and
read-hashed before sealing. No cleanup removes a failed run or its originals.
"""
import hashlib,json,os,shutil,subprocess,time
from pathlib import Path

MAX_BYTES=64*2**20
RESERVE_BYTES=2*2**30


def sha(path):return hashlib.sha256(path.read_bytes()).hexdigest()
def encoded(data):return (json.dumps(data,indent=2,allow_nan=False)+'\n').encode()


class Archive:
    def __init__(self,path,*,create=False,repo=None,maximum_bytes=MAX_BYTES,reserve_bytes=RESERVE_BYTES):
        self.root=Path(path).resolve();self.maximum_bytes=maximum_bytes;self.reserve_bytes=reserve_bytes;self.records={}
        if repo is not None and self.root.is_relative_to(Path(repo).resolve()):raise ValueError('Proprietary baseline must be outside Git checkout')
        if Path(path).is_symlink():raise ValueError('Private archive cannot be a symlink')
        if create:
            self.root.parent.mkdir(parents=True,exist_ok=True,mode=0o700);self.root.mkdir(mode=0o700);self.capacity()
        elif not self.root.is_dir():raise FileNotFoundError(self.root)

    def capacity(self):
        used=sum(p.stat().st_size for p in self.root.rglob('*')if p.is_file());free=shutil.disk_usage(self.root).free
        if used>self.maximum_bytes or free<self.reserve_bytes:raise RuntimeError('Private-run budget/reserve exhausted; files retained')
        return {'used_bytes':used,'maximum_bytes':self.maximum_bytes,'free_bytes':free,'reserve_bytes':self.reserve_bytes}

    def path(self,name):
        relative=Path(name)
        if relative.is_absolute()or '..'in relative.parts:raise ValueError('Archive-relative path required')
        p=self.root/relative
        if not p.resolve().is_relative_to(self.root):raise ValueError('Archive path escapes private root')
        return p

    def write(self,name,data,*,mode=0o600):
        if not isinstance(data,bytes):raise TypeError('Exact persisted bytes required')
        p=self.path(name);p.parent.mkdir(parents=True,exist_ok=True,mode=0o700)
        if sum(v['bytes']for v in self.records.values())+len(data)>self.maximum_bytes:raise RuntimeError('Input budget exceeded before write')
        fd=os.open(p,os.O_WRONLY|os.O_CREAT|os.O_EXCL,mode)
        with os.fdopen(fd,'wb')as f:f.write(data);f.flush();os.fsync(f.fileno())
        return p

    def input(self,name,data,role):
        p=self.write(name,data,mode=0o400);record={'sha256':sha(p),'bytes':p.stat().st_size,'role':role}
        if record['sha256']!=hashlib.sha256(data).hexdigest():raise RuntimeError('Persisted input bytes differ')
        self.records[name]=record;return p

    def seal(self,details):
        result=dict(details,files=self.records,capacity_at_seal=self.capacity(),sealed_before_compilation=True)
        return self.write('prepared.private.json',encoded(result),mode=0o400)

    def manifest(self):return json.loads(self.path('prepared.private.json').read_text())

    def verify(self,products=None):
        m=self.manifest()
        for name,record in m['files'].items():
            p=self.path(name)
            if p.is_symlink()or sha(p)!=record['sha256']or p.stat().st_size!=record['bytes']:raise RuntimeError('Sealed input changed: '+name)
        for name,record in (products or{}).items():
            if sha(self.path(name))!=record['sha256']:raise RuntimeError('Compiled/loaded product changed: '+name)
        return {'sealed_manifest_sha256':sha(self.path('prepared.private.json')),'input_files_verified':len(m['files']),'products_verified':len(products or{}),'all_SHA_match':True,'capacity':self.capacity()}

    def proof(self,name,products=None):
        data=self.verify(products);p=self.write('proofs/'+name+'.json',encoded(data),mode=0o400)
        return {'name':name,'sha256':sha(p),**{k:v for k,v in data.items()if k!='capacity'}}

    def redact(self,args):return [str(v).replace(str(self.root),'<private_run>')for v in args]


def compiler_identity(archive,compiler):
    compiler=compiler.resolve();before=sha(compiler);p=subprocess.run([str(compiler),'--version'],capture_output=True,timeout=15)
    out=archive.input('tool/clang-version.stdout',p.stdout,'compiler version stdout');err=archive.input('tool/clang-version.stderr',p.stderr,'compiler version stderr')
    if p.returncode or sha(compiler)!=before:raise RuntimeError('Compiler identity unavailable or changed')
    return {'resolved_path':str(compiler),'sha256':before,'version_first_line':p.stdout.decode(errors='replace').splitlines()[0],'version_stdout_sha256':sha(out),'version_stderr_sha256':sha(err)}


def compile_saved(archive,compiler,files,product,label):
    m=archive.manifest();identity=m['compiler']
    if str(compiler.resolve())!=identity['resolved_path']or sha(compiler.resolve())!=identity['sha256']:raise RuntimeError('Compiler differs from sealed identity')
    for name in files:
        if name not in m['files']or not name.startswith('inputs/'):raise ValueError('Compiler must read sealed input files only')
    archive.path(product).parent.mkdir(parents=True,exist_ok=True,mode=0o700)
    if archive.path(product).exists():raise FileExistsError('Do not overwrite an existing compiled artifact')
    pre=archive.proof('before-'+label);args=[str(compiler),'-target','arm64-apple-macos27.0','-Wno-override-module','-v','-dynamiclib',*[str(archive.path(n))for n in files],'-o',str(archive.path(product))];begin=time.perf_counter();p=subprocess.run(args,capture_output=True,timeout=30)
    stdout=archive.write('logs/'+label+'.stdout',p.stdout);stderr=archive.write('logs/'+label+'.stderr',p.stderr);post=archive.proof('after-'+label)
    record={'label':label,'argv_redacted':archive.redact(args),'argv_sha256':hashlib.sha256(encoded(args)).hexdigest(),'compiler_sha256':identity['sha256'],'reads_only_persisted_inputs':True,'input_files':files,'stdout_sha256':sha(stdout),'stderr_sha256':sha(stderr),'exit_code':p.returncode,'elapsed_seconds':time.perf_counter()-begin,'pre_input_proof':pre,'post_input_proof':post}
    archive.write('commands/'+label+'.json',encoded(dict(record,actual_argv=args)),mode=0o400)
    if p.returncode:raise RuntimeError('Compilation failed; all sources, command and logs retained')
    record['product']={'name':product,'sha256':sha(archive.path(product)),'bytes':archive.path(product).stat().st_size};return record
