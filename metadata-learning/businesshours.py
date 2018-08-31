#!/usr/bin/env python3

"""Calculate business hours between two timestamps
"""

from datetime import datetime, date, timedelta, time


def subtract_time(time_1, time_2):
    """Find the difference between two times (datetime.time objects)"""
    return (datetime.combine(date.min, time_1) -
            datetime.combine(date.min, time_2)).total_seconds()


class BusinessHours(object):
    """Calculates business hours between two timestamps.

    Note
    ----
    Please take care of the type of the arguments.

    Attributes
    ----------
    from_dt : datetime.datetime
    to_dt : datetime.datetime
    working_hours : [datetime.time, datetime.time]
    weekend : [int, int]
    holidays : [datetime.date, datetime.date, ...]
    """
    def __init__(self, from_dt, to_dt,
                 working_hours=(time(9), time(17)),
                 weekend=(6, 7),
                 holidays=()):
        """
        Parameters
        ----------
        from_dt : datetime.datetime
            start datetime

        to_dt : datetime.datetime
            end datetime

        working_hours : (datetime.time, datetime.time)
            start and end time of working hours

        weekends : tuple of int
            list of weekdays

        holidays : tuple of datetime.date
            list of holidays as datetime.date objects
        """
        assert isinstance(from_dt, datetime)
        assert isinstance(to_dt, datetime)
        assert isinstance(working_hours, tuple)
        assert len(working_hours) == 2
        assert isinstance(working_hours[0], time)
        assert isinstance(working_hours[1], time)
        assert isinstance(weekend, tuple)
        assert isinstance(holidays, tuple)
        for holiday in holidays:
            assert isinstance(holiday, date)
        for day in weekend:
            assert isinstance(day, int)

        self.from_dt = from_dt
        self.to_dt = to_dt
        self.working_hours = working_hours
        self.weekends = weekend
        self.holidays = holidays

    @property
    def total_seconds(self):
        """Total business seconds elapsed between give start and end time
        """
        # Explanation
        # ----|~~~~~~|----
        #     A      B     ; working hours
        A = self.working_hours[0]
        B = self.working_hours[1]
        X = self.from_dt
        Y = self.to_dt
        total_sec = 0

        C = X.date() + timedelta(days=1)

        # calculate seconds for days except the first and last day
        while C < Y.date():
            if (C.isoweekday() not in self.weekends) and \
                    (C not in self.holidays):
                total_sec += subtract_time(B, A)
            C += timedelta(days=1)

        # calculate seconds for the first and last day
        # case 1: the first and last day are same
        if X.date() == Y.date():
            if (X.isoweekday() not in self.weekends) and \
               (X.date() not in self.holidays):
                if (X.time() < A and Y.time() < A) or \
                   (X.time() > B and Y.time() > B):
                    X = Y
                elif X.time() < A:
                    X = datetime.combine(X.date(), A)
                elif Y.time() > B:
                    Y = datetime.combine(Y.date(), B)
                total_sec += (Y-X).total_seconds()

        # case 2: the first and last day are different
        else:
            if (X.isoweekday() not in self.weekends) and \
               (X.date() not in self.holidays):
                if X.time() < A:
                    total_sec += subtract_time(B, A)
                elif X.time() > B:
                    # count from next day, done above
                    pass
                else:
                    total_sec += subtract_time(B, X.time())

            if (Y.isoweekday() not in self.weekends) and \
               (Y.date() not in self.holidays):
                if Y.time() <= A:
                    # count till previous day, done above
                    pass
                elif Y.time() > B:
                    total_sec += subtract_time(B, A)
                else:
                    total_sec += subtract_time(Y.time(), A)

        return total_sec

    @property
    def total_hours(self):
        """Total business hours elapsed between given times
        """
        return self.total_seconds / 3600

    @property
    def total_minutes(self):
        """Total business minutes elapsed between given times"""
        return self.total_seconds / 60

    @property
    def total_days(self):
        """Total business days elapsed between given times
        """
        return self.total_seconds / 86400


if __name__ == "__main__":
    start = datetime.strptime("2017-06-29T9:00:00Z", "%Y-%m-%dT%H:%M:%SZ")
    end = datetime.strptime("2017-07-03T10:00:00Z", "%Y-%m-%dT%H:%M:%SZ")
    print(start, end)
    holidays = (
        date(2017, 6, 29),
        date(2017, 7, 1),
        date(2017, 7, 2)
    )
    b = BusinessHours(start, end, weekend=(6, 7), holidays=holidays)
    print(b.total_seconds)
    print(b.total_hours)
    print(b.total_days)
