"""Read only preserved bounded gzip prefixes; no full archive acquisition."""
import hashlib,io,json,tarfile
from pathlib import Path
from sources import ROOT


class Concatenated(io.RawIOBase):
    def __init__(self,paths):self.files=[p.open('rb') for p in paths];self.index=0
    def readable(self):return True
    def readinto(self,buffer):
        while self.index<len(self.files):
            n=self.files[self.index].readinto(buffer)
            if n:return n
            self.index+=1
        return 0
    def close(self):
        for f in self.files:f.close()
        super().close()


if __name__=='__main__':
    paths=[ROOT/'source_evidence/secondary_test_64MiB_prefix.bin',ROOT/'source_evidence/secondary_test_64_to256MiB.bin']
    entries=[];metadata=[];ended=None
    try:
        with tarfile.open(fileobj=io.BufferedReader(Concatenated(paths)),mode='r|gz') as archive:
            for member in archive:
                entries.append({'name':member.name,'bytes':member.size})
                if member.isfile() and member.size<1_000_000 and member.name.endswith(('.json','.txt','.yaml','.csv')):
                    raw=archive.extractfile(member).read();metadata.append({'name':member.name,'bytes':len(raw),'sha256':hashlib.sha256(raw).hexdigest(),'text':raw.decode(errors='replace')})
    except (EOFError,tarfile.ReadError) as exc:ended=str(exc)
    result={'compressed_bytes_examined':sum(p.stat().st_size for p in paths),'archive_complete':False,'expected_prefix_end':ended,'entries_seen':len(entries),'metadata_members':metadata}
    (ROOT/'checks/secondary_bounded_native_audit.json').write_text(json.dumps(result,indent=2)+'\n')
    (ROOT/'checks/secondary_256MiB_member_listing.json').write_text(json.dumps(entries,indent=2)+'\n')
    print('Secondary bounded entries',len(entries),'native metadata records',len(metadata));print(metadata[:5])
