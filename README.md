# Re3ModCreator
Changes various aspects of data within RDT files of RE3: Nemesis

Requires python 3.10 or later.

Requires Pyqt5 (pip install PyQt5).

A separate app must be used to unpack the rdt files from rofs13.dat.  On first launch, a file dialog will appear where you'll select the folder with all the rdt files.  Following that is a create mod input dialog.  Name your mod and a Mods folder will be created in the directory where your rdt files are, and all the rdt's will be copied their.  All edits made will modify these rdt files, leaving the originals intact.  This will create a config.ini.  As long as this config file is in your directory, you won't need to repeat choosing the default directory and can create or open mods from within the app.  If the default rdt directory or mod directory is undiscoverable, this may cause crashes.  An easy solution is to just delete the config.ini file.

The Code viewer portion of the app requires a 'SCD' directory in the root folder of the app.  SCD unpacker utilities i've found have the scd files separated into multiple files.  These must be merged into a single file and named after the room they correspond with (i.e. 'R100.scd').  WIthout these files, the app will crash if you try to open the code viewer.

Currently the editor only changes items.  Mod verification isn't perfect, and doesn't check for whether you have key items to access certain items (for example, 
it doesn't check if you have the wrench for the firehose location item).  Red text is necessary items, yellow text is to address missing optional items or duplicates.

Some items don't appear in the editor for changing.. for example the balls and gold gear in the chronos room.  These items either don't take to changes or have special handling.  As I learn more, i may eventually get these implemented.


