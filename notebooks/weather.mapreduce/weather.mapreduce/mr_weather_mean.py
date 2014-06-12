"""
compute mean vector for each partition
"""
import sys
sys.path.append('/usr/lib/python2.7/dist-packages')
from mrjob.job import MRJob
import re
from sys import stderr
import pickle, gzip
import pandas
import numpy as np

class MRWeatherMean(MRJob):

    #This adds options --stations for the location of where to get the lookup file
    def configure_options(self):
        super(MRWeatherMean,self).configure_options()
        self.add_file_option('--partitions')
    #This loads the lookup file into a field on the object
    def mapper_init(self):
        f = gzip.open( self.options.partitions, "rb" )
        pickleFile = pickle.Unpickler(f)
        self.partitions = pickleFile.load()
        f.close()

    def mapper(self, _, line):
        try:
            self.increment_counter('MrJob Counters','mapper',1)
            elements=line.split(',')       
            if elements[0]=='station':
                yield ('header',1)
            else:
                if elements[1]=='TMIN':
                    partitionID = int(self.partitions.ix[elements[0],'partitionID'])
                    N = (self.partitions.ix[elements[0],'N_TMIN365'])/365
                    mvalues = np.array(elements[3:])
                    if np.where(mvalues=='',True,False).any():
                        yield ('incomplete',1)
                    else:
                        # Only consider complete series
                        mvalues = mvalues.astype(np.float)
                        mvalues = mvalues/N
                        for i in xrange(365):
                            yield ((partitionID,i+1),mvalues[i])
                else:
                    yield ('other',1)
        except Exception, e:
            stderr.write('Error in line:\n'+line+'\n')
            stderr.write(str(e)+'\n')
            self.increment_counter('MrJob Counters','mapper-error',1)
            yield ('error',1)
            
    def combiner(self, word, counts):
        self.increment_counter('MrJob Counters','combiner',1)
        yield (word,sum(counts))

    def reducer(self, word, counts):
        self.increment_counter('MrJob Counters','reducer',1)
        yield (word,sum(counts))

if __name__ == '__main__':
    MRWeatherMean.run()