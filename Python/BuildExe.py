import PyInstaller.__main__
import shutil
import os
import stat

def remove_readonly(func, path, exc_info):
    "Clear the readonly bit and reattempt the removal"
    # ERROR_ACCESS_DENIED = 5
    if func not in (os.unlink, os.rmdir) or exc_info[1].winerror != 5:
        raise exc_info[1]
    os.chmod(path, stat.S_IWRITE)
    func(path)


filename = "automateRecon.py"
exename = "ReconAutomation.exe"
icon = "scan.ico"
pwd = os.getcwd()

if os.path.isfile(exename):
    os.remove(exename)

# Create executable from Python script
PyInstaller.__main__.run([
    "automateRecon.py",
    "--onefile",
    "--clean",
    "--log-level=ERROR",
    "--name="+exename,
    "--icon="+icon
])

# Clean up after Pyinstaller
def remove_readonly(func, path, exc_info):
    "Clear the readonly bit and reattempt the removal"
    # ERROR_ACCESS_DENIED = 5
    if func not in (os.unlink, os.rmdir) or exc_info[1].winerror != 5:
        raise exc_info[1]
    os.chmod(path, stat.S_IWRITE)
    func(path)

shutil.move(os.path.join(pwd,"dist",exename),pwd)
shutil.rmtree("dist", onerror=remove_readonly)
shutil.rmtree("build", onerror=remove_readonly)
shutil.rmtree("__pycache__", onerror=remove_readonly)
shutil.rmtree(exename+".spec", onerror=remove_readonly)