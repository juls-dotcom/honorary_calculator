import pandas as pd
from pandas.tseries.holiday import *
from pandas.tseries.offsets import CustomBusinessDay

class FrenchBusinessCalendar(AbstractHolidayCalendar):
   rules = [
        Holiday('New Years Day', month=1, day=1),
        EasterMonday,
        Holiday('Labour Day', month=5, day=1),
        Holiday('Victory in Europe Day', month=5, day=8),
        Holiday('Ascension Day', month=1, day=1, offset=[Easter(), Day(39)]),
        Holiday('Bastille Day', month=7, day=14),
        Holiday('Assumption of Mary to Heaven', month=8, day=15),
        Holiday('All Saints Day', month=11, day=1),
        Holiday('Armistice Day', month=11, day=11),
        Holiday('Christmas Day', month=12, day=25)
   ]

French_BD = CustomBusinessDay(calendar=FrenchBusinessCalendar())
s = pd.date_range('2016-12-29', end='2021-01-03', freq=French_BD)
df = pd.DataFrame(s, columns=['Date'])


def calculate_honorary(start_date, end_date, first_hour=True):
    """
    Calculate the honorary for worked hours based on following rules

    params: start_date (str), start date in format '%Y-%m-%d-H:M:S'
    params: end_date (str), end date in format '%Y-%m-%d-H:M:S'
    params: normal_dict (dict), business day fare dictionnary
    params: holiday_dict (dict), holiday day fare dictionnary

    #### Payment Rules

    day is between 0700 and 2200
    night is between 2200 and 0700

    normal day fare:
     * first hour = 42 euros
     * subsequent hour = 30 euros

    normal night fare
     * first hour = 49.50 euros
     * subsequent hour = 37.50 euros

    holiday fare:
     * first hour = 49.50 euros
     * subsequent hour = 37.50 euros

    holiday fare
     * first hour = 57 euros
     * subsequent hour = 45 euros
    """

    if first_hour:
        # Define fares depending on day time
        normal_dict = {'day_first_hour_fare': '42',
                       'night_first_hour_fare': '49.50',
                       'day_subsequent_hour_fare': '30',
                       'night_subsequent_hour_fare': '37.50'
                       }

        holiday_dict = {'day_first_hour_fare': '49.50',
                        'night_first_hour_fare': '57',
                        'day_subsequent_hour_fare': '37.50',
                        'night_subsequent_hour_fare': '45'
                        }
    else:
        normal_dict = {'day_first_hour_fare': '30',
                       'night_first_hour_fare': '37.50',
                       'day_subsequent_hour_fare': '30',
                       'night_subsequent_hour_fare': '37.50'
                       }

        holiday_dict = {'day_first_hour_fare': '37.50',
                        'night_first_hour_fare': '45',
                        'day_subsequent_hour_fare': '37.50',
                        'night_subsequent_hour_fare': '45'
                        }

    # Transform dates to Timestamps
    start_date = pd.Timestamp(start_date)
    end_date = pd.Timestamp(end_date)

    # Give feedback to user
    print('Start date: ' + str(start_date))
    print('End date: ' + str(end_date))
    print(' ')
    # Get number of hours worked
    number_hours_worked = int(pd.Timedelta(end_date - start_date, unit='h') / timedelta(hours=1))
    # Raise a simple error if problem with entered date
    if number_hours_worked < 0:
        raise ValueError("End date happened before start date")
    else:
        main_mess = 'You have worked ' + str(number_hours_worked) + ' hours.'
        print(main_mess)

    # Get actual hours relative to the day
    worked_hours = pd.Series(pd.date_range(start_date, end_date, freq='H').hour)
    worked_dates = pd.Series(pd.date_range(start_date, end_date, freq='H').date)

    # Get whether these hours were day or night shift
    ## Day is defined between 0700 and 2200
    bins = [0, 7, 22, 24]
    # I add a third night label that I rename later on. Suboptimal
    labels = ['Night', 'Day', 'Night1']
    # Compute shifts
    shift = pd.cut(worked_hours[1:], bins=bins, labels=labels, include_lowest=True, right=True).replace('Night1',
                                                                                                        'Night')
    # Concatenate data
    hours_per_shift = (pd
                       .DataFrame(pd.concat([worked_dates, worked_hours, shift], axis=1))
                       .rename(columns={0: 'date', 1: 'hour', 2: 'shifts'}))
    # Shift the shifts column to get correct number of hours per shift per day
    hours_per_shift.shifts = hours_per_shift.shifts.shift(-1)
    # Groupby and count the number of hours
    # Fill NaN with 0 hours worked
    hours_per_shift = hours_per_shift.groupby(['date', 'shifts']).count().fillna(0)
    print(hours_per_shift)
    print(' ')
    # Verify whether start date is holiday
    if (df.Date.astype(str).str.contains(start_date.strftime('%Y-%m-%d')).sum()) > 0:
        # Day in calendar, so not holiday
        start_holiday = False
        fare_dict_start = normal_dict
        start_date_mess = 'Start date is business day.'
        print(start_date_mess)
    else:
        # Day not in calendar, so holiday
        start_holiday = True
        fare_dict_start = holiday_dict
        start_date_mess = 'Start date is weekend or holiday'
        print(start_date_mess)
    if df.Date.astype(str).str.contains(end_date.strftime('%Y-%m-%d')).sum() > 0:
        # Day in calendar, so not holiday
        end_holiday = False
        fare_dict_end = normal_dict
        end_date_mess = 'End date is business day.'
        print(end_date_mess)
    else:
        # Day not in calendar, so holiday
        end_holiday = True
        fare_dict_end = holiday_dict
        end_date_mess = 'End date is weekend or holiday.'
        print(end_date_mess)

    # Calculate fee

    print('')

    if start_date.date() == end_date.date():  # if mission was on one day only
        print('Mission was on one single day')
        # Set end date as no gain
        honorary_end_date = 0
        # Get first day data
        day_one = hours_per_shift.reset_index().loc[hours_per_shift.reset_index()['date'] == start_date]
        if shift.iloc[0] == 'Day':
            honorary_start_date = (float(fare_dict_start.get("day_first_hour_fare"))
                                   + float((day_one.loc[day_one.shifts == 'Day'].hour - 1)
                                           * float(fare_dict_start.get("day_subsequent_hour_fare")))
                                   + float((day_one.loc[day_one.shifts == 'Night'].hour)
                                           * float(fare_dict_start.get("night_subsequent_hour_fare"))))
        else:
            honorary_start_date = (float(fare_dict.get("night_first_hour_fare"))
                                   + float((day_one.loc[day_one.shifts == 'Night'].hour - 1)
                                           * float(fare_dict_start.get("night_subsequent_hour_fare")))
                                   + float((day_one.loc[day_one.shifts == 'Day'].hour)
                                           * float(fare_dict_start.get("day_subsequent_hour_fare"))))

    else:  # if mission was on two consecutive days
        print('Mission was on two consecutive days')
        print('')
        day_one = hours_per_shift.reset_index().loc[hours_per_shift.reset_index()['date'] == start_date]
        day_two = hours_per_shift.reset_index().loc[hours_per_shift.reset_index()['date'] == end_date]
        if shift.iloc[0] == 'Day':
            print('First hour is day shift')
            # Honorary Start Date
            honorary_start_date = (float(fare_dict_start.get("day_first_hour_fare"))
                                   + float((day_one.loc[day_one.shifts == 'Day'].hour - 1)
                                           * float(fare_dict_start.get("day_subsequent_hour_fare")))
                                   + float((day_one.loc[day_one.shifts == 'Night'].hour)
                                           * float(fare_dict_start.get("night_subsequent_hour_fare"))))
            # Honorary End Date
            honorary_end_date = (
                    + float((day_two.loc[day_two.shifts == 'Night'].hour)
                            * float(fare_dict_end.get("night_subsequent_hour_fare")))
                    + float((day_two.loc[day_two.shifts == 'Day'].hour)
                            * float(fare_dict_end.get("day_subsequent_hour_fare"))))
        else:
            print('First hour isnight shift')
            # Honorary Start Date
            honorary_start_date = (float(fare_dict_start.get("night_first_hour_fare"))
                                   + float((day_one.loc[day_one.shifts == 'Night'].hour - 1)
                                           * float(fare_dict_start.get("night_subsequent_hour_fare")))
                                   + float((day_one.loc[day_one.shifts == 'Day'].hour)
                                           * float(fare_dict_start.get("day_subsequent_hour_fare"))))
            # Honorary End Date
            honorary_end_date = (
                    + float((day_two.loc[day_two.shifts == 'Night'].hour)
                            * float(fare_dict_end.get("night_subsequent_hour_fare")))
                    + float((day_two.loc[day_two.shifts == 'Day'].hour)
                            * float(fare_dict_end.get("day_subsequent_hour_fare"))))

    honorary_total = int(honorary_start_date + honorary_end_date)

    print(' ')
    honorary_mess = 'You are owed ' + str(honorary_total) + ' euros.'
    print(honorary_mess)

    return ('Start date: ' + str(start_date) + '          '
            + 'End date: ' + str(end_date) + '          '
            + start_date_mess + '               '
            + end_date_mess + '                   '
            + main_mess + '                    '
            + honorary_mess)

