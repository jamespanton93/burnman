# This file is part of BurnMan - a thermoelastic and thermodynamic toolkit for the Earth and Planetary Sciences
# Copyright (C) 2012 - 2017 by the BurnMan team, released under the GNU
# GPL v2 or later.


# This is a standalone program that converts the Holland and Powell data format into the standard burnman format (printed to stdout)
# It only outputs properties of solid endmembers - other endmembers are
# currently ignored.


import sys
import os.path

if os.path.isfile('tc-ds62.txt') == False:
    print('This code requires the data file tc-ds62.txt.')
    print(
        'This file is bundled with the software package THERMOCALC, which can be found here:')
    print(
        'http://www.metamorph.geo.uni-mainz.de/thermocalc/dataset6/index.html')
    print('')
    print('Please download the file and place it in this directory.')
    exit()

# Components
components = ['Si', 'Ti', 'Al', 'Fe', 'Mg', 'Mn', 'Ca', 'Na',
              'K', 'O', 'H', 'C', 'Cl', 'e-', 'Ni', 'Zr', 'S', 'Cu', 'Cr']


class Endmember:

    def __init__(self, name, atoms, formula, sites, comp, H, S, V, Cp, a, k, flag, od):
        self.name = name  # Name of end member
        self.atoms = atoms  # Number of atoms in the unit formula
        self.formula = formula
        self.sites = sites  # Notional number of sites
        self.comp = comp  # Composition
        self.H = H  # Enthalpy
        self.S = S  # Entropy
        self.V = V  # Volume
        self.Cp = Cp  # Heat capacity (c0 + c1*T + c2*T**2 + c3*T**(-0.5))
        self.a = a  # Thermal expansion
        self.k = k  # Bulk Modulus (and first two derivatives wrt pressure)
        self.flag = flag
        self.od = od


# Read dataset
with open('tc-ds62.txt', 'r') as f:
    ds = [line.split() for line in f]

def getmbr(ds, mbr):
    mbrarray = []
    for i in range(0, int(ds[0][0])):
        if ds[i * 4 + 3][0] == mbr:
            atoms = 0.0
            formula = ''
            for j in range(3, len(ds[i * 4 + 3]) - 1, 2):
                atoms += float(ds[i * 4 + 3][j])
                formula = formula + \
                    components[int(ds[i * 4 + 3][j - 1]) - 1] + str(
                        round(float(ds[i * 4 + 3][j]), 10))
            if mbr.endswith('L'):
                flag = -2
                od = [0]
            else:
                flag = int(ds[i * 4 + 6][4])
            endmember = Endmember(mbr, atoms, formula, int(ds[i * 4 + 3][1]), list(map(float, ds[i * 4 + 3][2:(len(ds[i * 4 + 3]) - 1)])), float(ds[i * 4 + 4][0]), float(
                ds[i * 4 + 4][1]), float(ds[i * 4 + 4][2]), map(float, ds[i * 4 + 5]), float(ds[i * 4 + 6][0]), list(map(float, ds[i * 4 + 6][1:4])), flag, list(map(float, ds[i * 4 + 6][5:])))
            return endmember

