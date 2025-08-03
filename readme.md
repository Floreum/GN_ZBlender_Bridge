This is an alternative to using GoB addon for Linux users that are running ZBrush through Wine.
It requires the paid addon GN ZBrush/Maya: https://www.artstation.com/marketplace/p/8vPd/gn-zbrush-maya-import-export-tool
All you have to do once obtained is install the ZBrush script, then download this script in the releases section and install that into Blender.
For now there is no easy way to set this via your preferences but that is planned eventually.
For now you can go into the __init__.py file and change FILE_PATH = "/home/floreum/Games/zbrush_2022-0-8/drive_c/temp/" to where your Zbrush temp folder is.
I recommend exporting from the ZBrush plugin first to see where this folder gets created, but it should be in your "drive_c/temp" folder for your zbrush Wine directory.

How this currently works in Blender is you can go to File > ZBrush Import
You can do two things, just import with nothing selector or select the object you want to replace and it'll swap its mesh data and try to keep the shapekeys on the object so as long as the object is still the same polycount. Multi import is also supported, it will detect if the folder exists in the temp directory and import that instead. After importing it will delete the files.
