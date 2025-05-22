# LindoAI_Log.spec
# 用于 pyinstaller 构建 .exe，图标 + 资源自动包含

block_cipher = None

a = Analysis(
    ['main.py'],
    pathex=[],
    binaries=[],
    datas=[
        ('kirin_final.ico', '.'),     # 图标文件
        ('projects.xml', '.'),        # 项目列表配置
        ('logo.png', '.'),            # UI图片
        ('ui.py', '.'),               # UI模块
        ('database.py', '.'),         # 数据模块
        ('export.py', '.'),           # 导出模块
    ],
    hiddenimports=[],
    hookspath=[],
    runtime_hooks=[],
    excludes=[],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
)

pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

exe = EXE(
    pyz,
    a.scripts,
    [],
    exclude_binaries=True,
    name='LindoAI_Log',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    console=False,
    icon='kirin_final.ico'
)

coll = COLLECT(
    exe,
    a.binaries,
    a.zipfiles,
    a.datas,
    strip=False,
    upx=True,
    upx_exclude=[],
    name='LindoAI_Log'
)