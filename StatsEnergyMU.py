""" Compute MU and Beam Energy Utilization Statistics
    
    This Mobius3D script searches through the plan list and compiles a list of patient, 
    plan name, plan MU, as well as a list of per beam MU and energy. The script also 
    searches each plan name and tracks the plan MU for 3DCRT (2DC or 3DC in the name), 
    VMAT (VMA), SBRT (SBR or FSR), or SRS (SRS). The script ends by printing out a list of
    patient name, plan name, and plan MU, as well as statistics about the mean MU for each 
    modality and how much each modality and beam energy is utilized.
    
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

# Download plan list
r = s.get('{}_plan/list?sort=date&descending=1&limit={}'.format(serverURL, int(limit)))
patientList = r.json()

# Initialize statistics variables
patientNames = []
planNames = []
planUIDs = []
planMU = []
beamMU = []
beamEnergy = []
threeD = []
vmat = []
sbrt = []
srs = []

# Loop over every patient
i = 0
for patient in patientList['patients']:

    # Print status
    i = i + 1
    print 'Scanning patient {} of {}'.format(i, len(patientList['patients']))

    # Build a URL using the plan's request_cid to get information about each plan check
    try:

        # And every plan check in each patient
        for plan in patient['plans']:      
      
            # Skip plan if there aren't results
            if not plan['results']:
                continue
        
            r = s.get('{}check/details/{}?format=json'.format(serverURL, \
                plan['request_cid']))
            planData = r.json()
        
            # Skip plan if it has already been appended to the list
            if planData['settings']['plan_dicom']['sopinst'] in planUIDs:
                continue
            
            else:
                planUIDs.append(planData['settings']['plan_dicom']['sopinst'])
         
            # Compute total fraction MU for the first fraction group
            mu = 0
            for group, group_dict in planData['data']['fractionGroup_info']\
                    ['fractionGroup_num2info_dict'].items():
    
                if 'TrueBeam' not in group_dict['TreatmentMachineName']:
                    continue
        
                for beams, beam_dict in group_dict['beam_num2info_dict'].items():            
                    beamEnergy.append(beam_dict['energy_int'])
    
                for beams, beam_dict in group_dict['beam_num2meterset_dict'].items():
                    mu = mu + beam_dict['value']  
                    beamMU.append(beam_dict['value'])

                break

            # Save patient information to lists only if a plan was found
            if mu == 0:
                continue
        
            patientNames.append(patient['patientName'])
            planNames.append(plan['notes'])
            planMU.append(mu)     
    
            # Append based on plan type
            if '3DC' in plan['notes'] or '2DC' in plan['notes']:
                threeD.append(mu)
                continue
        
            if 'SBR' in plan['notes'] or 'FSR' in plan['notes']:
                sbrt.append(mu)
                continue

            if 'VMA' in plan['notes']:
                vmat.append(mu)
                continue
    
            if 'SRS' in plan['notes']:
                srs.append(mu)
                continue
    
    # Catch errors caused by missing plan data, and skip over to next patient
    except KeyError:
        continue

    # If the user stops the script, still print the results
    except KeyboardInterrupt:
        break

# Print patient list
print '=' * 60
for name, plan, mu in zip(patientNames, planNames, planMU):
    print '{} ({}): {:.0f}'.format(name, plan, mu)
   
# Print stats
print '=' * 60
m = len(threeD) + len(sbrt) + len(srs) + len(vmat)

if len(threeD) > 0:
    print 'Mean 3DCRT MU for {} ({:.1f}%) plans: {:.0f}'.format(len(threeD), \
        float(len(threeD))/m*100, float(sum(threeD))/len(threeD))
    
if len(sbrt) > 0:
    print 'Mean SBRT MU for {} ({:.1f}%) plans: {:.0f}'.format(len(sbrt), \
        float(len(sbrt))/m*100, float(sum(sbrt))/len(sbrt))

if len(srs) > 0:
    print 'Mean SRS MU for {} ({:.1f}%) plans: {:.0f}'.format(len(srs), \
        float(len(srs))/m*100, float(sum(srs))/len(srs))

if len(vmat) > 0:
    print 'Mean VMAT MU for {} ({:.1f}%) plans: {:.0f}'.format(len(vmat), \
        float(len(vmat))/m*100, float(sum(vmat))/len(vmat))
    
energies = set(beamEnergy)
for energy in energies:
    mu = [beamMU[i] for i,x in enumerate(beamEnergy) if x == energy]
    print '{} MV Utilization: {:.1f}%'.format(energy, float(sum(mu))/sum(beamMU)*100)