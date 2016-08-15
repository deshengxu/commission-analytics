import sys


class Salesman:
    # initialize name, ID number, city
    def __init__(self, emp_no, emp_name, term=None, multiplier=""):
        self.__emp_no = emp_no
        self.__emp_name = emp_name
        self.__reporters = []
        self.__boss = []
        self.__is_overlay = False
        self.__is_termed = False
        if not multiplier:
            multiplier = ""
        multiplier = multiplier.strip().replace(" ", "")

        self.__multiplier = multiplier  # 2.7 or 3xACV; 2XACV; _blank_
        if term:
            term_str = term.upper().strip()
            if term_str == "TRUE" or term_str == "TERM":
                self.__is_termed = True

    def set_multiplier(self, multiplier):
        self.__multiplier = multiplier

    def get_multiplier(self):
        return self.__multiplier

    def get_emp_no(self):
        return self.__emp_no

    def is_manager(self):
        return len(self.__reporters) > 0

    def is_termed(self):
        return self.__is_termed

    def get_name(self):
        return self.__emp_name

    def set_overlay_on(self):
        self.__is_overlay = True

    def set_overlay_off(self):
        self.__is_overlay = False

    def set_boss(self, boss_emp_no):
        if boss_emp_no in self.__reporters:
            raise ValueError("You can't add reporter as boss!")

        self.__boss.append(boss_emp_no)

    def has_boss(self):
        return len(self.__boss) > 0

    def get_boss(self):
        return self.__boss

    def get_current_boss(self):
        if len(self.__boss) > 0:
            return self.__boss[0]
        else:
            return None

    def is_overlay(self):
        return self.__is_overlay

    def add_reporters(self, reporter_list):
        for emp_no in reporter_list:
            if not (emp_no in self.__reporters):
                if emp_no in self.__boss:
                    raise ValueError("You can't add boss as reporter!")

                self.__reporters.append(emp_no)

    def get_reporters(self):
        return self.__reporters

    def has_reporters(self):
        return len(self.__reporters) > 0

    def has_reporter(self, emp_no):
        return emp_no in self.__reporters

    # return formatting
    def __str__(self):
        name_string = '*'
        name_string += '*'.join(self.__boss)
        name_string += "->" + self.__emp_no + ":" + self.__emp_name + "->[" + ":".join(self.__reporters) + "]"
        if self.__is_termed:
            name_string += " Termed"
        name_string += " " + self.__multiplier
        return name_string


def main():
    newsales = Salesman('1234', 'First New Sales')
    print(newsales)
    newsales.add_reporters(['1235', '1236', '1237'])
    print(newsales)
    newsales.set_boss('1238')
    print(newsales)
    try:
        newsales.set_boss('1235')
        print(newsales)
    except ValueError as err:
        print(err)

    try:
        newsales.add_reporters(['1238'])
        print(newsales)
    except ValueError as err2:
        print(err2)


if __name__ == "__main__":
    main()
