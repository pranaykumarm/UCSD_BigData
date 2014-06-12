"""
compute mean vector for each partition
"""
import sys
sys.path.append('/usr/lib/python2.7/dist-packages')
from mrjob.job import MRJob
import re
from sys import stderr
import numpy as np

class MRWeatherSanity(MRJob):

    def mapper(self, _, line):
        try:
            elements=line.split(',')      
            if (elements[1]=='TMIN')|(elements[1]=='TMAX'):
                #mvalues = []
                for e in elements[3:]:
                    if e!='':
                        yield(e, 1)
        except Exception, e:
            stderr.write('Error in line:\n'+line+'\n')
            stderr.write(str(e)+'\n')
            self.increment_counter('MrJob Counters','mapper-error',1)
            yield ('error',1)

    def combiner(self, key, mlists):
        yield(key, sum(mlists))
            
    def reducer(self, key, mlists):
        yield(key, sum(mlists))

if __name__ == '__main__':
    MRWeatherSanity.run()