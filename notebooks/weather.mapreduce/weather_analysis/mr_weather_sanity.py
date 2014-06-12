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
            self.increment_counter('MrJob Counters','mapper',1)
            elements=line.split(',')      
            if (elements[1]=='TMIN')|(elements[1]=='TMAX'):
                mvalues = []
                for e in elements[3:]:
                    if e!='':
                        mvalues.append(float(e))
                mvalues = np.array(mvalues)
                hist, bins = np.histogram(mvalues,bins=200,range=(-200.5,200.5))
                center = (bins[:-1]+bins[1:])/2
                for j in xrange(len(hist)):
                    yield (center[j],hist[j])
        except Exception, e:
            stderr.write('Error in line:\n'+line+'\n')
            stderr.write(str(e)+'\n')
            self.increment_counter('MrJob Counters','mapper-error',1)
            yield ('error',1)
            
    def combiner(self, key, counts):
        self.increment_counter('MrJob Counters','combiner',1)
        yield (key,sum(counts))

    def reducer(self, key, counts):
        self.increment_counter('MrJob Counters','reducer',1)
        yield (key,sum(counts))

if __name__ == '__main__':
    MRWeatherSanity.run()