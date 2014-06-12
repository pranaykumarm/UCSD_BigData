"""
count the number of measurement series with non-NaN values for all 365 days
"""
import sys
sys.path.append('/usr/lib/python2.6/dist-packages')
from mrjob.job import MRJob
import re
from sys import stderr
import numpy as np

elementType = 'TMAX'
key = 0   # 0 for station, 2 for year

class MRWeatherCountMeasurements(MRJob):

    def mapper(self, _, line):
        try:
            self.increment_counter('MrJob Counters','mapper',1)
            elements=line.split(',')
            mvalues = np.array(elements[3:])
            if elements[0]!='station':
                if elements[1]==elementType:    
                    if np.where(mvalues=='',True,False).any():
                        out=(elements[key],0)
                    else:
                        out=(elements[key],365)
                else:
                    out=(elements[key],0)
            else:
                out=('header',1)
        except Exception, e:
            stderr.write('Error in line:\n'+line)
            stderr.write(e)
            self.increment_counter('MrJob Counters','mapper-error',1)
            out=('error',1)
        finally:
            yield out
            
    def combiner(self, word, counts):
        self.increment_counter('MrJob Counters','combiner',1)
        yield (word, sum(counts))

    def reducer(self, word, counts):
        self.increment_counter('MrJob Counters','reducer',1)
        yield (word, sum(counts))

if __name__ == '__main__':
    MRWeatherCountMeasurements.run()