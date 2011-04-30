#!/usr/bin/env python

import random
import math

CHOICES = ["BA", "BE", "LE", "CH"]
def choose1():
    return random.choice(CHOICES)
def choose3():
    return [choose1() for i in xrange(3)]
def payoff(chosen):
    if chosen[0] == "BA":
        if chosen[1] == chosen[2] == "BA":
            return 20-1
        else:
            return 0-1
    elif chosen[0] == "BE":
        if chosen[1] == chosen[2] == "BE":
            return 15-1
        else:
            return 0-1
    elif chosen[0] == "LE":
        if chosen[1] == chosen[2] == "LE":
            return 5-1
        else:
            return 0-1
    elif chosen[0] == "CH":
        if chosen[1] == chosen[2] == "CH":
            return 3-1
        elif chosen[1] == "CH":
            return 2-1
        else:
            return 1-1
    else:
        raise Exception("WHAT?")

N = 1000000
cpayoffs = {}
cwins = {}
for sym in CHOICES:
    cpayoffs[sym] = 0
    cwins[sym] = 0
    for i in xrange(N):
        chosen = choose3()
        chosen[0] = sym
        p = payoff(chosen)
        #print chosen, p
        cpayoffs[sym] += p
        if p >= 0:
            cwins[sym] += 1
    cpayoffs[sym] /= float(N)
    cwins[sym] /= float(N)

print "payoffs:"
s = 0
for k, v in cpayoffs.iteritems():
    s += v
    print k, v
print "avg payoff", s
print ""

print "wins:"
t = 0
for k, v in cwins.iteritems():
    t += v
    print k, v
print "avg wins", t/4.0

START = 10.0
all_rounds = []
for i in xrange(100000):
    #print "RUN",i
    coins = START
    rounds = 0 
    while coins > 1:
        #print "COINS",coins
        rounds += 1
        chosen = choose3()
        p = payoff(chosen)
        #print "PAYOFF",p
        coins += p
    #print "ROUNDS", rounds
    all_rounds.append(rounds)

def avg(lst):
    return float(sum(lst))/len(lst)
def stdev(lst):
    a = avg(lst)
    return math.sqrt(avg([(lst[i] - a)**2 for i in xrange(len(lst))]))

print "avg num rounds", avg(all_rounds)
print "stdev         ", stdev(all_rounds)
