__author__ = 'benkjohnson'

import imp
import os
import glob
import subprocess

class CheckDependencies(object):
    def __init__(self):
        self._javastate = False
        self._rstate = False
        self._numpystate = False

    def installdependencies(self):
        """Ask the user to install dependencies."""

        javainstall = CheckDependencies.getjavastate(self)
        rinstall = CheckDependencies.getrstate(self)
        numpyinstall = CheckDependencies.getnumpystate(self)

        if javainstall == False:
            print "You need to install Java or put it in your PATH. See tutorial: sparta.readthedocs.org. Quitting."
            quit()
        elif rinstall == False:
            print "You need to install R or put it in your PATH. See tutorial: sparta.readthedocs.org. Quitting."
            quit()
        elif numpyinstall == False:
            print "You need to install NumPy. See tutorial: sparta.readthedocs.org. Quitting."
            quit()

        return

    def getjavastate(self):
        """Return self._javastate"""

        return self._javastate

    def getrstate(self):
        """Return self._rstate"""

        return self._rstate

    def getnumpystate(self):
        """Return self._numpystate"""

        return self._numpystate

    def checkjava(self, options):
        """Check to see if Java is installed properly and included in the PATH"""

        try:
            subprocess.call(["java", "-version"], stderr=open(os.devnull, 'wb'))
            self._javastate = True

        except:
            print "Couldn't find Java. It might not be installed or not included in the PATH"
            print "If it is not installed, please download and install the latest version of Java"
            print "It can be downloaded from http://www.oracle.com/technetwork/java/javase/downloads/index.html"
            print "Trimming cannot be performed if Java is not installed. See the tutorial: sparta.readthedocs.org"
            if options.noninteractive:
                quit()

        return self._javastate


    def checkR(self, options):
        """Check to see if R is installed properly and included in the PATH"""

        try:
            subprocess.call(["R", "--version"], stdout=open(os.devnull, 'wb'))
            self._rstate = True

        except Exception:
            print "Couldn't find R. It might not be installed or not included in the PATH"
            print "If it is not installed, please install R from within the 'DE_analysis' folder within SPARTA"
            print "Differential gene expression cannot be performed if R is not installed. See the tutorial: sparta.readthedocs.org."
            if options.noninteractive:
                quit()
        return self._rstate

    def checknumpy(self, options):
        """Check to see if NumPy module exists"""

        try:
            imp.find_module('numpy')
            self._numpystate = True

        except ImportError:
            self._numpystate = False

        if self._numpystate == False:
            print "You need to install 'NumPy' before proceeding, otherwise HTSeq will not work properly."
            if options.noninteractive:
                quit()
        return self._numpystate

    def getpwd(self):
        """Get present working directory"""

        present_working_directory = subprocess.Popen("pwd", stdout=subprocess.PIPE).communicate()[0].strip("\n")
        return present_working_directory

    def getdesktoppath(self):
        """Get the path to the desktop"""

        desk_path = os.path.join(subprocess.Popen("echo $HOME", shell=True, stdout=subprocess.PIPE).stdout.readline().strip("\n"), "Desktop")
        return desk_path

    def getSPARTAdir(self, options):
        """Attempt to figure out where SPARTA is located. Default should be Desktop"""

        desk_path = os.path.join(subprocess.Popen("echo $HOME", shell=True, stdout=subprocess.PIPE).stdout.readline().strip("\n"), "Desktop")
        os.chdir(desk_path)
        #This is explicitly coded to ensure that the rest of the functions are able to find the appropriate binaries

        try:
            #Get list of SPARTA_Linux versions on the Desktop
            spartaver = glob.glob(desk_path + "/SPARTA_Linux*")[:]
            #Get latest version of SPARTA_Linux in case multiple versions exist on the Desktop
            spartaver.sort()
            if os.path.lexists(spartaver[-1]):
                sparta_dir = spartaver[-1]

            elif os.path.lexists(os.path.join(desk_path, "SPARTA_Linux")):
                sparta_dir = os.path.join(desk_path, "SPARTA_Linux")


        except:
            print "Couldn't find the SPARTA_Linux folder on the Desktop"

            if options.noninteractive:
                quit()

            while not os.path.lexists(sparta_dir):
                sparta_dir = str(raw_input("SPARTA_Linux folder is not on the Desktop. Please place the folder on the Desktop or enter the file path for the folder location or enter quit to exit the program:"))
                if sparta_dir.upper() == "Q" or sparta_dir.upper() == "QUIT":
                    quit()
                #Get list of SPARTA_Mac versions on the Desktop
                spartaver = glob.glob("SPARTA_Linux-*")[:]
                #Get latest version of SPARTA_Mac in case multiple versions exist on the Desktop
                spartaver.sort()
                if os.path.lexists(os.path.join(desk_path, spartaver[-1])):
                    sparta_dir = os.path.join(desk_path, spartaver[-1])

                elif os.path.lexists(os.path.join(desk_path, "SPARTA_Linux")):
                    sparta_dir = os.path.join(desk_path, "SPARTA_Linux")

                elif not os.path.lexists(sparta_dir):
                    print("Invalid file path. The path you have selected does not exist or was not written correctly. \nAn example of path on Ubuntu Linux: /home/yourusername/Desktop/SPARTA_Linux")

        return sparta_dir

    def parseConfigFile(self, options):
        print "SPARTA is running in non-interactive mode."

        cd = CheckDependencies()
        spartadirloc = cd.getSPARTAdir(options)

        conditions_list = []
        #check and make sure that the ConfigFile.txt exists in the SPARTA directory
        if os.path.isfile(os.path.join(spartadirloc, "ConfigFile.txt")):
            with open(os.path.join(spartadirloc, "ConfigFile.txt"), "r") as configfile:
                with open(os.path.join(spartadirloc, 'conditions_input.txt'), "w") as conditions_input:
                    for line in configfile:
                        if line.startswith("Data") or line.startswith("Trimmomatic") or line.startswith("Bowtie") or line.startswith("HTSeq"):
                            parameters = line.split("->")[1]
                            paramlst = parameters.split(",")
                            if line.startswith("Data"):
                                dataloc = paramlst[0].strip()
                                inputname = paramlst[-1].strip()
                                data_path = os.path.join(subprocess.Popen("echo $HOME", shell=True, stdout=subprocess.PIPE).stdout.readline().strip("\n"), dataloc, inputname)
                            elif line.startswith("Trimmomatic"):
                                try:
                                    options.threads = paramlst[0].strip().split("=")[1]
                                    options.illuminaclip = paramlst[1].strip()[len("ILLUMINACLIP:"):]
                                    options.leading = paramlst[2].strip()[len("LEADING:"):]
                                    options.trailing = paramlst[3].strip()[len("TRAILING:"):]
                                    options.slidingwindow = paramlst[4].strip()[len("SLIDINGWINDOW:"):]
                                    options.minlentrim = paramlst[5].strip()[len("MINLEN:"):]
                                except Exception:
                                    print "There doesn't appear to be enough parameters associated with Trimmomatic."
                                    print "Make sure that there are 6: threads, ILLUMINACLIP, LEADING, TRAILING, SLIDINGWINDOW, MINLEN"
                                    print "Proceeding with defaults"
                            elif line.startswith("Bowtie"):
                                try:
                                    if paramlst[0].strip().split("=")[1] != '0' and paramlst[1].strip().split("=")[1] != "None":
                                        options.mismatch = paramlst[0].strip().split("=")[1]
                                        options.otherbowtieoptions = paramlst[1].strip().split("=")[1]
                                    elif paramlst[0].strip().split("=")[1] != '0':
                                        options.mismatch = paramlst[0].strip().split("=")[1]
                                    elif paramlst[1].strip().split("=")[1] != "None":
                                        options.otherbowtieoptions = paramlst[1].strip().split("=")[1]
                                    else:
                                        print "There doesn't appear to be any options specified for Bowtie."
                                        print "Proceeding with defaults"
                                except Exception:
                                    print "There seems to be an error with the options input for Bowtie."
                                    print "Proceeding with defaults"
                            elif line.startswith("HTSeq"):
                                try:
                                    options.stranded = paramlst[0].strip().split("=")[1]
                                    options.order = paramlst[1].strip().split("=")[1]
                                    options.minqual = paramlst[2].strip().split("=")[1]
                                    options.type = paramlst[3].strip().split("=")[1]
                                    options.idattr = paramlst[4].strip().split("=")[1]
                                    options.mode = paramlst[5].strip().split("=")[1]
                                except Exception:
                                    print "There appears to be an issue with the parameter input for HTSeq"
                                    print "Proceeding with defaults"

                        elif line.upper().startswith("REFERENCE") or line.upper().startswith("EXPERIMENTAL"):
                            #Generate the conditions_input.txt file
                            conditions_input.write(line)
                            #Strip off any newlines
                            conditions = line.strip('\n')
                            #Split on the colon and grab just the conditions
                            colsep = conditions.split(':')[1]
                            #Clean up the condition input by attempting to remove spaces and tabs if present
                            condition = colsep.split(',')
                            conditions_list.append(condition)


        return conditions_list, data_path