# Output actual GUI

from tkinter import *
from tkcalendar import *
from tkinter import messagebox

root = Tk()
root.title("Honorary Calculator")

#frame_start_date = LabelFrame(root, text='Start Date (Y-M-D)',padx=10,pady=10)
#frame_start_date.grid(row=0,column=0,padx=10,pady=10)

cal_start_date = Calendar(root, selectmode="day",year=2020, month=6, day=1)
cal_start_date.grid(row=1,column=0,padx=10,pady=10)

frame_start_hour = LabelFrame(root, text='Start Hour(Hour from 0 to 24)',padx=10,pady=10)
frame_start_hour.grid(row=0,column=0,padx=10,pady=10)

#frame_end_date = LabelFrame(root, text='End Date (Y-M-D)',padx=10,pady=10)
#frame_end_date.grid(row=0,column=1,padx=10,pady=10)

cal_end_date = Calendar(root, selectmode="day",year=2020, month=6, day=1)
cal_end_date.grid(row=1,column=1,padx=10,pady=10)

frame_end_hour = LabelFrame(root, text='End Hour (Hour from 0 to 24)',padx=10,pady=10)
frame_end_hour.grid(row=0,column=1,padx=10,pady=10)

#e_start_date = Entry(cal_start_date,width=35,bg="black", fg='white', borderwidth=5)
#_end_date = Entry(frame_end_date,width=35,bg="black", fg='white', borderwidth=5)
e_start_hour = Entry(frame_start_hour,width=35,bg="black", fg='white', borderwidth=5)
e_end_hour = Entry(frame_end_hour,width=35,bg="black", fg='white', borderwidth=5)

#e_start_date.grid(row=0,column=0)
#e_end_date.grid(row=0,column=1)
e_start_hour.grid(row=1,column=0)
e_end_hour.grid(row=1,column=1)

def popup():
    messagebox.showinfo('Honorary Results', calculate_honorary(start_date=str(cal_start_date.get_date()) + ' '+ str(e_start_hour.get()+':00:00'),
                                                               end_date=str(cal_end_date.get_date())    + ' ' + str(e_end_hour.get()  +':00:00'),
                                                               first_hour=var.get() )
                        )

## Define Buttons
# Calculate button
button_confirm = Button(root, text="Calculate!", padx=40, pady=20, command=popup)
# Quite button
button_quit = Button(root, text = 'Exit Calculator', command=root.quit)

## Define Box to inform whether first hour should count more
# Define the boolean variable resulting from box checking
var = IntVar()
# Define Box
first_hour_box = Checkbutton(root, text='First hour counts extra?', variable=var)

## Put the content on screen
# Calculate button
button_confirm.grid(row=3, column=0, columnspan=3)
# First hour check box
first_hour_box.grid(row=2, column=0, columnspan=3)
# Quite button
button_quit.grid(row=4, column=0, columnspan=3)

root.mainloop()
