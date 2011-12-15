#!/usr/bin/python

# This contains a wrapper around the vowpal wabbit machine learning system.

import subprocess

class VwLearner:    
    def __init__(self):
        p = subprocess.PIPE
        args = ['vw', '-d', '/dev/stdin', '-p', '/dev/stdout']
        self.vw_proc = subprocess.Popen(args, stdin=p, stdout=p)

    def predict(self, vec):
        """ Return a prediction for the given vector.
        
        vec is a list of strings in vw format, label:weight."""
        self._write_vec(vec)
        pred = float(self.vw_proc.stdout.readline())
        return pred

    def learn(self, vec, label):
        """ Learn from given vec, label pair."""
        self.vw_proc.stdin.write(str(label) + ' ')
        self._write_vec(vec)
        ignored_train_msg = self.vw_proc.stdout.readline()
        
    def _write_vec(self, vec):
        self.vw_proc.stdin.write('| ')
        for val in vec:
            self.vw_proc.stdin.write(val)
            self.vw_proc.stdin.write(' ')
        self.vw_proc.stdin.write('\n')

if __name__ == '__main__':
    vw = VwLearner()
    vw.learn(['1', '2'], 0)
    vw.learn(['3', '4:2'], 1.0)
    vw.learn(['5', '6'], .5)
    vw.learn(['5', '7'], .5) 
    vw.learn(['5'], .5) 
    vw.learn(['1'], .1) 
    print vw.predict(['1'])
    print vw.predict(['1', '5'])
    print vw.predict(['3', '4'])
    print vw.predict(['3', '5'])
