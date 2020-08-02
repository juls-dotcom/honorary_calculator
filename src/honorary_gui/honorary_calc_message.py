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

# Define fares depending on day time
normal_dict = {'day_first_hour_fare':'40',
           'night_first_hour_fare':'49.50',
           'day_subsequent_hour_fare': '32',
           'night_subsequent_hour_fare': '37.50'
          }

holiday_dict = {'day_first_hour_fare':'49.50',
                'night_first_hour_fare':'57',
                'day_subsequent_hour_fare':'37.50',
                'night_subsequent_hour_fare':'45'

}


def calculate_honorary(start_date, end_date, normal_dict, holiday_dict):
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
     * first hour = 40 euros
     * subsequent hour = 32 euros

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

    # Transform dates to Timestamps
    start_date = pd.Timestamp(start_date)
    end_date = pd.Timestamp(end_date)

    print('Start date: ' + str(start_date))
    print('End date: ' + str(end_date))
    print(' ')
    # Get number of hours worked
    number_hours_worked = int(pd.Timedelta(end_date - start_date, unit='h') / timedelta(hours=1))
    if number_hours_worked < 0:
        raise ValueError("End date happened before start date")
    else:
        main_mess = 'You have worked ' + str(number_hours_worked) + ' hours.'
        print(main_mess)

    # Get actual hours relative to the day
    worked_hours = pd.Series(pd.date_range(start_date, end_date, freq='H').hour)

    # Get whether these hours were day or night shift
    bins = [0, 7, 22]  # Day is defined between 0700 and 2200
    labels = ['Night', 'Day']
    shift = pd.cut(worked_hours, bins=bins, labels=labels, include_lowest=True).replace('Night1', 'Night')
    hours_per_shift = pd.DataFrame(pd.concat([worked_hours, shift], axis=1)).groupby(1).count()
    print(hours_per_shift)

    # Verify whether start date is holiday
    if (df.Date.astype(str).str.contains(start_date.strftime('%Y-%m-%d')).sum()) > 0:
        # Day in calendar, so not holiday
        start_holiday = False
        fare_dict = normal_dict
        start_date_mess = 'Start date is business day.'
        print(start_date_mess)
    else:
        # Day not in calendar, so holiday
        start_holiday = True
        fare_dict = holiday_dict
        start_date_mess = 'Start date is weekend or holiday'
        print(start_date_mess)
    if df.Date.astype(str).str.contains(end_date.strftime('%Y-%m-%d')).sum() > 0:
        # Day in calendar, so not holiday
        end_holiday = False
        fare_dict = normal_dict
        end_date_mess = 'End date is business day'
        print(end_date_mess)
    else:
        # Day not in calendar, so holiday
        end_holiday = True
        fare_dict = holiday_dict
        end_date_mess = 'End date is weekend or holiday'
        print(end_date_mess)

    honorary_night = ((hours_per_shift.T.Night.values - 1) * float(normal_dict.get("night_subsequent_hour_fare"))
                      + float(normal_dict.get("night_first_hour_fare"))
                      )

    honorary_day = ((hours_per_shift.T.Day.values - 1) * int(normal_dict.get("day_subsequent_hour_fare"))
                    + int(normal_dict.get("day_first_hour_fare"))
                    )

    honorary_total = int(honorary_day + honorary_night)

    print(' ')
    honorary_mess = 'You are owed ' + str(honorary_total) + ' euros.'
    print(honorary_mess)

    return ('Start date: ' + str(start_date) + '          '
           + 'End date: ' + str(end_date) + '          '
           +  start_date_mess + '               '
           + end_date_mess+ '                   '
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

frame_start_hour = LabelFrame(root, text='Start Hour(H:M:S)',padx=10,pady=10)
frame_start_hour.grid(row=0,column=0,padx=10,pady=10)

#frame_end_date = LabelFrame(root, text='End Date (Y-M-D)',padx=10,pady=10)
#frame_end_date.grid(row=0,column=1,padx=10,pady=10)

cal_end_date = Calendar(root, selectmode="day",year=2020, month=6, day=1)
cal_end_date.grid(row=1,column=1,padx=10,pady=10)

frame_end_hour = LabelFrame(root, text='End Hour (H:M:S)',padx=10,pady=10)
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
    messagebox.showinfo('Honorary Results', calculate_honorary(start_date=str(cal_start_date.get_date()) + ' '+ str(e_start_hour.get()),
                                                                                                       end_date=str(cal_end_date.get_date()) + ' ' + str(e_end_hour.get()),
                                                                                                       normal_dict=normal_dict,
                                                                                                       holiday_dict=holiday_dict)
                        )

# Define Buttons

button_confirm = Button(root, text="Calculate!", padx=40, pady=20, command=popup)


# Put the buttons on screen

button_confirm.grid(row=2, column=0, columnspan=3)

button_quit = Button(root, text = 'Exit Calculator', command=root.quit)
button_quit.grid(row=3, column=0, columnspan=3)

root.mainloop()
