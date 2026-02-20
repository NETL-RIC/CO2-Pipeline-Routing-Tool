#!/usr/bin/env python3

'''
Docstring for tests.endpoint_tester

The purpose of this file is to test the endpoints of the API. It will test the following endpoints:
Our main goal is to evaluate the 

Following endpoints:
token
download_report

First:
gen_uid
get_uid 
must be called to setup a session 
then /token can be called 

token despite its name actually begins the ML process and can hang for some time
this time will be one of our metrics need to be measured, tracked, and graphed. 

download_report can be called after token to get the results of the ML process. 
This will need to be validated to ensure that it has the necessary data.
    Down the line we might be able to directly validate the results of download_report against the known data of the CSS sites.


Multiple threads will be possible to test multiple sessions at once, and to test the performance of the API under load.
Each thread will need to have its own session, and will need to track its own metrics.
Those metrics will be collected and graphed as coseries on the same graph



'''


#Taken from IdModes.js 

#List of the CCS site beginning locations
start_locations = [
{ 'id': [39.87, -88.89], 'name': 'Illinois Industrial Carbon Capture and Storage Project'},
{ 'id': [45, -85], 'name': 'MRCSP Development Phase - Michigan Basin Project' },
{ 'id': [35, -98], 'name': 'PurdySho-Vel-Tum EOR Project'},
{ 'id': [30, -101], 'name': 'Val Verde NG Plants'},
{ 'id': [39.863, -88.913], 'name': 'Illinois Industrial Carbon Capture and Storage'},
{ 'id': [37.106767, -100.7977], 'name': 'Arkalon'},
{ 'id': [37.959112, -100.83676], 'name': 'Bonanza BioEnergy'},
{ 'id': [37.047329, -95.604094], 'name': 'Coffeyville Plant'},
{ 'id': [45.113, -84.652], 'name': 'Core Energy CO2-EOR'},
{ 'id': [46.8839, -102.3157], 'name': 'Red Trail'},
{ 'id': [36.378636, -97.762739], 'name': 'Enid Fertilizer'},
{ 'id': [29.866, -93.967], 'name': 'Air Products Port Arthur Facility'},
{ 'id': [30.3718, -101.8449], 'name': 'Terrell Gas Processing'},
{ 'id': [31.009, -88.025], 'name': 'SECARB Development Phase - Citronelle Project'},
{ 'id': [37.536, -105.104], 'name': 'Oakdale NG Processing'},
{ 'id': [40.530, -89.682], 'name': 'NRG Powerton Station'},
{ 'id': [38.272, -89.668], 'name': 'Prairie State Energy Campus'},
{ 'id': [37.046, -95.604], 'name': 'CO2 Capture from Coffeyville Fertilizer Plant'},
{ 'id': [37.7903, -84.7144], 'name': 'EW Brown Generating Station'},
{ 'id': [39.594529, -78.745292], 'name': 'AES Warrior Run'},
{ 'id': [42.0916, -71.48352], 'name': 'Bellingham Cogeneration Facility'},
{ 'id': [47.3727, -101.15679], 'name': 'Great River Energy'},
{ 'id': [40.90214, -82.03784], 'name': 'Touchstone Bioconversion Pilot Plant'},
{ 'id': [36.37858, -97.76379], 'name': 'Purdy Sho-Vel-Tum EOR Project'},
{ 'id': [29.86493, -93.966697], 'name': 'Air Products and Chemicals Inc. CCS Project'},
{ 'id': [31, -103], 'name': 'Century Plant Gas Processing'},
{ 'id': [33.216456, -97.772382], 'name': 'Mitchell Energy Bridgeport Plant'},
{ 'id': [29.47678, -95.637769], 'name': 'W.A. Parish Post-Combustion CO2 Capture and Sequestration Project'},
{ 'id': [39.501027, -112.581819], 'name': 'Intermountain Power Agency'},
{ 'id': [42.535541, -87.903483], 'name': 'We Energies Pleasant Prairie Field Pilot'},
{ 'id': [35.760591, -117.379211], 'name': 'Searles Valley Minerals'},
{ 'id': [41.88568, -110.0926], 'name': 'Shute Creek Plant'},
{ 'id': [30.692226, -88.042569], 'name': 'Fuel Cell Carbon Capture Pilot Plant'},
{ 'id': [31.01124, -88.024597], 'name': 'Linde/BASF FEED'},
{ 'id': [33.2343, -86.4836], 'name': 'National Carbon Capture Center (NCCC)'},
{ 'id': [33.417905, -111.928358], 'name': 'Center for Negative Carbon Emissions'},
{ 'id': [35.27444, -119.32301], 'name': 'Elk Hills CCS'},
{ 'id': [37.510632, -121.997288], 'name': 'Membrane Technology & Research, Inc.'},
{ 'id': [37.458009, -122.175774], 'name': 'SRI International Post-combustion Sorbent'},
{ 'id': [39.79121, -105.137092], 'name': 'TDA Research Post-combustion'},
{ 'id': [39.791215, -105.136744], 'name': 'TDA Research Pre-combustion'},
{ 'id': [31.006474, -88.008697], 'name': 'Gas Technology Institute'},
{ 'id': [40.116306, -88.243522], 'name': 'Linde/Illinois'},
{ 'id': [38.24935, -89.75296], 'name': 'Prairie State Generating Station CCS'},
{ 'id': [37.106778, -100.799611], 'name': 'Arkalon Bioethanol'},
{ 'id': [37.958806, -100.836556], 'name': 'Bonanza Bioethanol'},
{ 'id': [37.050663, -95.604763], 'name': 'Coffeyville Fertilizer'},
{ 'id': [38.03501, -84.504821], 'name': 'University of Kentucky Center for Applied Energy Research'},
{ 'id': [38.03501, -84.504821], 'name': 'University of Kentucky Research Foundation'},
{ 'id': [30.218533, -91.052119], 'name': 'PCS Nitrogen'},
{ 'id': [39.594529, -78.745292], 'name': 'Warrior Run'},
{ 'id': [45.1, -84.65], 'name': 'Core Energy'},
{ 'id': [41.0809508, -101.1433768], 'name': 'Gerald Gentleman Coal Power Plant'},
{ 'id': [40.764619, -73.971056], 'name': 'Global Thermostat'},
{ 'id': [40.71217, -74.007155], 'name': 'Infinitree'},
{ 'id': [35.905909, -78.863898], 'name': 'Research Triangle Institute'},
{ 'id': [47.11495, -101.1725], 'name': 'Project Tundra'},
{ 'id': [47.9198, -97.0605], 'name': 'University of North Dakota Energy and Environmental Research Center'},
{ 'id': [35.194006, -94.646982], 'name': 'Shady Point'},
{ 'id': [29.865806, -93.967361], 'name': 'Air Products Steam Methane Reformer'},
{ 'id': [30.608764, -102.57876], 'name': 'Century Plant'},
{ 'id': [29.646611, -95.055917], 'name': 'NET Power'},
{ 'id': [33.63559, -96.60902], 'name': 'Panda Energy Fund'},
{ 'id': [29.477964, -95.635209], 'name': 'Petra Nova'},
{ 'id': [29.477964, -95.635209], 'name': 'Petra Nova'},
{ 'id': [32.972554, -102.74361], 'name': 'University of Texas'},
{ 'id': [44.388212, -105.459617], 'name': 'Dry Fork Power Plant CCS'},
{ 'id': [43.280518, -107.6022], 'name': 'Lost Cabin'},
{ 'id': [44.388212, -105.45961], 'name': 'Wyoming Integrated Test Center'},
{ 'id': [47.361953, -101.838103], 'name': 'Great Plains Synfuel Plant'},
]


