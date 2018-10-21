
TEAM MEMBERS:
DINESH ANAND SIVASUBRAMANIAN SURIANARAYANAN (dsivas3@uic.edu)
GAUTAM (gautam5@uic.edu)



Python(version 3) is used to implement MS Apriori Algorithm. 

All files are given as command line arguments. Order is
Argument 1 - input.txt
Argument 2 - parameter.txt
Argument 3 - output.txt

Running command - python3 MSApriori.py input.txt parameter.txt output.txt

Data file is required in which transactions are stored. Transactions are in the following form
{1, 2}
{2, 3, 4}

Parameter file is required in which parameters are stored. Parameters must contain MIS values of all items. Parameter file may or may not contain SDC, must-have and cannot_be_together.
Default SDC is set as 1.
Parameter file is specified in the following way:

MIS(2) = 0.07
MIS(4) = 0.06
SDC = 0.22
cannot_be_together: {2,4}, {1,2}
must-have: 4 or 2

Results are stored in output file which contains all frequent item-sets and their respective support counts and tail counts.