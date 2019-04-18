import sys
from datetime import datetime, timedelta
import pylab as pl
from discwt import getdata_full, takedata_eachm

def get_first_clock (fname):
    with open(fname) as f:
        for line in f:
            if 'N' in line:
                tmp = line.split('N')
                tmp = tmp[0].split()
                if len(tmp) != 2: continue
                if 'T' not in tmp[0]: continue
                if len(tmp[0].split('T')) != 2: continue
                try: tmp[1] = float(tmp[1])
                except ValueError: continue
                return tmp
    print 'Cannot find first clock'
    raise KeyError

def get_time (clocks):
    dates, clock = clocks.split('T')
    year, month, date = map(int,dates.split('.'))
    clock = clock.split(':')
    hour, minute = map(int,clock[:2])
    second, point = clock[2].split('.')
    second = int(second)
    microsec = int(round(float('.'+point)*1e6))
    return year, month, date, hour, minute, second, microsec

def get_time_diff (clock1, clock2):
    year1, mon1, day1, hour1, min1, sec1, msec1 = get_time (clock1)
    year2, mon2, day2, hour2, min2, sec2, msec2 = get_time (clock2)
    time1 = datetime(year1, mon1, day1, hour1, min1, sec1, msec1)
    time2 = datetime(year2, mon2, day2, hour2, min2, sec2, msec2)
    totsecs = (time2-time1).total_seconds()
    return totsecs

def get_sweeps_time (fname):
    clock0,cputime0 = get_first_clock (fname)
    its,ns,ens,enps,terrs,ms,msu2s,clocks,cputimes = getdata_full (fname)
    walltimes = [get_time_diff (clock0, clock) for clock in clocks]

    ns, ms, msu2s, walltimes, cputimes = takedata_eachm ((ns, ms, msu2s, walltimes, cputimes), ns, ms)
    print 'cpu time: ',str(timedelta(seconds=cputimes[-1]))
    print 'wall time: ',str(timedelta(seconds=walltimes[-1]))
    return ns, ms, msu2s, walltimes, cputimes

def plot_time (fname):
    ns, ms, msu2, walltimes, cputimes = get_sweeps_time (fname)
    pl.plot (ms, walltimes, '-ok', label='wall time')
    pl.plot (ms, cputimes, '-xr', mew=2, label='cpu time')
    pl.xlabel ('m',fontsize=20)
    pl.ylabel ('time (sec)', fontsize=20)
    pl.legend (loc='upper left')
    pl.show()

if __name__ == '__main__':
    fs = sys.argv[1:]
    for fname in fs:
        ns, ms, msu2, walltimes, cputimes = get_sweeps_time (fname)
        pl.plot (ms, cputimes, marker='o', mew=2, label='')
    pl.xlabel ('m',fontsize=20)
    pl.ylabel ('time (sec)', fontsize=20)
    pl.show()
