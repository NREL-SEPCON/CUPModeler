Only the online installer is accessible through GitHub. Please reach out if you would like to install CUP Modeler on a Mac that is not connected to the internet.

This installer will create a directory for the MATLAB runtime environment and a directory for the CUP Modeler software package. It will require admin privileges. The locations where you install these files are needed to run the program.

When the installation is complete, running the modeler will require you to navigate to the CUP Modeler directory in your terminal and running the 'run_CUPV1.sh' bash file. 

The bash file requires an argument, which is the location of the MATLAB runtime environment. For example, when I want to run the modeler, I navigate to the application environment (set during installation, I'm using the default here):

	cd /Applications/NREL/CUPM/application

Then I enter the following command into my terminal:

	./run_CUPM.sh /Applications/MATLAB/MATLAB_Runtime/R2024b

The two parts of this command are running the bash script and the MATLAB runtime environment location (set during installation, I'm using the default here).

The first time you run this, it may take up to 5 minutes to fully set up the environment and run the program. Subsequent launches will be much quicker.