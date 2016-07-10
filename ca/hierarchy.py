import sys
import pandas as pd

sys.path.append(".")

try:
    from . import salesman
except:
    import salesman


class Hierarchy:
    def __init__(self):
        self.__emp_list = {}  # emp_no: salesman
        self.__top_emp = None
        self.__vp_list = []

    def get_emp_list(self):
        return self.__emp_list

    def collect_reporters(self, new_salesman):
        '''
        collect reporters from existing emp list by checking who's boss is current user.
        :param new_salesman:
        :return:
        '''
        future_reporters = []
        for emp_no, emp in self.__emp_list.iteritems():
            existing_boss = emp.get_current_boss()
            if existing_boss:
                if existing_boss == new_salesman.get_emp_no():
                    future_reporters.append(emp_no)
                    # print(future_reporters)

        return future_reporters

    def get_salesman_allbosses(self, existing_salesman):
        '''
        return a list of all level of boss of this sales man.
        :param existing_salesman:
        :return:
        '''
        boss_list = []
        current_bosses = existing_salesman.get_boss();
        if len(current_bosses) > 0:
            boss_list.extend(current_bosses)
            uplevel_boss = self.__emp_list.get(current_bosses[0], None)
            if uplevel_boss:
                uplevel_boss_list = self.get_salesman_allbosses(uplevel_boss)
                boss_list.extend(uplevel_boss_list)
        return boss_list

    def get_sales_allreporters(self, existing_salesman):
        '''
        return all children reporters from current salesman
        :param existing_salesman:
        :return:
        '''
        reporters_list = []
        current_reporters = existing_salesman.get_reporters()
        reporters_list.extend(current_reporters)
        for reporter in current_reporters:
            next_salesman = self.__emp_list.get(reporter, None)
            if next_salesman:
                reporters_list.extend(self.get_sales_allreporters(next_salesman))
        return reporters_list

    def add_salesman(self, new_salesman):
        '''
        add a new sales man to emp_list but this function will perform recursve check.
        :param new_salesman:
        :return:
        '''
        if new_salesman.get_emp_no() in self.__emp_list.keys():
            return

        existing_reporters = self.collect_reporters(new_salesman)
        new_salesman.add_reporters(existing_reporters)

        # check current all reporters are not any level of managers.
        all_bosses = self.get_salesman_allbosses(new_salesman)
        if new_salesman.get_emp_no() in all_bosses:
            raise ValueError("Current Hierarchy up level has same emp_no:" + new_salesman.get_emp_no())

        all_reporters = self.get_sales_allreporters(new_salesman)
        if new_salesman.get_emp_no() in all_reporters:
            raise ValueError("Current Hierarchy low level has same emp_no:" + new_salesman.get_emp_no())

        # add current node
        self.__emp_list[new_salesman.get_emp_no()] = new_salesman

        # sync manager node
        current_boss_list = new_salesman.get_boss()
        if len(current_boss_list) == 0:
            # this is top boss
            self.__top_emp = new_salesman.get_emp_no()
        else:
            existing_boss = self.__emp_list.get(current_boss_list[0], None)
            if existing_boss:
                if not (new_salesman.get_emp_no() in existing_boss.get_reporters()):
                    existing_boss.add_reporters([new_salesman.get_emp_no()])

        # sync reporters role.
        current_reporters_list = new_salesman.get_reporters()
        for emp_no in current_reporters_list:
            reporter = self.__emp_list.get(emp_no, None)
            if reporter:
                reporter.set_boss(emp_no)


def build_hierarchy_from_csv(csvfile):
    df = pd.read_csv(csvfile, index_col='EMPLOYEE NO', dtype={'EMPLOYEE NO': object, 'MANAGER': object})
    print(df)

    new_h = Hierarchy()
    for index, row in df.iterrows():
        # print index, row['NAME']
        new_sales = salesman.Salesman(str(index), row['NAME'])  # index has to be converted to string.
        if pd.notnull(row['MANAGER']):
            new_sales.set_boss(row['MANAGER'])

        new_h.add_salesman(new_sales)

    return new_h


def build_hierarchy_from_sample():
    '''
        EMPLOYEE NO	NAME	MANAGER
    1001	Jim H
    1002	Richard Shou	1001
    1003	Matt Cohen	1001
    1004	Carlos D	1003
    1005	Sanjay V	1003
    1006	Michal P	1003
    1007	Chris M	1006
    1008	Elric F	1006
    1009	Zhang J	1002
        :return:
        '''
    new_h = Hierarchy()

    jimh = salesman.Salesman('1001', 'Jim H')

    richardshou = salesman.Salesman('1002', 'Richard Shou')
    richardshou.set_boss('1001')

    mattc = salesman.Salesman('1003', 'Matt Cohen')
    mattc.set_boss('1001')

    carlosd = salesman.Salesman('1004', 'Carlos D')
    carlosd.set_boss('1003')

    sanjayv = salesman.Salesman('1005', 'Sanjay V')
    sanjayv.set_boss('1003')

    michaelp = salesman.Salesman('1006', 'Michael P')
    michaelp.set_boss('1003')

    chrism = salesman.Salesman('1007', 'Chris M')
    chrism.set_boss('1006')

    elricf = salesman.Salesman('1008', 'Elric F')
    elricf.set_boss('1006')

    zhangj = salesman.Salesman('1009', 'Zhang J')
    zhangj.set_boss('1002')

    new_h.add_salesman(jimh)
    new_h.add_salesman(richardshou)
    new_h.add_salesman(mattc)
    new_h.add_salesman(carlosd)
    new_h.add_salesman(sanjayv)
    new_h.add_salesman(michaelp)
    new_h.add_salesman(chrism)
    new_h.add_salesman(elricf)
    new_h.add_salesman(zhangj)

    return new_h


def main():
    # new_h = build_hierarchy_from_sample()
    new_h = build_hierarchy_from_csv('../Sample/FY16Q3/hierarchy.csv')

    for emp_no, sales in new_h.get_emp_list().iteritems():
        print emp_no, "\t", sales
        # print "EMP No:\t", sales.get_emp_no()
        # print "EMP Name:\t", sales.get_name()
        # print "Reporters:\t", sales.get_reporters()
        # print "Current Boss:\t", sales.get_boss()


if __name__ == "__main__":
    main()
