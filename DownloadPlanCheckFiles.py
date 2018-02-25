""" Download Plan Check Files
    
    This Mobius3D script prompts you to enter all or part of a patient name or ID, then 
    downloads all plan check files to folders within a destination folder. A subfolder is
    created for each plan check based on the plan name. Note, if multiple plan checks 
    exist for the same plan, files with the same name will get overwritten. The RTDOSE 
    files and check PDF will not, however, as they are uniquely named.
    
    This program is free software: you can redistribute it and/or modify it under
    the terms of the GNU General Public License as published by the Free Software
    Foundation, either version 3 of the License, or (at your option) any later
    version.
    
    This program is distributed in the hope that it will be useful, but WITHOUT
    ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS
    FOR A PARTICULAR PURPOSE. See the GNU General Public License for more details.
    
    You should have received a copy of the GNU General Public License along with
    this program. If not, see <http://www.gnu.org/licenses/>.
    """

__author__ = 'Mark Geurts'
__contact__ = 'mark.w.geurts@gmail.com'
__date__ = '2018-02-23'

__version__ = '1.0.0'
__status__ = 'Development'
__deprecated__ = False
__reviewer__ = 'N/A'

__reviewed__ = 'YYYY-MM-DD'
__mobius__ = '2.1.0'
__maintainer__ = 'Mark Geurts'

__email__ =  'mark.w.geurts@gmail.com'
__license__ = 'GPLv3'
__copyright__ = 'Copyright (C) 2018, University of Wisconsin Board of Regents'

# Specify import statements
import os
import requests

# Define server URL and plan limit
serverURL = 'http://mobius.uwhealth.wisc.edu/'
limit = 99999

# Prompt user for username, password
username = raw_input('Enter Mobius3D username: ')
password = raw_input('Enter password: ')

# Authenticate against Mobius3D server
s = requests.Session()
s.post('{}auth/login'.format(serverURL), {'username': username, 'password': password})

# Prompt user for patient name, export directory
name = raw_input('Enter all or part of patient name or ID to download: ')
saveDir = raw_input('Enter the directory to download files to: ')

# Download plan list
r = s.get('{}_plan/list?sort=date&descending=1&limit={}'.format(serverURL, int(limit)))
patientList = r.json()

# Loop over every patient
for patient in patientList['patients']:

	# If this patient is a validation patient
	if name in patient['patientName'] or name in patient['patientId']:

		# And every plan check in each patient
		for plan in patient['plans']:      
		
			# Skip if there aren't results (results will be empty)
			if not plan['results']:
				continue
			
			#  Retrieve JSON plan information
			r = s.get('{}/check/details/{}?format=json'.format(serverURL, \
			    plan['request_cid']))
			planData = r.json()
			
			# Make subdirectory in save directory using plan name
			if not os.path.exists('{}/{}'.format(saveDir, plan['notes'])):
				os.mkdir('{}/{}'.format(saveDir, plan['notes']))
				
			# Retrieve JSON list of the raw data files
			r = s.get('{}/check/details/{}/data?format=json'.format(serverURL, plan['request_cid']))
			planFiles = r.json()
			
			# Loop through data files
			for files in planFiles['data']:
			
				# If file already exists, delete it
				if os.path.exists('{}/{}/{}'.format(saveDir, plan['notes'], \
				        files['filename'])):
					os.remove('{}/{}/{}'.format(saveDir, plan['notes'], files['filename']))
			
				print 'Saving {}/{}/{}'.format(saveDir, plan['notes'], files['filename'])
			
				# Write data file to save directory
				with open('{}/{}/{}'.format(saveDir, plan['notes'], \
				        files['filename']), 'wb') as f:
					f.write(s.get('{}/check/attachment/{}/{}'.format(serverURL, \
					    plan['request_cid'], files['filename'])).content)
			
				f.close()
