# -*- mode: python ; coding: utf-8 -*-

block_cipher = None


a = Analysis(['/Users/wen/PycharmProjects/Pipeline_ProxyConverter/main.py'],
             pathex=['/Users/wen'],
             binaries=[],
             datas=[],
             hiddenimports=[],
             hookspath=[],
             runtime_hooks=[],
             excludes=[],
             win_no_prefer_redirects=False,
             win_private_assemblies=False,
             cipher=block_cipher,
             noarchive=False)
pyz = PYZ(a.pure, a.zipped_data,
             cipher=block_cipher)
exe = EXE(pyz,
	  Tree('data', prefix='data'),
          a.scripts,
          a.binaries,
          a.zipfiles,
          a.datas,
          [],
          name='GUI',
          debug=False,
          bootloader_ignore_signals=False,
          strip=False,
          upx=True,
          upx_exclude=[],
          runtime_tmpdir=None,
          console=False )
app = BUNDLE(exe,
	     Tree('data', prefix='data'),
             name='ConvertTo.app',
             icon=None,
             bundle_identifier=None)
