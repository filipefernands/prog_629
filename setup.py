from distutils.core import setup
import py2exe,sys,os

setup(console=['main.py'],
      options={
                'py2exe': {
                            'dll_excludes': [
                                    'MSVCP90.dll',
                                    'IPHLPAPI.DLL',
                                    'NSI.dll',
                                    'WINNSI.DLL',
                                    'WTSAPI32.dll',
                                    'SHFOLDER.dll',
                                    'PSAPI.dll',
                                    'MSVCR120.dll',
                                    'MSVCP120.dll',
                                    'CRYPT32.dll',
                                    'GDI32.dll',
                                    'ADVAPI32.dll',
                                    'CFGMGR32.dll',
                                    'USER32.dll',
                                    'POWRPROF.dll',
                                    'MSIMG32.dll',
                                    'WINSTA.dll',
                                    'MSVCR90.dll',
                                    'KERNEL32.dll',
                                    'MPR.dll',
                                    'Secur32.dll',
                             ]
                            }

               }
      )