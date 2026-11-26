"""Read optimizer literal metadata from a torch ZIP pickle without executing it."""
import pickletools
import zipfile


def optimizer_literals(path):
    with zipfile.ZipFile(path) as archive:
        name=next(n for n in archive.namelist() if n.endswith('/data.pkl'))
        operations=list(pickletools.genops(archive.read(name)))
    strings={'SHORT_BINUNICODE','BINUNICODE','UNICODE'}
    starts=[i for i,(op,arg,_) in enumerate(operations) if op.name in strings and arg=='param_groups']
    if not starts:return {}
    result={}
    numeric={'BINFLOAT','FLOAT','BININT','BININT1','BININT2','INT','LONG1','LONG4'}
    keys={'betas','eps','weight_decay','lr','initial_lr','amsgrad','maximize',
          'foreach','capturable','differentiable','fused'}
    for i in range(starts[0],len(operations)):
        op,arg,offset=operations[i]
        if op.name not in strings or arg not in keys or arg in result:continue
        following=[(o,a) for o,a,_ in operations[i+1:i+10] if o.name not in {'MEMOIZE','BINPUT','LONG_BINPUT','PUT'}]
        if arg=='betas':
            values=[a for o,a in following[:3] if o.name in numeric]
            if len(values)==2:result[arg]=values
        elif following:
            item,value=following[0]
            if item.name in numeric:result[arg]=value
            elif item.name in ['NEWTRUE','NEWFALSE']:result[arg]=item.name=='NEWTRUE'
            elif item.name=='NONE':result[arg]=None
    return result
