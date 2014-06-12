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
                    yield ('T',mvalues)
        except Exception, e:
            stderr.write('Error in line:\n'+line+'\n')
            stderr.write(str(e)+'\n')
            self.increment_counter('MrJob Counters','mapper-error',1)
            yield ('error',1)
            
    def reducer(self, key, mlists):
        self.increment_counter('MrJob Counters','reducer',1)
        if key=='T':
            mvalues_f = [item for sublist in mlists for item in sublist]
            mvalues_f = np.array(mvalues_f)
            hist, bins = np.histogram(mvalues_f,bins=100)
            center = (bins[:-1]+bins[1:])/2
            for j in xrange(len(hist)):
                yield (center[j],hist[j])

if __name__ == '__main__':
    MRWeatherSanity.run()