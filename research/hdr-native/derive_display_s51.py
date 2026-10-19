"""Change only input bindings and contact layout in the frozen S47 recipe."""
import ast,hashlib
def derive(template,case):
    prefix=template.split("files=[{'path':str(p.relative_to(PRIVATE))",1)
    assert len(prefix)==2
    original=prefix[0]
    swaps=[
      ("PHOTO=R/'research/vm-native/samples/IMG_2600.HEIC'",f"PHOTO=R/{case['source_path']!r}"),
      ("SOURCE_SHA='63872222783e757a41a41337b48875e1172e68ace0f6e411db999c77b027a4d0'",f"SOURCE_SHA={case['source_sha256']!r}"),
      ("ZIP_SHA='897065d3ea71e3068f2af8ee98ef8745065b923c6692f0366d98cd1b3069d621'",f"ZIP_SHA={case['ZIP_sha256']!r}"),
      ("CIPHER_SHA='d1c3d9beabec857f972f897a7ef91f0fbee8df8d9ab270c7f97949235ae30c86'",f"CIPHER_SHA={case['cipher_sha256']!r}"),
      ("EXR_SHA='69c553e49f3c70ffbebc6e85d32ad6933fe3582535088dd24f60f59c398c4634'",f"EXR_SHA={case['master_EXR_sha256']!r}"),
      ("['IMG_2600-full.tar.gz.gpg']",repr([case['cipher_member']])),
      ("'b846859e6e5bcdc82921c4038aa7863c96dacc27245020953eff0bb6f10f0014'",repr(case['old_logmap_EXR_sha256'])),
      ("'artifact_id':'12188060302'",f"'artifact_id':{str(case['artifact_id'])!r}"),
      ("'sample':'IMG_2600 development case, not a new holdout'",f"'sample':{(case['photo']+' '+case['role']+' for frozen S44/S47 HDR display intent')!r}"),
      ("'photo':'IMG_2600'",f"'photo':{case['photo']!r}"),
      ("==(5712,4284)",f"==({case['shape'][1]},{case['shape'][0]})"),
      ('copy.thumbnail((320,240))','copy.thumbnail((240,180))'),
      ('(cols*320,rows*268)','(cols*240,rows*208)'),
      ('x=(n%cols)*320;y=(n//cols)*268','x=(n%cols)*240;y=(n//cols)*208'),
      ('(x+2,y+244)','(x+2,y+184)'),
    ]
    changed=original
    for old,new in swaps:
        assert changed.count(old)==1,old
        changed=changed.replace(old,new)
    inverse=changed
    for old,new in reversed(swaps):
        assert inverse.count(new)==1,new
        inverse=inverse.replace(new,old)
    assert inverse==original,'Mathematical recipe changed outside allowed input/layout substitutions'
    # Contact collection/encryption is done once by S51. Individual PNGs remain
    # temporary on runner; their input-SHA checks remain in per-case analysis.
    changed+='\nprint("S51 frozen display case complete")\n'
    ast.parse(changed)
    return changed,{'original_template_sha256':hashlib.sha256(template.encode()).hexdigest(),'derived_script_sha256':hashlib.sha256(changed.encode()).hexdigest(),'inverse_binding_and_layout_substitutions_equal_original_prefix':True,'mathematical_processing_changed':False,'new_preview_layout':'3 columns,240x180 contact cells; pixel processing and original preview samples unchanged','original_encryption_footer_replaced_by':'Parent runner seals only contact and meaning for bounded archival; no individual photo PNG uploaded'}
