########################################################################################################################
# Author:
#               Matt Tucker
#
# Date:
#               24 Oct 2023 - 25 Oct 2023
#
# Description:
#               Parse and compare data from CSV and HTML files.
#
# Rev.(I) Date:
#               24 Oct 2023
#
# Revision Notes:
#               Initial version
#
# ToDo:
#               x)  User hardcodes file path for CSV as string(PATH)
#               x)  User hardcodes "CASESTR" strings as array(casestr)
#               x)  Take column titles to be searched as array(cref and href) that user hardcodes
#               x)  Search "host" folder for HTMLS containing "CASESTR" strings from CSV in their titles
#               x)  Compare values, corresponding to the list of columns, between CSV and HTML
#               x)  Note on CSV-HTML pairs that have differing values
#               x)  Save tables as .csv/.xlsx:
#                                   MISMATCH    Column_1    Column_2    Column_3    ...
#                           CSV     (1,0)       'value'     'value'     'value'     ...
#                           HTML    (1,0)       'value'     'value'     'value'     ...
#                     Mismatches    'Count'     (1,0)       (1,0)       (1,0)       ...
#                   Note- '1' if file is mismatched, otherwise '0'
#               x)  Print:
#                       "CASESTR-'string', has mismatches in the following column-\n
#                                   'col'"
#
# Notes:
#               1)  Since column titles between the CSV and HTML may not be exactly the same, it would be nice to use
#                   Hamming Distance: d_{H}('st1_{binary}' xor 'st2_{binary}')
########################################################################################################################

########################################################################################################################
#
# Notes about QuickSilvers CSV-HTML Parser:
#               1) The user has to hardcode:
#                       i) PATH(line 64)     =   path to CSV file
#                      ii) casestr(line 68)  =   the CASESTR values they're interested in
#                     iii) cref(line 75)     =   the columns from the CSV file that they're interested in
#                      iv) href(line 80)     =   the parameter data from the HTML file that they're interested in
#               2) Lines 162 and 163 mark a CSV-HTML data pair as mismatched if one doesn't have a unit but the other
#                  one does.
#               3) Lines 95 - 108 alert the user to potential missing files or typos in user provided fields
#               4) All saved CSV files(lines 185- 189) are saved in the same folder as the corresponding HTML file and
#                  have the same name as the corresponding HTML file but with the file extension '.csv
#
########################################################################################################################

from bs4 import BeautifulSoup
import decimal
from decimal import *
import os
import pandas as pd

gen_labels = ['CSV', 'HTML', 'Mismatch']

# Enter path to and name of .csv file
PATH = 'Sample Input Files\substitutionfile_20230620.csv'
folder = os.path.dirname(PATH)

# Enter list of "CASESTR" you'd like to check
casestr = ['Case_041', 'Case_042', 'Case_043', 'Case_044', 'Case_045', 'Case_046']


########################################################################################################################
# NOTE: For this code to work properly, you must insert href values in the same order as their corresponding cref values
########################################################################################################################
# Enter list of .csv column names you'd like to compare
cref = ['Mach_Ref', 'V_Ref', 'Ps_Ref', 'SAT_Ref', 'Rho_Ref']
# Leave this line- it ensures we have a flag in the eventual CSV dataframe
cref.insert(0, 'CASESTR')

# Enter list of .html column names you'd like to compare
href = ['Mach Ref', 'V Ref', 'Ps Ref', 'SAT Ref', 'Rho Ref']
########################################################################################################################
########################################################################################################################
########################################################################################################################

# Get list of all HTMLs
file_ls = []
casestr_cor = []
for file in os.listdir(folder):
    for ele in casestr:
        if ele in file and 'html' in file:
            file_ls.append(file)
            casestr_cor.append(ele)

# Alerts user to the possibility that a "CASESTR" is typed wrong or missing its corresponding HTML
casestr_missing = []
for ele in casestr:
    if ele not in casestr_cor:
        casestr_missing.append(casestr)
if len(file_ls) == 0:
    print('No html files containing the provided \"CASESTRs\" were found')
    exit()
else:
    if len(casestr_missing) != 0:
        print('Html files could not be found for the following \"CASESTRs\": ')
        for ele in casestr_missing:
            print(ele)
    else:
        print('Html files were found for all provided \"CASESTRs.\"')

# Build dataframe from .csv file
cdf = pd.read_csv(PATH, sep=',')
cdf = cdf[cdf.columns[cdf.columns.isin(cref)]]


# Build dataframe from .html file
def buildHtmldataframe(eleme):
    hdata = []
    html_doc = open(os.path.join(folder, eleme), 'r')
    soup = BeautifulSoup(html_doc, 'html.parser')
    # print(soup.get_text())
    for l in href:
        if l != 'CASESTR':
            hdelim = l + '\nTypeSCALAR'
            hdatum = soup.get_text()
            hdatum = hdatum.split(hdelim)[1]
            hdatum = hdatum.split('\nValue')[1]
            hdatum = hdatum.split('\n')[0]
            hdata.append(hdatum)
    cstr = (eleme.split('_Summary.html'))[0]
    hdata.insert(0, cstr)
    return pd.DataFrame(index=cref, data=hdata)


def main():
    i = 0
    href.insert(0, 'CASESTR')

    # Compare decimal values
    def compareDecimals(cvalue, hvalue):
        cutoff = decimal.Decimal(hvalue)
        cutoff = abs((cutoff.as_tuple().exponent)) - 1
        if cutoff > 0:
            getcontext().prec = cutoff
        if cvalue - hvalue == 0:
            return 0
        else:
            return 1

    # Compare dataframes, and returns "mismatch" dataframe consisting of 1s and 0s. 1 if corresponding data values do not
    # match and 0 if they do.
    # The logic for why we are using 1 to represent mismatches is that this dataframe answers the question, "are these
    # values mismatched?"
    def compareDataFrames(cdf, cref, hdf):
        misdata = [0 for i in range(len(cref))]
        for i in range(1, len(misdata)):
            # Removes units from values for comparison
            cvalue = str(cdf.iat[0, i]).split(' ')
            hvalue = str(hdf.iat[0, i]).split(' ')
            check = compareDecimals(float(cvalue[0]), float(hvalue[0]))
            ############################################################################################################
            # Comment this block out if it doesn't matter when one has units but the other one doesn't
            if len(cvalue) != len(hvalue):
                check = 1
            ############################################################################################################
            if len(cvalue) == 2 and len(hvalue) == 2:
                if cvalue[1] != hvalue[1]:
                    check = 1
            if check == 1:
                misdata[i] = check
                print(
                    'CASESTR-' + str(cdf.iat[0, 0]) + ', has mismatches in the following column-\n' + str(cref[i]))
        return pd.DataFrame(index=cref, data=misdata).T, misdata


    # Iterates over list of HTML file and builds hdf
    for el in file_ls:
        # Builds dataframe for ONE HTML file.
        hdf = buildHtmldataframe(el).T
        # Form sub dataframe from CSV dataframe for the row corresponding to the HTML file
        sub_cdf = cdf.loc[cdf['CASESTR'] == hdf.iat[0, 0]]
        # Compares dataframe values retrieved from the HTML file to the appropriate values retrieved from the CSV file
        mdf, misdata = compareDataFrames(sub_cdf, cref, hdf)

        # Saves .csv file
        resdf = pd.concat([sub_cdf, hdf, mdf])
        resdf.index = gen_labels
        saved_name = el.replace('html', 'csv')
        saved_file = os.path.join(folder, saved_name)
        resdf.to_csv(saved_file)


if __name__ =="__main__":
    main()
