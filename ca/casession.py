import sys
import os
import re
import pandas as pd
import csv

sys.path.append(".")

try:
    from . import salesman
    from . import hierarchy
except:
    import salesman
    import hierarchy


class CASession:
    page_left_margin = 0.2
    block_width = 4.0
    block_w_gap = 3.0
    page_bottom_margin = 0.2
    block_height = 1.0
    block_h_gap = 0.4

    def __init__(self, folder):
        self.__project_folder = None  # indicate project folder in absolute path, /Desheng/FY16Q3
        self.__booking_folder = None  #
        self.__hierarchy_folder = None
        self.__SFDC_folder = None
        self.__GEO_folder = None
        self.__filter_folder = None
        self.__processing_folder = None
        self.__year = None
        self.__quarter = None

        self.__booking_filelist = None
        self.__sfdc_filelist = None
        self.__sfdc_current = None
        self.__GEO_file = None
        self.__configuration_file = None
        self.__commission_plan = None
        self.__hierarchy = None

        self.__cleaned_booking_fileist = None
        self.__cleaned_sfdc_file = None
        self.__cleaned_sfdc_filelist = None
        self.__pivot_sfdc_file = None
        self.__pivot_sfdc_filelist = None
        self.__filtered_booking_filelist = None
        self.__filtered_sfdc_file = None
        self.__filtered_sfdc_filelist = None
        self.__filtered_pivot_SFDC_file = None
        self.__filtered_pivot_SFDC_filelist = None
        self.__summarized_filtered_pivot_SFDC_file = None
        self.__summarized_filtered_pivot_SFDC_filelist = None

        self.__cleaned_geo_file = None
        self.__sales_plannedmgr_mapping_file = None
        self.__all_managers = None  # all up level managers of current lowest level sales rep.

        self.__init_from_folder(folder)
        self.__initialize_default_files()
        self.__init_subfolders()

    def get_img_filename(self):
        return os.path.join(
            self.__processing_folder, '00-Ora-Chart.svg'
        )
    def get_all_managers_list(self):
        if not self.__all_managers:
            raise ValueError("self.__all_managers hasn't been initialized yet!")
        return self.__all_managers

    def build_all_managers_list(self, emp_list):
        '''
        based on recevied emp list to find out all of their managers
        and then store them in variable self.__all_managers
        :param emp_list:
        :return:
        '''
        if not emp_list:
            raise ValueError("emp_list can't be None in build_all_managers_list!")

        self.__all_managers = self.__hierarchy.get_multiple_sales_allbosses(emp_list)

        return self.__all_managers

    def get_manager_rollup_filename(self, algorithm_key):
        return os.path.join(
            self.__processing_folder, "40-Manager-" + algorithm_key + "-Rollup.csv"
        )

    def get_combined_sfdc_allocation_filename(self, algorithm_key):
        return os.path.join(
            self.__processing_folder, "35-SFDC-GEO-" + algorithm_key + "-Allocation.csv"
        )

    def get_split_key_filename(self, key, algorithm_key):
        return os.path.join(
            self.__processing_folder, "30-" + key + "-" + algorithm_key + "-Allocation.csv"
        )

    def get_allocation_step1_filename(self, algorithm_key):
        self.__allocation_step1_filename = os.path.join(
            self.__processing_folder, "25-" + algorithm_key + "Allocation.csv"
        )
        return self.__allocation_step1_filename

    def get_booking_eligible_list_filename(self):
        self.__booking_eligible_list_file = os.path.join(
            self.__processing_folder, "20-Booking-Eligible-List.csv"
        )
        return self.__booking_eligible_list_file

    def get_20_booking_eligible_list_file(self):
        if not self.__booking_eligible_list_file:
            raise ValueError("self.__booking_eligible_list_file hasn't been initialized yet!")
        return self.__booking_eligible_list_file

    def get_15_merged_GEO_SFDC_sum_file(self):
        if not self.__merged_GEO_SFDC_sum_file:
            raise ValueError("self.__merged_GEO_SFDC_sum_file hasn't been initialized yet!")
        return self.__merged_GEO_SFDC_sum_file

    def get_merged_GEO_SFDC_sum_filename(self):
        self.__merged_GEO_SFDC_sum_file = os.path.join(
            self.__processing_folder, "15-Merged-GEO-SFDC-sum.csv"
        )
        return self.__merged_GEO_SFDC_sum_file

    def get_pivot_manager_SFDC_sum_filename(self):
        self.__pivot_manager_SFDC_sum_file = os.path.join(
            self.__processing_folder, "10-Pivot-MGR-SFDC-sum.csv"
        )
        return self.__pivot_manager_SFDC_sum_file

    def get_merged_SFDC_sum_filename(self):
        self.__merged_SFDC_sum_file = os.path.join(self.__processing_folder, "05-Merged-SFDC-sum-Manager.csv")
        return self.__merged_SFDC_sum_file

    def get_05_merged_SFDC_sum_file(self):
        if not self.__merged_SFDC_sum_file:
            raise ValueError("05-Merged_SFDC_sum_file hasn't been initialized yet!")
        return self.__merged_SFDC_sum_file

    def get_summarized_filtered_pivot_sfdc_file(self):
        if not self.__summarized_filtered_pivot_SFDC_file:
            raise ValueError("Default Summarized filtered pivot SFDC file hasn't been initialized yet!")
        return self.__summarized_filtered_pivot_SFDC_file

    def add_summarized_filtered_pivot_SFDC(self, summarized_filtered_pivot):
        if not self.__summarized_filtered_pivot_SFDC_filelist:
            self.__summarized_filtered_pivot_SFDC_filelist = []
            self.__summarized_filtered_pivot_SFDC_file = summarized_filtered_pivot
        self.__summarized_filtered_pivot_SFDC_filelist.append(summarized_filtered_pivot)

    def get_filtered_pivot_SFDC_filelist(self):
        if not self.__filtered_pivot_SFDC_filelist:
            raise ValueError("Filtered Pivot SFDC filelist hasn't been initialized yet!")
        return self.__filtered_pivot_SFDC_filelist

    def get_summarized_filtered_pivot_sfdc_filename(self, filtered_pivot):
        basename = os.path.basename(filtered_pivot)
        return os.path.join(self.__processing_folder, "01-Summarized-" + basename)

    def get_default_filterd_pivot_SFDC_file(self):
        if not self.__filtered_pivot_SFDC_file:
            raise ValueError("Filtered Pivot SFDC file hasn't been initialized yet!")
        return self.__filtered_pivot_SFDC_file

    def add_filtered_pivot_SFDC_file(self, filtered_pivot_sfdc):
        if not self.__filtered_pivot_SFDC_filelist:
            self.__filtered_pivot_SFDC_filelist = []
            self.__filtered_pivot_SFDC_file = filtered_pivot_sfdc
        self.__filtered_pivot_SFDC_filelist.append(filtered_pivot_sfdc)

    def get_filtered_pivot_SFDC_filename(self, pivot_sfdc_file):
        basename = os.path.basename(pivot_sfdc_file)
        basename = "Filtered-" + basename
        return os.path.join(self.__filter_folder, basename)

    def get_filtered_SFDC_filename(self, cleaned_sfdc):
        basename = os.path.basename(cleaned_sfdc)
        if "Cleaned" in basename:
            basename = basename.replace("Cleaned", "Filtered")
        else:
            basename = "Filtered-" + basename
        return os.path.join(self.__filter_folder, basename)

    def add_filtered_SFDC_file(self, filtered_file):
        if not self.__filtered_sfdc_filelist:
            self.__filtered_sfdc_filelist = []
            self.__filtered_sfdc_file = filtered_file  # default SFDC file.
        self.__filtered_sfdc_filelist.append(filtered_file)

    def get_filtered_SFDC_filelist(self):
        if not self.__filtered_sfdc_filelist:
            raise ValueError("filtered SFDC File List hasn't been initialized yet!")
        return self.__filtered_sfdc_filelist

    def get_filtered_SFDC_file(self):
        if not self.__filtered_sfdc_file:
            raise ValueError("filtered SFDC File hasn't been initialized yet!")
        return self.__filtered_sfdc_file

    def get_filtered_booking_filelist(self):
        if not self.__filtered_booking_filelist:
            raise ValueError("filtered Booking Filelist hasn't been initialized yet!")
        return self.__filtered_booking_filelist

    def add_filtered_booking_file(self, filtered_file):
        if not self.__filtered_booking_filelist:
            self.__filtered_booking_filelist = []
        self.__filtered_booking_filelist.append(filtered_file)

    def get_filtered_booking_filename(self, booking_file):
        basename = os.path.basename(booking_file)
        if "Cleaned" in basename:
            basename = basename.replace("Cleaned", "Filtered")
        else:
            basename = "Filtered-" + basename

        return os.path.join(self.__filter_folder, basename)

    def get_GEO_file(self):
        if not self.__GEO_file:
            raise ValueError("GEO forecast file hasn't been initialized correctly!")
        return self.__GEO_file

    def get_cleaned_GEO_filename(self, geo_file=None):
        if not geo_file:
            if not self.__cleaned_geo_file:
                raise ValueError("Cleaned GEO file hasn't been initialized yet!")
            return self.__cleaned_geo_file

        basename = os.path.basename(geo_file)
        self.__cleaned_geo_file = os.path.join(self.__GEO_folder, "Cleaned-" + basename)
        return self.__cleaned_geo_file

    def get_sales_manager_mapping_filename(self, geo_file=None):
        if not geo_file:
            if not self.__cleaned_geo_file:
                raise ValueError("Sales Mapping file hasn't been initialized yet!")
            return self.__sales_plannedmgr_mapping_file

        basename = os.path.basename(geo_file)
        if "Cleaned" in basename:
            basename = basename.replace("Cleaned", "Mapped")
        else:
            basename = "Mapped-" + basename
        self.__sales_plannedmgr_mapping_file = os.path.join(self.__GEO_folder, basename)
        return self.__sales_plannedmgr_mapping_file

    def get_sales_manager_mapping_file(self):
        if not self.__sales_plannedmgr_mapping_file:
            raise ValueError("Sales Mapping file hasn't been initialized yet!")
        return self.__sales_plannedmgr_mapping_file

    def get_pivot_SFDC_filelist(self):
        return self.__pivot_sfdc_filelist

    def get_pivot_SFDC_filename(self, cleaned_sfdc):
        new_filename = ""
        if "Cleaned" in cleaned_sfdc:
            new_filename = (os.path.basename(cleaned_sfdc)).replace("Cleaned", "Pivot")
        else:
            new_filename = "Pivot-" + os.path.basename(cleaned_sfdc)
        return os.path.join(self.__SFDC_folder, new_filename)

    def add_pivot_SFDC_file(self, pivot_file):
        if not self.__pivot_sfdc_filelist:
            self.__pivot_sfdc_filelist = []
            self.__pivot_sfdc_file = pivot_file  # setup first as default.
        self.__pivot_sfdc_filelist.append(pivot_file)

    def get_default_pivot_SFDC_file(self):
        if not self.__pivot_sfdc_file:
            raise ValueError("Default pivot SFDC file hasn't been initalized yet!")
        return self.__pivot_sfdc_file

    def get_SFDC_filelist(self):
        if not self.__sfdc_filelist:
            raise ValueError("SFDC Filelist hasn't been initialized yet!")

        return self.__sfdc_filelist

    def get_SFDC_file(self):
        if not self.__sfdc_current:
            raise ValueError("Current SFDC file hasn't been initialized yet!")
        return self.__sfdc_current

    def get_cleaned_SDFC_filename(self, sfdc_file):
        return os.path.join(self.__SFDC_folder, "Cleaned-" + os.path.basename(sfdc_file))

    def add_cleaned_SFDC_file(self, sfdc_file):
        if not self.__cleaned_sfdc_filelist:
            self.__cleaned_sfdc_filelist = []
            self.__cleaned_sfdc_file = sfdc_file  # setup first as default.
        self.__cleaned_sfdc_filelist.append(sfdc_file)

    def get_cleaned_SFDC_filelist(self):
        if not self.__cleaned_sfdc_filelist:
            raise ValueError("Cleaned SFDC File List hasn't been initalized yet!")
        return self.__cleaned_sfdc_filelist

    def get_year(self):
        return self.__year

    def get_quarter(self):
        return self.__quarter

    def add_cleaned_booking_file(self, filename):
        if not self.__cleaned_booking_fileist:
            self.__cleaned_booking_fileist = []
        if not (filename in self.__cleaned_booking_fileist):
            self.__cleaned_booking_fileist.append(filename)

    def get_cleaned_booking_filelist(self):  # will add a check whether it is None
        if not self.__cleaned_booking_fileist:
            self.clean_bookings()
        return self.__cleaned_booking_fileist

    def __init_subfolders(self):
        self.__booking_folder = self.__setup_subfolder("booking")
        self.__SFDC_folder = self.__setup_subfolder("SFDC")
        self.__GEO_folder = self.__setup_subfolder("GEO")
        self.__filter_folder = self.__setup_subfolder("filter")
        self.__processing_folder = self.__setup_subfolder("processing")

    def get_configuration_file(self):
        if not self.__configuration_file:
            raise ValueError("Configuration File hasn't been initialized yet!")
        return self.__configuration_file

    def get_booking_filelist(self):
        return self.__booking_filelist

    def get_refined_booking_filename(self, booking_filename):
        return os.path.join(self.get_booking_folder(), "Refined-" + os.path.basename(booking_filename))

    def get_cleaned_booking_filename(self, booking_filename):
        old_basename = os.path.basename(booking_filename)
        new_basename = ""
        if "Refined" in old_basename:
            new_basename = old_basename.replace("Refined", "Cleaned")
        else:
            new_basename = "Cleaned-" + old_basename

        return os.path.join(self.get_booking_folder(), new_basename)

    def get_booking_folder(self):
        return self.__booking_folder

    def get_SFDC_folder(self):
        return self.__SFDC_folder

    def get_GEO_folder(self):
        return self.__GEO_folder

    def get_filter_folder(self):
        return self.__filter_folder

    def get_processing_folder(self):
        return self.__processing_folder

    def __setup_subfolder(self, foldername):
        subfolder = os.path.join(self.__project_folder, foldername)
        if not os.path.exists(subfolder):
            os.makedirs(subfolder)

        return os.path.abspath(subfolder)

    def __init_from_folder(self, current_folder):
        if not current_folder or not (os.path.isdir(current_folder)):
            raise ValueError("session should be initiated from a valid folder!")

        abspathname = os.path.abspath(current_folder)  # return /Desheng/sample/FY16Q1
        project_folder = abspathname[abspathname.rfind(os.path.sep) + 1:]  # return FY16Q1

        if not project_folder:
            raise ValueError("You are not in a right project folder!")

        project_folder = re.sub('[\s+]', '', project_folder).upper()  # remove space and upper it.

        if len(project_folder) != 6 or project_folder[0:2] != 'FY' or project_folder[4:5] != 'Q':
            raise ValueError("Wrong project folder name!")

        self.__project_folder = abspathname

        current_year_str = project_folder[2:4]
        current_quarter_str = project_folder[5:6]
        try:
            current_year = int(current_year_str)
            current_quarter = int(current_quarter_str)

            if not (15 < current_year < 100 and 0 < current_quarter < 5):
                raise ValueError("Year or quarter number is out of scope in folder structure!")

            self.__year = current_year
            self.__quarter = current_quarter
        except ValueError:
            raise ValueError("Wrong year or quarter in folder name!")

    def __initialize_default_files(self):
        # get all booking files
        self.__booking_filelist = []
        if self.__quarter != 1:
            for i in range(self.__quarter - 1):
                booking_file = os.path.join(self.__project_folder, "FY%2dQ%1d-Booking.csv" %
                                            (self.__year, (i + 1)))
                # print(booking_file)
                if os.path.isfile(booking_file) and os.path.exists(booking_file):
                    self.__booking_filelist.append(booking_file)
                else:
                    raise ValueError("Can't find file:%s in project folder!" % booking_file)

        # get current SFDC file and all future SFDC files
        self.__sfdc_filelist = []

        sfdc_file = os.path.join(self.__project_folder, "FY%2dQ%1d-SFDC.csv" %
                                 (self.__year, self.__quarter))
        if os.path.isfile(sfdc_file) and os.path.exists(sfdc_file):
            self.__sfdc_current = sfdc_file
            self.__sfdc_filelist.append(sfdc_file)  # current SFDC must have!
        else:
            raise ValueError("Can't find file with name:%s for current quarter!" % (sfdc_file))

        # rest of Q, it's optional to have
        if self.__quarter < 4:
            for i in range(self.__quarter + 1, 5):
                sfdc_file = os.path.join(self.__project_folder, "FY%2dQ%1d-SFDC.csv" %
                                         (self.__year, (i)))
                # print(booking_file)
                if os.path.isfile(sfdc_file) and os.path.exists(sfdc_file):
                    self.__sfdc_filelist.append(sfdc_file)

        # get Hierarchy file and initialize it.
        hierarchy_file = os.path.join(self.__project_folder, "FY%2dQ%1d-Hierarchy.csv" %
                                      (self.__year, self.__quarter))
        if os.path.isfile(hierarchy_file) and os.path.exists(hierarchy_file):
            self.__initialize_hierarchy(hierarchy_file)
        else:
            raise ValueError("Can't find hierarchy file %s in project folder!" % (hierarchy_file))

        # get Geo-forecast file
        geo_file = os.path.join(self.__project_folder, "FY%2dQ%1d-GEOForecast.csv" %
                                (self.__year, self.__quarter))

        if os.path.isfile(geo_file) and os.path.exists(geo_file):
            self.__GEO_file = geo_file
        else:
            raise ValueError("Can't find GEO forecast file %s in project folder!" % (geo_file))

        # get configure ini file.
        config_ini_file = os.path.join(self.__project_folder, "FY%2dQ%1d-Config.ini" %
                                       (self.__year, self.__quarter))

        if os.path.isfile(config_ini_file) and os.path.exists(config_ini_file):
            self.__configuration_file = config_ini_file
        else:
            raise ValueError("Can't find configuration file %s in project folder!" % (config_ini_file))

        # get commission plan file
        commission_plan_file = os.path.join(self.__project_folder, "FY%2dQ%1d-CommissionPlan.csv" %
                                            (self.__year, self.__quarter))

        if os.path.isfile(commission_plan_file) and os.path.exists(commission_plan_file):
            self.__commission_plan = commission_plan_file
        else:
            raise ValueError("Can't find commission plan file %s in project folder!" % (commission_plan_file))

    def __initialize_hierarchy(self, csvfile):
        df = pd.read_csv(csvfile, index_col='EMPLOYEE NO',
                         dtype={'EMPLOYEE NO': object, 'MANAGER': object, 'Status': object})
        # print(df)

        self.__hierarchy = hierarchy.Hierarchy()
        for index, row in df.iterrows():
            # print index, row['NAME'], row['MANAGER']
            new_sales = salesman.Salesman(str(index), row['NAME'],
                                          str(row['Status']))  # index has to be converted to string.
            if pd.notnull(row['MANAGER']):
                new_sales.set_boss(row['MANAGER'])
                # print(new_sales)
            self.__hierarchy.add_salesman(new_sales)

    def get_hierarchy(self):
        if not self.__hierarchy:
            raise ValueError("Hierarchy has not been initialized yet!")
        else:
            return self.__hierarchy

    def clean_bookings(self):
        current_quarter = self.__quarter
        current_year = self.__year
        booking_files = self.__booking_filelist

        for booking_file in booking_files:
            newfilename = self.get_refined_booking_filename(booking_file)
            cleanedfilename = self.get_cleaned_booking_filename(booking_file)

            self.add_cleaned_booking_file(cleanedfilename)

            with open(booking_file, "r") as oldfile, open(newfilename, "w") as newfile:
                oldcsv = csv.reader(oldfile)
                newcsv = csv.writer(newfile)

                first_line = True
                name_index = -1
                tmp_fy_str = 'FY%2d' % current_year
                tmp_q_str = 'Q%d' % current_quarter
                for rix, line in enumerate(oldcsv):
                    if first_line:
                        header_list = []
                        for ix, cell in enumerate(line):
                            tmp_str = (cell.upper().replace(tmp_fy_str, "").replace(tmp_q_str, ""))
                            tmp_str = tmp_str.replace("?", "").strip()
                            if tmp_str == "NAME":
                                name_index = ix
                            else:
                                header_list.append(tmp_str)

                        newcsv.writerow(header_list)
                        first_line = False
                    else:
                        # if rix==1:
                        #    print(line)
                        data_list = []

                        for ix, cell in enumerate(line):
                            # if rix==1:
                            #    print(cell)
                            tmp_str = ""
                            try:
                                if ix != name_index:
                                    tmp_str = cell.strip().replace(",", "")
                                    float(tmp_str)
                                    data_list.append(tmp_str)
                            except:
                                tmp_str = r'0.0'
                                data_list.append(tmp_str)
                                # if rix==1:
                                #    print(cell + "\t-->"+ tmp_str)

                        newcsv.writerow(data_list)
                df = pd.read_csv(newfilename, index_col="EMPLOYEE NO")
                for col in df.columns:
                    if 'TOTAL' in col:
                        del df[col]

                df.to_csv(cleanedfilename)
