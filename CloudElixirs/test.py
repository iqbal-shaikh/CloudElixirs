from os import walk
import os, shutil

cwd = os.getcwd()
filelist = os.path.join(cwd, "file_to_send")
sentfile = os.path.join(cwd, "files_sent")
audiofile = []
for (dirpath, dirnames, filenames) in walk(filelist):
    for file in filenames:
        currentfile = os.path.join(filelist, file)
        audiofile.append(currentfile)
        shutil.move(currentfile, sentfile)
#     break

print("Files :", audiofile)
print(sentfile)


