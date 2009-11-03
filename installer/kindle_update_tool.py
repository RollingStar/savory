#!/usr/bin/python
# Kindle Firmware Update tool v0.4 Copyright (c) 2009 Igor Skochinsky & Jean-Yves Avenard
# History:
#  2009-03-10 Initial release
#  2009-10-22 Update for K2 International support
#  2009-10-30 Add conversion from gzip tar to OTA update file, add signature of files for K2 International
#  2009-11-01 Use hashlib instead of obsolete md5
#             Add ability to install package without first installing the freekindle-k2i package.

import tarfile, gzip, array, hashlib, sys, struct
from binascii import hexlify
import os, subprocess
import random, tempfile

## For Kindle 2 International Only

BASE_CMD = "openssl dgst -sha256 "
CMD_SIGN = BASE_CMD + "-sign %(privkey)s -out %(outfile)s %(infile)s"
KINDLE_HACK_DIR = "/etc/uks"
KINDLE_HACK_KEYNAME = "pubprodkey01.pem"
SIGN_KEY = """
-----BEGIN RSA PRIVATE KEY-----
MIICXgIBAAKBgQDJn1jWU+xxVv/eRKfCPR9e47lPWN2rH33z9QbfnqmCxBRLP6mM
jGy6APyycQXg3nPi5fcb75alZo+Oh012HpMe9LnpeEgloIdm1E4LOsyrz4kttQtG
RlzCErmBGt6+cAVEV86y2phOJ3mLk0Ek9UQXbIUfrvyJnS2MKLG2cczjlQIDAQAB
AoGASLym1POD2kOznSERkF5yoc3vvXNmzORYkRk1eJkJuDY6yAbYiO7kDppqj4l8
wGogTpv98OMXauY8JgQj6tgO5LkY2upttukDr8uhE2z9Dh7HMZV/rDYa+9rybJus
RiAQDmF+VCzY2HirjpsSzgRu0r82NC8znNm2eGORys9BvmECQQDoIokOr0fYz3UT
SbHfD3engXFPZ+JaJqU8xayR7C+Gp5I0CgSnCDTQVgdkVGbPuLVYiWDIcEaxjvVr
hXYt2Ac9AkEA3lnERgg0RmWBC3K8toCyfDvr8eXao+xgUJ3lNWbqS0HtwxczwnIE
H49IIDojbTnLUr3OitFMZuaJuT2MtWzTOQJBAK6GCHU54tJmZqbxqQEDJ/qPnxkM
CWmt1F00YOH0qGacZZcqUQUjblGT3EraCdHyFKVT46fOgdfMm0cTOB6PZCECQQDI
s5Zq8HTfJjg5MTQOOFTjtuLe0m9sj6zQl/WRInhRvgzzkDn0Rh5armaYUGIx8X0K
DrIks4+XQnkGb/xWtwhhAkEA3FdnrsFiCNNJhvit2aTmtLzXxU46K+sV6NIY1tEJ
G+RFzLRwO4IFDY4a/dooh1Yh1iFFGjcmpqza6tRutaw8zA==
-----END RSA PRIVATE KEY-----
"""

NEW_KEY = """
-----BEGIN PUBLIC KEY-----
MIGfMA0GCSqGSIb3DQEBAQUAA4GNADCBiQKBgQDJn1jWU+xxVv/eRKfCPR9e47lP
WN2rH33z9QbfnqmCxBRLP6mMjGy6APyycQXg3nPi5fcb75alZo+Oh012HpMe9Lnp
eEgloIdm1E4LOsyrz4kttQtGRlzCErmBGt6+cAVEV86y2phOJ3mLk0Ek9UQXbIUf
rvyJnS2MKLG2cczjlQIDAQAB
-----END PUBLIC KEY-----
"""

INSTALL_SCRIPT = """
#!/bin/sh

_FUNCTIONS=/etc/rc.d/functions
[ -f ${_FUNCTIONS} ] && . ${_FUNCTIONS}

. /etc/sysconfig/mntus

update_progressbar 50

#Restore original Kindle signing key
cat > /etc/uks/pubprodkey01.pem <<EOF
-----BEGIN PUBLIC KEY-----
MIGfMA0GCSqGSIb3DQEBAQUAA4GNADCBiQKBgQCxfpiZ1dbdSOgrikqXD6lESUrD
5l52nN50iMh2vDcmW/FzkPDv0eRf1ci6w3ifhmHwqDK9OYNnowPapzUHAiHukXjW
rOC3fZYzgAxzIPN4NyUw369zFK2AALZnXptc68D/xxtZ94porf+kLtw/4vF2NhHs
XtchrpvID+Jhkor8MQIDAQAB
-----END PUBLIC KEY-----
EOF

update_progressbar 100

return 0
"""

