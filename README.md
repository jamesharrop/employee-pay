# employee-pay

Calculates cost of employee pay including pension and NI contributions.

Example rates used for pension and NI are for illustration only.

Two different versions - using classes, or using Pandas

Classes version:
Takes as input a csv file with a format of:
    Header row
    Name: str, Pensionable: bool, Role1 start date: dd/mm/yy, Role1 hours: float, Role1 rate: float, Role1 type: str, Role2 start date...

Can compare scenarios and dates as employee roles and rates of pay/hours change
