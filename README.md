# commission-analytics
A tool to help my deal friend to do what-if analysis on sales commission easily on local computer

Sample data will not be shared into repository due to security concern.

**Simple process**:
1) check current folder name:
    1.1) it should be in pattern like: FY16Q3
    1.2) Scheme is: FY(Year)Q(No. Q), for example: FY16Q2, FY17Q3 etc.
    
2) check booking numbers from all past Q
    2.1) If current current Q is not Q1, then booking number file should be available.
    2.2) Search FY16Q1-Booking.csv and FY16Q2-Booking.csv in current folder
    2.3) if not, search FY16Q1-Booking.csv and FY16Q2-Booking.csv in FY16Q2 folder
    2.4) if not found FY16Q1-Booking.csv, then search it in FY16Q1 folder.
    2.5) both files must exist, otherwise stop.
    
3) Refine booking files:
    3.1) Go through each booking file
    3.2) all fields should be strip()
    3.3) 'FY1?' and 'Q?' in header should be removed.
    3.4) all non-floating field will be set to 0.0
    3.5) Save refined booking file in current folder with name: Refined-FY16Q1-Booking.csv etc.
    
4) Generate Booking Total:
    4.1) Load each refined booking csv file as DataFrame and 'Employee No' column will be index column.
    4.2) Drop 'Name' column
    4.3) Drop column which has 'total' in name
    4.3) merge all booking together
    4.4) Export merged booking data into file:FY16BookingYTD.csv as log
    
5) Refine SFDC data:
    5.1) Go through each opportunity line
    5.2) all field should be strip()
    5.3) '?' should be removed from header
    5.4) 'ID' will be changed to 'Employee No'
    5.5) Save refined SFDC file in current folder with name: Refined-SFDC.csv
    
6) Pivot SFDC:
    6.1) Load Refined-SFDC.csv as DataFrame
    6.2) "Employee No" and "Opportunity" will be index column both.
    6.3) TBD
    