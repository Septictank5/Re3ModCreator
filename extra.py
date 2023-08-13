import os

directory = 'C:/Users/amish_ac2c1jm/Desktop/New/RDT'
dirs = [f.path for f in os.scandir(directory) if f.is_dir()]
for path in dirs:
    files = [f for f in os.listdir(path + '/PL00/SCRIPT/') if f.endswith('.SCD')]
    with open('SCD/' + path[-4:] + '.SCD', 'wb') as writefile:
        for file in files:
            with open(path + '/PL00/SCRIPT/' + file, 'rb') as readfile:
                data = readfile.read()
            writefile.write(data)