if sys.hexversion >= 0x3000000:
  print "This script is incompatible with Python 3.x. Please install Python 2.6.x from python.org"
  sys.exit(2)

def dm(s):
  arr = array.array('B',s)
  for i in xrange(len(arr)):
    b = arr[i]^0x7A
    arr[i] = (b>>4 | b<<4)&0xFF
  return arr.tostring()

def md(s): #opposite of dm
  arr = array.array('B',s)
  for i in xrange(len(arr)):
    b = arr[i]
    b = (b>>4 | b<<4)&0xFF
    arr[i] = b^0x7A
  return arr.tostring()

def s_md5(s): #return md5 in string format
  m = hashlib.md5()
  m.update(s)
  return hexlify(m.digest())

def runCommand(cmd):
    """wrapper to simplify the execution of external programs.
    @param cmd: Command line to be executed
    @type cmd: string

    @return: tuple (exit code, stdout, stderr).
    @rtype: tuple
    """
    ssl = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    status = ssl.wait()
    out, err = ssl.communicate()
    return status, out, err

def extract_bin(binname):
    f = file(binname, "rb")
    sig, fromVer, toVer, devCode, optional = struct.unpack("<4sIIHBx", f.read(16))
    
    if sig=="FC02":
      typ="OTA update"
    elif sig=="FB01":
      typ="Manual update"
    else:
      print "Not a Kindle update file!"
      return

    print "Signature: %s (%s)"%(sig,typ)
    if sig=="FC02":
      print "min version: %d"%(fromVer)
      print "max version: %d"%(toVer)
      print "device code: %d%d"%divmod(devCode,256)
      print "optional: "+("yes" if optional else "no")
    print "md5 of tgz: %s"%dm(f.read(32))
    if sig=="FC02":
    	f.seek(64)
    elif sig=="FB01":
        f.seek(131072)
    file(binname+".tgz","wb").write(dm(f.read()))

def add_tarfile(tarinfo, file, tar, mode=0100644):
    tarinfo.mode = mode
    tarinfo.uid = tarinfo.gid = 0
    tarinfo.uname = tarinfo.gname = "root"
    file.seek(0)
    tar.addfile(tarinfo, file)

def create_sig(keyfile, name, tar, finalname=''):
    sigfile = tempfile.NamedTemporaryFile()
    cmd = CMD_SIGN % { 'privkey': keyfile.name,
                       'outfile': sigfile.name,
                       'infile': name}
    #print 'cmd = %s' % cmd
    status = runCommand(cmd)
    if status[0] != 0:
        raise ValueError("Openssl failed")
    # Add signature file
    if finalname == '':
        finalname = name
    tarinfo = tar.gettarinfo(sigfile.name, arcname=finalname+'.sig')
    add_tarfile(tarinfo, sigfile, tar)
    sigfile.close()

def make_bin(basename, filelist, type, kver):
    tgz_fname = tempfile.NamedTemporaryFile()
    tar = tarfile.open(tgz_fname.name,"w:gz")

    dat_list = ""
    jailbreak = 0
    
    if kver == 3 or kver == 32:
        keyfile = tempfile.NamedTemporaryFile()
        keyfile.write(SIGN_KEY)
        keyfile.flush()

    if kver == 32:
        kver = 3
        jailbreak = 1
        random.seed()
        
        # Create fake symlink
        namedir = '__dir' + str(random.randint(1000,9999))
        tarinfo = tarfile.TarInfo(namedir)
        tarinfo.type = tarfile.SYMTYPE
        tarinfo.linkname = KINDLE_HACK_DIR
        tar.addfile(tarinfo)
        
        # Create new key
        tmpfile = tempfile.NamedTemporaryFile()
        tmpfile.write(NEW_KEY)
        tmpfile.flush()
        tarinfo = tar.gettarinfo(tmpfile.name, arcname=namedir+'/'+KINDLE_HACK_KEYNAME)
        add_tarfile(tarinfo, tmpfile, tar)
        tmpfile.close()
        
        # Create additional install script
        nameinstall = '_install' + str(random.randint(1000,9999)) + '.sh'
        tmpinstall = tempfile.NamedTemporaryFile()
        tmpinstall.write(INSTALL_SCRIPT)
        tmpinstall.flush()
        tarinfo = tar.gettarinfo(tmpinstall.name, arcname=nameinstall)
        add_tarfile(tarinfo, tmpinstall, tar)
        tmpinstall.seek(0)
        create_sig(keyfile, tmpinstall.name, tar, finalname=nameinstall)
        
        # Creating extra script signature

    if kver == 3:   # Kindle 2 International

        for name in filelist:
            print "calculating signature for %s" % name
            create_sig(keyfile, name, tar)
        keyfile.close()        

    for name in filelist:
        print "adding %s"%name
        tarinfo = tar.gettarinfo(name)
        if name.endswith(".sh"):
            mode = 0100755 #rwxr-xr-x
            fid = 129
        else:
            mode = 0100644 #rw-r--r--
            fid = 128
        inf = file(name,"rb")
        add_tarfile(tarinfo, inf, tar, mode)

        #129 a2592fe6898d468fd64f00c5b4b04ad7 test.sh 0 Test_script
        if not name.endswith(".sig"):
            inf.seek(0)
            dat_list+="%d %s %s 0 %s\n"%(fid, s_md5(inf.read()), name, name+"_file")

    if jailbreak == 1:
        tmpinstall.seek(0)
        dat_list+="%d %s %s 0 %s\n"%(129, s_md5(tmpinstall.read()), nameinstall, nameinstall+"_file")
        tmpinstall.close()
    if kver == 3:
        keyfile.close()

    tmpdat = tempfile.NamedTemporaryFile()
    tmpdat.write(dat_list)
    tmpdat.flush()
    tmpdat.seek(0)
    tarinfo = tar.gettarinfo(tmpdat.name, arcname=basename+'.dat')
    add_tarfile(tarinfo, tmpdat, tar)
    
    tar.close()

    convert_bin(basename, tgz_fname.name, type, kver)

    tgz_fname.close()
    