#List of possible CCS ending locations
ending_locations = [
{ 'id': [39.87, -88.89], 'name': 'Illinois Industrial Carbon Capture and Storage Project'},
{ 'id': [43, -106], 'name': 'LINC Energy - Wyoming EOR'},
{ 'id': [45, -85], 'name': 'MRCSP Development Phase - Michigan Basin Project' },
{ 'id': [35, -98], 'name': 'PurdySho-Vel-Tum EOR Project'},
{ 'id': [40, -109], 'name': 'Rangely-Webber EOR'},
{ 'id': [42, -109], 'name': 'Salt CreekMonellSussex Unit EOR'},
{ 'id': [36, -101], 'name': 'SWP Development Phase - Farnsworth Unit Ochiltree Project'},
{ 'id': [30, -101], 'name': 'Val Verde NG Plants'},
{ 'id': [31, -102], 'name': 'Yates Oil Field EOR Operations'},
]

#These targets locations will be used to test the API endpoints in a combinatorial fashion.
#make sure you check to not use the same location for both start and end in the same test case
#longest pair according to https://www.quora.com/What-are-the-two-furthest-driving-points-in-the-contiguous-USA
#Start point: 24.594237 N, 81.797872 W (Fleming Key, Florida)
#End point: 48.367418 N, 124.692498 W (Neah Bay, Washington)

