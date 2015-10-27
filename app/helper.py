#-*- coding: utf-8-*-
import datetime

def to_timestamp(t):
    return (t - datetime.datetime(1970,1,1)).total_seconds()