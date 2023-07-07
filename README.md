# ecc100-python-dll

Python (3.6) communication library for the Attocube ECC100 three axis motion controller connected to a PC via a USB connection.
The class makes use of a dynamical link library (dll) provided by the Attocube software (links below). Documentation on the library functions is provided by the company in the .zip files.

The functions are adapted from an example provided by Attocube for using the dll library with C#.

The functions defined herein allow the user to:

- connect to and disconnect from an ECC 100 motion controller
- set voltage and frequency parameters for single step movement along different axes
- make single steps forward or backward along a particular axis

These are not an exhaustive list of the functions available to communicate with the motion controller; using the dll library documentation, python versions of additional dll functions could be easily added as necessary following the format of the functions already defined so far. If you write additional functions feel free to send a pull request.

Manual: https://www.attocube.com/FTP/download/_Manuals/ECC100/Manual_ECC100.pdf
Driver: https://www.attocube.com/FTP/download/_Software/ECC100/Software_ECC100.zip
