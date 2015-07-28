#!/usr/bin/env python
# -*- coding: utf-8 -*-

from twitchcancer.diagnosis import Diagnosis

def cure(source):
  diagnosis = Diagnosis()
  
  for message in source:
    if diagnosis.diagnose(message) == []:
      print(message)