with open('HP_2011_ds62.py', 'wb') as outfile:
    outfile.write('# This file is part of BurnMan - a thermoelastic and '
                  'thermodynamic toolkit for the Earth and Planetary Sciences\n'
                  '# Copyright (C) 2012 - 2018 by the BurnMan team, '
                  'released under the GNU \n# GPL v2 or later.\n\n\n'
                  '"""\n'
                  'HP_2011 (ds-62)\n'
                  'Endmember minerals from Holland and Powell 2011 and references therein\n'
                  'Update to dataset version 6.2\n'
                  'The values in this document are all in S.I. units,\n'
                  'unlike those in the original tc-ds62.txt\n'
                  'File autogenerated using HPdata_to_burnman.py\n'
                  '"""\n\n'
                  'from ..mineral import Mineral\n'
                  'from ..processchemistry import dictionarize_formula, formula_mass\n\n')

    outfile.write('"""\n'
                  'ENDMEMBERS\n'
                  '"""\n\n')
    
    formula = '0'
    for i in range(int(ds[0][0])):
        mbr = ds[i * 4 + 3][0]
        M = getmbr(ds, mbr)
        if mbr == 'and':  # change silly abbreviation
            mbr = 'andalusite'
        if M.flag != -1 and M.flag != -2 and M.k[0] > 0:
            outfile.write('class {0} (Mineral):\n'.format(mbr)+
                          '    def __init__(self):\n'
                          '        formula = \'{0}\''.format(M.formula)+'\n'
                          '        formula = dictionarize_formula(formula)\n'
                          '        self.params = {{\n'
                          '            \'name\': \'{0}\','.format(M.name)+'\n'
                          '            \'formula\': formula,\n'
                          '            \'equation_of_state\': \'hp_tmt\',\n'
                          '            \'H_0\': {0},'.format(M.H * 1e3)+'\n'
                          '            \'S_0\': {0},'.format(M.S * 1e3)+'\n'
                          '            \'V_0\': {0},'.format(M.V * 1e-5)+'\n'
                          '            \'Cp\': {0},'.format([round(M.Cp[0] * 1e3, 10), round(M.Cp[1] * 1e3, 10), round(M.Cp[2] * 1e3, 10), round(M.Cp[3] * 1e3, 10)])+'\n'
                          '            \'a_0\': {0},'.format(M.a)+'\n'
                          '            \'K_0\': {0},'.format(M.k[0] * 1e8)+'\n'
                          '            \'Kprime_0\': {0},'.format(M.k[1])+'\n'
                          '            \'Kdprime_0\': {0},'.format(M.k[2] * 1e-8)+'\n'
                          '            \'n\': sum(formula.values()),\n'
                          '            \'molar_mass\': formula_mass(formula)}\n')
            if M.flag != 0:
                outfile.write('        self.property_modifiers = [[\n')
            if M.flag == 1:
                outfile.write('            \'landau_hp\', {{\'P_0\': 100000.0,\n'
                              '                          \'T_0\': 298.15,\n'
                              '                          \'Tc_0\': {0},'.format(M.od[0])+'\n'
                              '                          \'S_D\': {0},'.format(M.od[1] * 1e3)+'\n'
                              '                          \'V_D\': {0}}}]]'.format(M.od[2] * 1e-5)+'\n\n')
            if M.flag == 2:
                outfile.write('            \'bragg_williams\', {{\'deltaH\': {0},'.format(M.od[0] * 1e3)+'\n'
                              '                               \'deltaV\': {0},'.format(M.od[1] * 1e-5)+'\n'
                              '                               \'Wh\': {0},'.format(M.od[2] * 1e3)+'\n'
                              '                               \'Wv\': {0},'.format(M.od[3] * 1e-5)+'\n'
                              '                               \'n\': {0},'.format(M.od[4])+'\n'
                              '                               \'factor\': {0}}}]]'.format(M.od[5])+'\n')
            outfile.write('        Mineral.__init__(self)\n\n')


    # Process uncertainties
    import numpy as np
    n_mbrs = int(ds[0][0])
    
    names = []
    for i in range(n_mbrs):
        names.append(ds[i*4+3][0])
        
    cov = []
    for i in range(n_mbrs*4+4, len(ds)-2):
        cov.extend(map(float, ds[i]))

    i_utr = np.triu_indices(n_mbrs)
    i_ltr = np.tril_indices(n_mbrs)
    M = np.zeros((n_mbrs, n_mbrs))

    M[i_utr] = cov[1:]
    M[i_ltr] = M.T[i_ltr]
    
    M = M*1.e6 # (kJ/mol)^2 -> (J/mol)^2

    
    d = {'endmember_names':names,
         'covariance_matrix':M}
    
    np.set_printoptions(threshold='nan')
  
    import pprint
    pp = pprint.PrettyPrinter(indent=0, width=160, depth=3, stream=outfile)

    outfile.write('\n# Variance-covariance matrix\n'
                  '# cov is a dictionary containing:\n'
                  '#     - names: a list of endmember names\n'
                  '#     - covariance_matrix: a 2D variance-covariance array for the endmember enthalpies of formation\n\n'
                  'from numpy import array\n'
                  'cov = ')
    pp.pprint(d)

    outfile.write('\n')
