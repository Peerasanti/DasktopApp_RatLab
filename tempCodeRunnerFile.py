date_entry = DateEntry(window, locale='th_TH', date_pattern='dd-mm-yyyy')
date_entry.place(x=690, y=200, width=250, height=25)
date_entry.set_date(datetime.now())