longest_pair = [
    {'id':[24.594237, -81.797872],'name':'fleming_key'},
    {'id': [48.367418, -124.692498],'name':'neah_bay'}
]

import matplotlib.pyplot as plt
import numpy as np
import requests
import time
import uuid
import threading
import zipfile
import io
import os
import tqdm
import random
import pandas as pd
import logging

class TestSession:
    def __init__(self, api_url,test_cases):
        self.api_url = api_url
        self.session = requests.Session()
        self.times= []
        self.pass_fail = []
        self.test_cases = test_cases
    
    def get_times(self):
        return self.times   

    def get_pass_fail(self):
        return self.pass_fail
    
    def get_test_cases(self):
        return self.test_cases

    #retry gen id and get id until they succeed, as they are necessary to setup a session and they usually dont fail for the same reason as token, which is that the ML process is still running and the session is not ready yet.

    def _request_gen_uid(self):
        response = self.session.get(f"{self.api_url}/gen_uid")
        if response.status_code == 204:
            return 
        else:
            while response.status_code != 204:
                tqdm.tqdm.write(f"Failed to generate UID, retrying...")
                time.sleep(60)  # Wait before retrying
                response = self.session.get(f"{self.api_url}/gen_uid")
                
            return

    def _request_get_uid(self):
        response = self.session.get(f"{self.api_url}/get_uid")
        if response.status_code == 200:
            return response.json().get("uid")
        else:
            while response.status_code != 200:
                tqdm.tqdm.write(f"Failed to get UID, retrying...")
                time.sleep(60)  # Wait before retrying
                response = self.session.get(f"{self.api_url}/get_uid")
            
            return response.json().get("uid")


    #this is the long running ML process we are interested in testing, we want to track the time and validate it works first time.

    def _request_token(self, start_location, end_location,mode = 'route'):
        payload = {
            's':start_location,
            'e':end_location,
            'mode':mode
        }

        response = self.session.post(f"{self.api_url}/token", json=payload)

        if response.status_code == 200:
            return (True,response)
        else:
            return (False,response)


    #currently unused 
    def _request_download_report(self):
        payload = {'extension':'.zip'}
        response = self.session.post(f"{self.api_url}/download_report", json=payload)
        if response.status_code != 200:
            raise Exception(f"Failed to download report: {response.status_code} - {response.text}")
        else:
            with zipfile.ZipFile(io.BytesIO(response.content)) as z:
                return len(z.namelist()) == 6
            

    def _test_worker(self,start_location, end_location,mode = 'route'):
        self._request_gen_uid()        
        self.uid = self._request_get_uid()

        start_time = time.time()
        result = self._request_token(start_location, end_location, mode)
        token_time = time.time() - start_time

   

        datum = {
            'start_location': start_location,
            'end_location': end_location,
            'mode': mode,
            'token_time': token_time,
            'token_success': result[0],
            #'report_valid': report_valid
        }
        
        if not result[0]:
            logging.info(f"Test failed for {start_location} to {end_location} in mode {mode}. Token request failed with response: {result[1]}")
                   
        return datum
    
    def run_tests(self,thread_num, mode = 'route'):
        for start_id, end_id in tqdm.tqdm(self.test_cases, desc=f"thread_{thread_num}_Running tests"):
            
            start_location = start_id['id']
            end_location = end_id['id'] 

            try:
               
                result = self._test_worker(start_location, end_location, mode)
                self.times.append(result['token_time'])
                self.pass_fail.append(result['token_success'])
                if not result['token_success']:
                    tqdm.tqdm.write(f"Tested {start_id['name']} to {end_id['name']} in {result['token_time']:.2f} seconds - Token Success: {result['token_success']}")              
            except Exception as e:
                logging.error(f"Error in test worker for {start_id['name']} to {end_id['name']}: {e}")
                tqdm.tqdm.write(f"Error in test worker: {e}")
                self.times.append(-1)  # Append -1 for fully failed tests


