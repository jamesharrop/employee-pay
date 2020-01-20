import csv
import datetime
import copy
''' 
Calculates cost of employee pay including pension and NI contributions
Takes as input a csv file with a format of:
    Header row
    Name: str, Pensionable: bool, Role1 start date: dd/mm/yy, Role1 hours: float, Role1 rate: float, Role1 type: str, Role2 start date...
Can compare scenarios and dates as employee roles and rates of pay/hours change
'''

class Employee:
    '''Represents one employee
    '''
    def __init__(self, name: str, pensionable: bool):
        self.name = name
        self.pensionable = pensionable
        self.roles = []
    
    def __str__(self):
        out = f"{self.name}"
        if not self.pensionable:
            out += " (Not in pension scheme)"
        return out
    
    def current_roles_str(self, date):
        out = ""
        for role in self.roles:
            if role.is_valid_on(date):
                out += role.__str__()
                out += '\n'
        return out
    
    def calculate_pay(self, date):
        '''
        Calculates total cost of this employee's pay on a certain date
        '''
        self.weekly_pay = 0
        
        # Base pay
        for role in self.roles:
            if role.is_valid_on(date):
                self.weekly_pay += role.weekly_pay
        self.annual_pay_before_deductions = self.weekly_pay * 52

        # Employer's NI
        self.NI_threshold = 162
        self.NI_rate = 13.8/100
        if self.weekly_pay > self.NI_threshold:
           self.weekly_amount_liable_to_employers_NI = (self.weekly_pay - self.NI_threshold)
        else:
            self.weekly_amount_liable_to_employers_NI = 0
        self.NI = self.weekly_amount_liable_to_employers_NI * self.NI_rate * 52

        # Pension
        self.pension_rate = 14.38/100
        if self.pensionable:
            self.pension = self.pension_rate * self.annual_pay_before_deductions
        else:
            self.pension = 0

        # Total
        self.total_annual_cost_to_employer = self.annual_pay_before_deductions + self.NI + self.pension

    def calculate_jobroles(self, date, jobroles):
        for role in self.roles:
            if role.is_valid_on(date):
                jobroles[role.role_type] += role.hours

class Role:
    def __init__(self, start_date, hours, rate, role_type, stop_date):
        self.start_date = start_date
        self.hours = hours
        self.rate = rate
        self.role_type = role_type
        self.stop_date = stop_date
        self.weekly_pay = self.hours * self.rate

    def __str__(self):
        out = f"{self.role_type}: "
        out += f"{self.hours} hours/week @ "
        out += f"£{self.rate} / hour"
        return out
    
    def is_valid_on(self, date):
        return (self.start_date < date) and (self.stop_date is None or self.stop_date > date)

class Scenario:
    def __init__(self, name, staff, date):
        self.name = name
        self.staff = copy.deepcopy(staff) # Deepcopy may not be needed but was introduced in a prior version 
                                          # as staff data structure was altered in some scenarios
        self.date = date
        self.jobroles = JobRoles(self.staff).jobroles
        
    def calculate_scenario(self):
        self.total_pay = 0
        for person in self.staff:
            person.calculate_pay(self.date)
            self.total_pay += person.total_annual_cost_to_employer
            person.calculate_jobroles(self.date, self.jobroles)

    def output_scenario(self):
        print("----------------------------")
        print(f"Scenario: {self.name}")
        print(f"Date: {self.date.strftime('%d %B %Y')}")
        print("----------------------------")
        for person in self.staff:
            print(person)
            print(person.current_roles_str(self.date), end="")
            print(f"£{person.total_annual_cost_to_employer:.0f} / year")
            # TODO: switch to Decimal for accuracy
            print("")
        print(f"Total pay: £{self.total_pay:.0f}")
        print(f"Hours per job role: {self.jobroles}")

    def compare_with(self, base_scenario):
        print("----------------------------")
        print(f"Comparing this scenario {self.name} ({self.date.strftime('%d %B %Y')}) with base scenario {base_scenario.name} ({base_scenario.date.strftime('%d %B %Y')}):")
        print("----------------------------")

        print(f"Total annual cost in base scenario: {base_scenario.total_pay:.0f}")
        print(f"Total annual cost in this scenario: {self.total_pay:.0f}")
        print(f"Difference: {(self.total_pay - base_scenario.total_pay):.0f}")
        print("This difference is made up as follows:\n")
        for index, person in enumerate(self.staff):
            base_person = base_scenario.staff[index]
            person_roles = person.current_roles_str(self.date)
            base_person_roles = base_person.current_roles_str(base_scenario.date)
            if person_roles != base_person_roles:
                print(base_person)
                print(f"In base scenario: \n{base_person_roles}", end='')
                print(f"Total annual cost: {base_person.total_annual_cost_to_employer:.0f}\n")
                print(f"In this scenario: \n{person_roles}", end='')
                print(f"Total annual cost: {person.total_annual_cost_to_employer:.0f}\n")
                print(f"Increase in total annual cost: {person.total_annual_cost_to_employer - base_person.total_annual_cost_to_employer:.0f}\n")
                print("---")
        print(f"Hours per job role in base scenario: {base_scenario.jobroles}")
        print(f"Hours per job role in this scenario: {self.jobroles}")


class JobRoles:
    ''' A dictionary of all the different job role strings
    '''
    def __init__(self, staff):
        self.staff = staff
        self.jobroles={}
        for person in self.staff:
            for role in person.roles:
                self.jobroles.setdefault(role.role_type, 0)

def read_from_csv(filename):
    output = []
    with open(filename) as csv_file:
        csv_reader = csv.reader(csv_file, delimiter=',')
        line_count = 0
        for row in csv_reader:
            if line_count == 0:
                line_count += 1
            else:
                name = row.pop(0)
                pensionable_raw = row.pop(0)
                if pensionable_raw == 'Yes' or pensionable_raw == '': # defaults to Yes
                    pensionable = True
                elif pensionable_raw == 'No':
                    pensionable = False
                else:
                    raise ValueError(f"Pensionable value is not given correctly in data for {name}")
                employee = Employee(name, pensionable)
                while len(row)>4: # Another role found
                    start_date_raw = row.pop(0)
                    if start_date_raw == '':
                        start_date_raw = '01/01/1900'
                    start_date = datetime.datetime.strptime(start_date_raw, '%d/%m/%Y').date()    
                    hours_raw = row.pop(0)
                    if hours_raw != '': # Another role found
                        hours = float(hours_raw)
                        rate = float(row.pop(0))
                        role_type = row.pop(0)
                        stop_date_raw = row.pop(0)
                        if stop_date_raw == '':
                            stop_date = None
                        else:
                            stop_date = datetime.datetime.strptime(stop_date_raw, '%d/%m/%Y').date()
                            if stop_date < start_date:
                                raise ValueError(f"Stop date is before start date for {name}")
                        role = Role(start_date, hours, rate, role_type, stop_date)
                        employee.roles.append(role)
                line_count += 1
                output.append(employee)
    return output

if __name__ == "__main__":    
    staff = read_from_csv('2020_01_14 Pay calculator\initial2.csv')

    date = datetime.date(2020,1,17)
    scenario1 = Scenario('', staff, date)
    scenario1.calculate_scenario()
    scenario1.output_scenario()

    date = datetime.date(2020,4,2)
    scenario2 = Scenario('', staff, date)
    scenario2.calculate_scenario()
    scenario2.output_scenario()

    scenario2.compare_with(scenario1)