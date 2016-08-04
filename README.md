# commission-analytics
A tool to help my dear friend to perform what-if analysis on sales commission easily on local computer

Sample data will not be shared into repository due to security concern.

**Simple process**:

1) check current folder name: (**Done**!)

    1.1) it should be in pattern like: FY16Q3
    
    1.2) Scheme is: FY(Year)Q(No. Q), for example: FY16Q2, FY17Q3 etc.
    
2) check booking numbers from all past Q

    2.1) If current current Q is not Q1, then booking number file should be available.(**Done**)
    
    2.2) Search FY16Q1-Booking.csv and FY16Q2-Booking.csv in current folder (**Done**)
    
    2.3) if not, search FY16Q1-Booking.csv and FY16Q2-Booking.csv in FY16Q2 folder(**~~Postpone~~**)
    
    2.4) if not found FY16Q1-Booking.csv, then search it in FY16Q1 folder.(**~~Postpone~~**)
    
    2.5) both files must exist, otherwise stop. (**Done**)
    
3) Refine booking files: (**Done**)

    3.1) Go through each booking file
    
    3.2) all fields should be strip()
    
    3.3) 'FY1?' and 'Q?' in header should be removed.
    
    3.4) all non-floating field will be set to 0.0
    
    3.5) Save refined booking file in current folder with name: Refined-FY16Q1-Booking.csv etc.
    
4) Generate Booking Total: (**Done**)

    4.1) Load each refined booking csv file as DataFrame and 'Employee No' column will be index column.
    
    4.2) Drop 'Name' column
    
    4.3) Drop column which has 'total' in name
    
    4.3) merge all booking together
    
    4.4) Export merged booking data into file:FY16BookingYTD.csv as log
    
5) Refine SFDC data: (**Done**)

    5.1) Go through each opportunity line
    
    5.2) all field should be strip()
    
    5.3) '?' should be removed from header
    
    5.4) 'ID' will be changed to 'Employee No'
    
    5.5) Save refined SFDC file in current folder with name: Refined-SFDC.csv
    
6) Pivot SFDC: (**Done**)

    6.1) Load Refined-SFDC.csv as DataFrame
    
    6.2) "Employee No" will be index column both.
    
    6.3) Pivot key will be configurable, which by default is "EMPLOYEE NO"
    
    6.4) Pivot columns will be configurable.
    
    6.5) Pivot Big deal
    
7) Hierarchy Build Up (**Done**)
    
    7.1) Load Emp hierarchy after refine
    
    7.2) Define EMP class
    
    7.3) Define direct report list.
    
    7.4) Define report to list.
    
    7.5) Provide hierarchy chat for validation.

8) Refine Geo-Forecast Data

    8.1) Data Clean (TBD)
    
    8.2) Verification (TBD)
    
9) Calculation Process (Regular, **Done**):
    
    9.1) From Geo-Forecast data, query all lowest level sales list.
    
    9.2) From Q1/Q2 booking list, filter records for those sales man only.
    
    9.3) Merge filtered booking together and assign different columns names.
    
    9.4) Rule 1: if total booking > certain numbers, sales will not be included in next two steps allocation.
    
    9.5) Rule 2: Remove big deal both from SFDC pivot and Geo-Forecast; 
    
        9.5.1) then allocate rest of direct manager's Geo-forecast to direct sales proportionally.
        
        9.5.2) Calculate sales total for next step.
        
        9.5.3) Individual Sales will has a max cap. over allocation will be captured and reallocated later.
    
    9.6) Rule 3: Allocate Geo-Forecast from uplevel managers to all direct sales proportionally.
        
        9.6.1) Individual Sales will has a max cap. over allocation will be captured and reallocated later.
    
    9.7) Rule 4: Allocate rest Geo-Forecast to all sales.
    
    9.8) Roll up to all level managers
    
    
10) Calculate Process (Minimal Commission):

    10.1) "Rest" of a manager will be spreaded out to all his lowest level eligible sales equally.
    
11) Calculate Process (Maximal Commission):
    11.1) "Rest" will be assigned to "richest" sales.

12) Calculate Process (Very Low Commission):

    12.1) "Rest" will be assigned to lowest sales rep first and then next lowest sales rep.
    

    