"""
count the number of measurements of each type
"""
import sys
sys.path.append('/usr/lib/python2.6/dist-packages')
from mrjob.job import MRJob
import re
from sys import stderr

elementType = 'TMAX'
key = 2   # 0 for station, 2 for year

class MRWeatherCountMeasurements(MRJob):

    def mapper(self, _, line):
        try:
            self.increment_counter('MrJob Counters','mapper',1)
            elements=line.split(',')
            measurements_per_line = 0
            if elements[1]==elementType:    
                for j in range(365):
                    if isinstance(elements[j+3], basestring):
                        measurements_per_line += 1        
            if elements[0]!='station':
                out=(elements[key],measurements_per_line)
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