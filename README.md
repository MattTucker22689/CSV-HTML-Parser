# CSV-HTML-Parser

The following data parser- 
      1) uses BeautifulSoup and Pandas to parse data from a CSV file and a set of HTML files, 
      2) forms data frames using Pandas to compare the data, compares the data, 
      3) reports if there were any mismatches, 
      4) and then saves a CSV copy of a data frame formed by concatenating the three data frames(subset of the data from the original CSV file, the HTML data, and the mismatched data)  formed along the way
