#!/usr/bin/env python3

"""
  Analysis utilities for Soft Drop jet analysis with track dataframe.
  
  Author: James Mulligan (james.mulligan@berkeley.edu)
"""

from __future__ import print_function

# General
import os
import sys
import math

# Data analysis and plotting
import uproot
import pandas
import numpy as np
from array import *
import ROOT

# Base class
from pyjetty.alice_analysis.analysis.base import analysis_utils

################################################################
class AnalysisUtils_Obs(analysis_utils.AnalysisUtils):
  
  #---------------------------------------------------------------
  # Constructor
  #---------------------------------------------------------------
  def __init__(self, observable='', **kwargs):
    super(AnalysisUtils_Obs, self).__init__(**kwargs)
    
    self.observable = observable

  #---------------------------------------------------------------
  # Get observable settings (i.e. list that stores the observable setting, e.g. subjetR)
  # from observable config block
  #---------------------------------------------------------------
  def obs_settings(self, observable, obs_config_dict, obs_subconfig_list):
  
    if observable == 'subjet_z':
      obs_settings = [obs_config_dict[name]['subjet_R'] for name in obs_subconfig_list]
    elif observable == 'jet_axis':
      obs_settings = [obs_config_dict[name]['axis'] for name in obs_subconfig_list]
    else:
      obs_settings = [None for _ in obs_subconfig_list]
      
    return obs_settings
    
  #---------------------------------------------------------------
  # Get subobservable label (e.g. formatted label for subjetR)
  #---------------------------------------------------------------
  def formatted_subobs_label(self, observable):
  
    if observable == 'subjet_z':
      label = '#it{R}_{subjet}'
    elif observable == 'jet_axis':
      label = '#Delta #it{R}_{axis}'
    else:
      label = None
      
    return label

  #---------------------------------------------------------------
  # Compute scale factor to vary prior of observable
  #
  # Note that prior_variation_parameter is the parameter used to scale both
  # the pt prior (assumed to be a change to the power law exponent) and the observable prior,
  # and is typically taken to be +/- 0.5.
  #
  # This function overrides the virtual function in analysis_utils.py
  #---------------------------------------------------------------
  def prior_scale_factor_obs(self, obs_true, prior_variation_parameter):
  
    if self.observable == 'zg':
      scale_factor = math.pow(obs_true, prior_variation_parameter)
    elif self.observable == 'theta_g':
      scale_factor = (1 + obs_true)
    elif self.observable == 'subjet_z':
      scale_factor = (1 + obs_true)
    elif self.observable == 'jet_axis':
      scale_factor = (1 + obs_true)
    else:
      raise ValueError('No observable is defined in prior_scale_factor_obs()!')
      
    return scale_factor
    
  #---------------------------------------------------------------
  #---------------------------------------------------------------
  #---------------------------------------------------------------
  # All observable-specific edits should be above here!
  #---------------------------------------------------------------
  #---------------------------------------------------------------
  #---------------------------------------------------------------

  #---------------------------------------------------------------
  # Get label from obs_setting and sd_setting
  #---------------------------------------------------------------
  def obs_label(self, obs_setting, sd_setting):

    obs_label = ''
    if obs_setting:
      obs_label += '{}'.format(obs_setting)
    if sd_setting:
      obs_label += '{}'.format(self.sd_label(sd_setting))
    return obs_label

  #---------------------------------------------------------------
  # Get formatted Soft Drop label from sd_setting = [zcut, beta]
  #---------------------------------------------------------------
  def formatted_sd_label(self, sd_setting):

    text = 'z_{cut} = ' + str(sd_setting[0]) + '   #beta = ' + str(sd_setting[1])
    return text
    
  #---------------------------------------------------------------
  # Get name of response THn
  #---------------------------------------------------------------
  def name_thn(self, observable, jetR, obs_label):
  
      return 'hResponse_JetPt_{}_R{}_{}Scaled'.format(observable, jetR, obs_label)

  #---------------------------------------------------------------
  # Get name of response THn, rebinned
  #---------------------------------------------------------------
  def name_thn_rebinned(self, observable, jetR, obs_label):
  
      return 'hResponse_JetPt_{}_R{}_{}_rebinned'.format(observable, jetR, obs_label)
  
  #---------------------------------------------------------------
  # Get name of 2D data histogram
  #---------------------------------------------------------------
  def name_data(self, observable, jetR, obs_label):
  
      return 'h_{}_JetPt_R{}_{}'.format(observable, jetR, obs_label)
  
  #---------------------------------------------------------------
  # Get name of 2D data histogram, rebinned
  #---------------------------------------------------------------
  def name_data_rebinned(self, observable, jetR, obs_label):
  
      return 'h_{}_JetPt_R{}_{}_rebinned'.format(observable, jetR, obs_label)

  #---------------------------------------------------------------
  # Get regularization parameter
  #---------------------------------------------------------------
  def get_reg_param(self, obs_settings, sd_settings, obs_subconfig_list, obs_config_dict, obs_label, observable, jetR):
    
    for i, _ in enumerate(obs_subconfig_list):
    
      obs_setting = obs_settings[i]
      sd_setting = sd_settings[i]
      
      if self.obs_label(obs_setting, sd_setting) == obs_label:
        
        config_name = obs_subconfig_list[i]
        reg_param = obs_config_dict[config_name]['reg_param'][jetR]
        #print('reg_param for {} {} jetR={}: {}'.format(obs_label, observable, jetR, reg_param))
          
        return reg_param
      
      else:
        continue
        
  #---------------------------------------------------------------
  # Compute SD tagging rate, based on MC correction
  #---------------------------------------------------------------
  def tagging_rate(self, jetR, min_pt_truth, max_pt_truth, hData2D, hMC_Det2D, hMC_Truth2D):

    hData2D.GetXaxis().SetRangeUser(min_pt_truth, max_pt_truth)
    hData = hData2D.ProjectionY()
    n_jets_inclusive = hData.Integral(0, hData.GetNbinsX()+1)
    n_jets_tagged = hData.Integral(1, hData.GetNbinsX())
    fraction_tagged_data =  n_jets_tagged/n_jets_inclusive
    #print('fraction_tagged_data: {}'.format(fraction_tagged_data))

    hMC_Det2D.GetXaxis().SetRangeUser(min_pt_truth, max_pt_truth)
    hMC_Det = hMC_Det2D.ProjectionY()
    n_jets_inclusive = hMC_Det.Integral(0, hMC_Det.GetNbinsX()+1)
    n_jets_tagged = hMC_Det.Integral(1, hMC_Det.GetNbinsX())
    fraction_tagged_mc_det =  n_jets_tagged/n_jets_inclusive
    #print('fraction_tagged_mc_det: {}'.format(fraction_tagged_mc_det))
    
    hMC_Truth2D.GetXaxis().SetRangeUser(min_pt_truth, max_pt_truth)
    hMC_Truth = hMC_Truth2D.ProjectionY()
    n_jets_inclusive = hMC_Truth.Integral(0, hMC_Truth.GetNbinsX()+1)
    n_jets_tagged = hMC_Truth.Integral(1, hMC_Truth.GetNbinsX())
    fraction_tagged_mc_truth =  n_jets_tagged/n_jets_inclusive
    #print('fraction_tagged_mc_truth: {}'.format(fraction_tagged_mc_truth))

    fraction_tagged = fraction_tagged_data * fraction_tagged_mc_truth / fraction_tagged_mc_det
    #print('fraction_tagged: {}'.format(fraction_tagged))

    return fraction_tagged