def main(args):
    
    threads = []
    test_sessions = []
    test_cases = []

    logging.basicConfig(filename=args.log_file, level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

    for begin in start_locations:
        for end in ending_locations:
            if begin['id'] != end['id']:
                test_cases.append((begin, end))

    test_cases.append((longest_pair[0], longest_pair[1]))  # Add the longest pair as a test case

    print(f"Total test cases: {len(test_cases)}")

    for j in range(args.num_threads):
        
        test_case_share = test_cases[j::args.num_threads]  # Distribute test cases among threads
        print(f"Thread {j+1} will run {len(test_case_share)} test cases.")
        test_session = TestSession(args.api_url, test_case_share)
        test_sessions.append(test_session)
        threads.append(threading.Thread(target=test_session.run_tests, args=(j,), kwargs={'mode': args.mode}))
        threads[-1].start()

    for t in threads:
        t.join()

    
    #Collect results and output to graph and csv
    # Collect all times from all test sessions
    all_times = []



    for i, session in enumerate(test_sessions):

        times = session.get_times()
        pass_fail = session.get_pass_fail()
        locations = session.get_test_cases()
        all_times.extend([(time, success, loc[0]['name'], loc[1]['name']) for time, success, loc in zip(times, pass_fail, locations)])


    # Create DataFrame for CSV output
    df = pd.DataFrame(all_times, columns=['token_time','success','from_location','to_location'])
    df.to_csv(args.output_file, index=False)

    # Create graph with each test session as its own series
    plt.figure(figsize=(12, 8))
    for i, session in enumerate(test_sessions):
        times = session.get_times()
        iterations = range(len(times))
        plt.plot(iterations, times, marker='o', label=f'Thread {i+1}')

    plt.xlabel('Iteration')
    plt.ylabel('Token Time (seconds)')
    plt.title('API Token Request Times by Thread')
    plt.legend()
    plt.grid(True, alpha=0.3)
    plt.savefig(args.graph_file, dpi=300, bbox_inches='tight')
    plt.show()

    print(f"Results saved to {args.output_file}")
    print(f"Graph saved to {args.graph_file}")

if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description='Test the API endpoints for the CO2 Pipeline Routing Tool')
    parser.add_argument('--num_threads', type=int, default=1, help='Number of threads to use for testing') 
    parser.add_argument('--output_file', type=str, default=f'{time.time()}.csv', help='File to output the results to')
    parser.add_argument('--graph_file', type=str, default=f'{time.time()}.png', help='File to output the graph to')
    parser.add_argument('--api_url', type=str, default='http://localhost:5000/researcher-apps/co2-pipeline-routing-tool/', help='URL of the API to test')
    parser.add_argument('--mode', type=str, default='route', help='Mode to test: route or other modes if available')
    parser.add_argument('--log_file', type=str, default=f'{time.time()}_endpoint_tester.log', help='File to output logs to')
    args = parser.parse_args()

    main(args)