def convert_bin(basename, tgz_fname, type, kver):
    print "making bin file"
    if type==2:
      BLOCK_SIZE=64
      sig = "FC02"
    else:
      BLOCK_SIZE=131072
      sig = "FB01"

    f = file(tgz_fname, "rb").read()
    of = file(basename+".bin","wb")
    #C4 1D 3C 07 C2 B5 A0 08
    header = struct.pack("<4sIIHBB", sig, 0x0, 0x7fffffff, kver, 0, 0x13) #signature, fromVer, toVer, devCode, optional
    of.write(header)
    of.write(md(s_md5(f)))
    of.write("\0"*(BLOCK_SIZE - of.tell()))
    of.write(md(f))
    print "output written to "+basename+".bin"

def usage():
  print """Usage:
    kindle_update_tool.py e update_mmm.bin
      Extract a Kindle or Kindle 2 firmware update file. Outputs a .tgz file with decrypted content.

    kindle_update_tool.py m [flags] name file1 [file2 ...]
      Where flags is one of the following: -k2 , -k2i, -k2iex -k3
      Makes a Kindle DX, Kindle 2 (-k2), Kindle 2 International (-k2i|-k2iex) or Kindle DX (-k3)
      OTA firmware update file from the list of files.
      "name" is the update file suffix (final file will be called update_name.bin).
      Any file with .sh extension will be marked as a shell script to be executed.
      If using -k2iex, the generated package will install without the need to first install new RSA keys
      to the kindle (also called jailbreaking).
      It is imperative that the install script works 100%. As should they fail, it could leave your kindle
      in a corrupted state preventing to install future official Amazon updates.
      Installing update_freekindle-k2i.bin would fix it.

    kindle_update_tool.py c [-k2|-k2i|-k3] name tarname]
      Convert a GZIPPED TAR file into a Kindle DX, Kindle 2 (-k2), Kindle 2 International (-k2i)
      or Kindle DX (-k3) OTA firmware update file.
      "name" is the update file suffix (final file will be called update_name.bin)."""
  
print "Kindle Firmware Update tool v0.4 Copyright (c) 2009 Igor Skochinsky & Jean-Yves Avenard"

if len(sys.argv)<3:
  usage()
elif sys.argv[1]=="e":
  extract_bin(sys.argv[2])
elif sys.argv[1]=="c":
  kver = 1
  if sys.argv[2] in ["-k2", "-k2i", "-k3"]:
    kver =2
  name = sys.argv[kver+1]
  tarname = sys.argv[kver+2]
  if sys.argv[2]=="-k2i": 
    kver = 3
  if sys.argv[2]=="-k3": 
    kver = 4
  convert_bin("update_"+name, tarname, 2, kver)
elif sys.argv[1]=="m":
  kver = 1
  if sys.argv[2] in ["-k2", "-k2i", "-k2iex", "-k3"]:
    kver = 2
  name = sys.argv[kver+1]
  filelist = sys.argv[kver+2:]
  if sys.argv[2]=="-k2i":
    kver = 3
  if sys.argv[2]=="-k2iex":
    kver = 32
  if sys.argv[2]=="-k3": 
    kver = 4
  make_bin("update_"+name, filelist, 2, kver)
else:
  usage()
