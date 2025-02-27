'''
this module does bla bla
'''

from datetime import timedelta
from datetime import datetime as dt


class TimeDelta(timedelta):
    '''
    some doc here
    '''

    def __str__(self):
        _times = super(TimeDelta, self).__str__().split(':')
        if "," in _times[0]:
            _hour = int(_times[0].split(',')[-1].strip())
            if _hour:
                _times[0] += " hours" if _hour > 1 else " hour"
            else:
                _times[0] = _times[0].split(',')[0]
        else:
            _hour = int(_times[0].strip())
            if _hour:
                _times[0] += " hours" if _hour > 1 else " hour"
            else:
                _times[0] = ""
        _min = int(_times[1])
        if _min:
            _times[1] += " minutes" if _min > 1 else " minute"
        else:
            _times[1] = ""
        _sec = int(_times[2])
        if _sec:
            _times[2] += " seconds" if _sec > 1 else " second"
        else:
            _times[2] = ""
        return ", ".join([i for i in _times if i]).strip(" ,").title()


def datetime_to_elapsed(date):
    '''
    some doc here
    '''
    diff = str(TimeDelta(seconds=int((dt.now()-date).total_seconds())))
    return diff


if __name__ == '__main__':
    a = dt(2022, 12, 28, 19, 0, 0)
    b = dt.now()
    secs = (b-a).total_seconds()
    print(TimeDelta(seconds=int(secs)))
