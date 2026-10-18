"""Export relevant AIR text using an existing LLVM C API; never export Apple binary payloads."""
from pathlib import Path
import ctypes as C,glob,os,sys,re,struct,json,subprocess,hashlib
if len(sys.argv)>2 and sys.argv[1]=='--child':
 lib=C.CDLL(sys.argv[2]);raw=Path(sys.argv[3]).read_bytes();buf=C.create_string_buffer(raw)
 lib.LLVMCreateMemoryBufferWithMemoryRangeCopy.argtypes=[C.c_void_p,C.c_size_t,C.c_char_p];lib.LLVMCreateMemoryBufferWithMemoryRangeCopy.restype=C.c_void_p
 lib.LLVMParseBitcode2.argtypes=[C.c_void_p,C.POINTER(C.c_void_p)];lib.LLVMParseBitcode2.restype=C.c_int
 lib.LLVMPrintModuleToFile.argtypes=[C.c_void_p,C.c_char_p,C.POINTER(C.c_char_p)];lib.LLVMPrintModuleToFile.restype=C.c_int
 memory=lib.LLVMCreateMemoryBufferWithMemoryRangeCopy(buf,len(raw),b'texture-air');module=C.c_void_p();rc=lib.LLVMParseBitcode2(memory,C.byref(module))
 if rc:raise SystemExit(rc)
 error=C.c_char_p();raise SystemExit(lib.LLVMPrintModuleToFile(module,sys.argv[4].encode(),C.byref(error)))
out=Path(sys.argv[1]);out.mkdir(exist_ok=True);candidates=[]
for pattern in ['/Applications/Xcode*.app/Contents/Developer/Toolchains/XcodeDefault.xctoolchain/usr/lib/libLLVM*.dylib','/opt/homebrew/opt/llvm/lib/libLLVM*.dylib','/Library/Developer/CommandLineTools/usr/lib/libLLVM*.dylib']:
 candidates.extend(glob.glob(pattern))
usable=[]
for p in candidates:
 try:
  lib=C.CDLL(p)
  if all(hasattr(lib,n)for n in ['LLVMCreateMemoryBufferWithMemoryRangeCopy','LLVMParseBitcode2','LLVMPrintModuleToFile']):usable.append(p)
 except OSError:pass
source=Path('/System/Library/PrivateFrameworks/CMImaging.framework/Resources/default.metallib');data=source.read_bytes();result={'os_build':'26A434','source_sha256':hashlib.sha256(data).hexdigest(),'existing_llvm_candidates':candidates,'usable_llvm':usable,'downloaded_software_bytes':0,'modules':[]}
temp=Path(os.environ['W'])/'air-tmp';temp.mkdir(exist_ok=True)
for n,m in enumerate(re.finditer(b'\xde\xc0\x17\x0b',data)):
 start=m.start()
 if start+20>len(data):continue
 _,version,offset,size,cpu=struct.unpack_from('<5I',data,start);raw=data[start+offset:start+offset+size]
 if raw[:4]!=b'BC\xc0\xde'or not any(k.lower()in raw.lower()for k in [b'TextureStyle',b'UnderEye',b'Mattify',b'SkinSmoothStandalone']):continue
 row={'module':n,'payload_bytes':size,'payload_sha256':hashlib.sha256(raw).hexdigest()};result['modules'].append(row)
 if not usable:row['status']='existing LLVM C API unavailable; native compiler tool inspection required';continue
 p=temp/f'{n:04d}.bc';p.write_bytes(raw);target=out/f'{n:04d}.ll'
 with(out/f'{n:04d}.log').open('w')as log:
  try:row['returncode']=subprocess.run([sys.executable,__file__,'--child',usable[0],p,target],stdout=log,stderr=subprocess.STDOUT,timeout=30).returncode
  except subprocess.TimeoutExpired:row['returncode']='timeout'
 if target.exists():row['functions']=re.findall(r'^define .*?@(?:"([^"]+)"|([^ (]+))',target.read_text(),re.M)
 p.unlink()
(out/'index.json').write_text(json.dumps(result,indent=2)+'\n')
