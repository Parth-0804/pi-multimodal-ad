"""Inspect official ZIP directory using HTTP ranges, never download full ZIP."""
import io
import json
import zipfile
from acquisition import ROOT, acquire


class RemoteArchive(io.RawIOBase):
    def __init__(self, length):
        self.length=length
        self.position=0

    def seekable(self): return True
    def readable(self): return True
    def tell(self): return self.position
    def seek(self, offset, whence=0):
        self.position = offset if whence==0 else self.position+offset if whence==1 else self.length+offset
        if not 0 <= self.position <= self.length:
            raise ValueError('Invalid range')
        return self.position

    def read(self, count=-1):
        count=self.length-self.position if count<0 else min(count,self.length-self.position)
        if count==0: return b''
        if count>30_000_000: raise RuntimeError('Range exceeds metadata budget')
        start=self.position
        end=start+count-1
        path=acquire('http://160.75.159.4/data/failure.zip',f'failure/zip_ranges/{start}_{end}.bin',count+1,f'bytes={start}-{end}')
        data=path.read_bytes()
        assert len(data)==count
        self.position+=len(data)
        return data


if __name__=='__main__':
    head=json.loads((ROOT/'checks/failure_archive_head.json').read_text())
    with zipfile.ZipFile(RemoteArchive(int(head['headers']['Content-Length']))) as archive:
        rows=[{'name':i.filename,'bytes':i.file_size,'compressed_bytes':i.compress_size,'crc32':f'{i.CRC:08x}','header_offset':i.header_offset} for i in archive.infolist()]
        (ROOT/'checks/failure_archive_inventory.json').write_text(json.dumps(rows,indent=2)+'\n')
        print('ZIP entries',len(rows),'uncompressed bytes',sum(x['bytes'] for x in rows))
        print('First entries',rows[:20])
