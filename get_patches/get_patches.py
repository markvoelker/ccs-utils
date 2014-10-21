#!/usr/bin/python

"""
A quick-hack script that generates a list of local patches for all
components that we have local patches for, and drops them into a
directory for you to peruse.
"""

import glob
import os
import shutil
import subprocess

def fetch_patches(component, grep_string='Not-in-upstream: true'):
    """
    Given a component name and a phrase in the git log to grep for,
    fetches patchfiles for all matching commits and drops them into
    the patch directory for that component.
    """

    # Get a list of SHA's that we care about
    print 'git --no-pager log --grep \'' + grep_string +  '\' --format=\'%H\''
    shas = subprocess.check_output([
        'git', '--no-pager', 'log', '--grep', grep_string,
        '--format=%H']).rstrip().split("\n")
    shas = filter(None, shas)

    # Iterate through the SHA's generating patches.
    for sha in shas:
        print 'git format-patch -1 ' + sha.rstrip()
        subprocess.call(['git', 'format-patch', '-1', sha.rstrip()])

    # Move all those patches to the patch dir.
    if len(shas) > 0:
        # create a patch directory for this component
        if not os.path.exists(PATCHDIR + '/' + component):
            os.makedirs(PATCHDIR + '/' + component)

        # change to the directory of the checkout
        for filename in glob.glob(os.path.join(os.getcwd(), '*.patch')):
            shutil.copy(filename, PATCHDIR + '/' + component)


# A list of all of the components we need to generate patches for.
COMPONENTS = ['cinder', 'nova', 'neutron', 'horizon', 'keystone',
              'ceilometer', 'python-ceilometerclient',
              'python-cinderclient', 'python-novaclient',
              'python-neutronclient', 'python-keystoneclient',
              'heat', 'python-heatclient', 'glance', 'python-glanceclient']

# Figure out if we have a patches directory and make it if not
PATCHDIR = os.getcwd() + '/patches'
if not os.path.exists(PATCHDIR):
    os.makedirs(PATCHDIR)

# Iterate through the list
for comp in COMPONENTS:
    # Get a clean checkout
    subprocess.call([
        'git', 'clone', '-b', 'cis-havana',
        "https://github.com/CiscoSystems/" + comp])

    # Change to the component's checkout directory
    print 'cd ' + os.getcwd() + '/' + comp
    os.chdir(os.getcwd() + '/' + comp)

    # Fetch ALL THE PATCHES!
    grep_strings = [
        'Not-in-upstream: true',
        'Backported-from: juno'
    ]
    for string in grep_strings:
        fetch_patches(comp, string)

    # Go back up
    print 'cd ' + os.getcwd() + '/' + '..'
    os.chdir(os.getcwd() + '/' + '..')
