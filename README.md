# Hard-Disk Prediction

Predictive API for Hard Disk failure prediction.
Loads the ML Model and gives the prediction on the basis of API request.

## Requirement

tqdm                                                  

NumPy

TensorFlow                                        

Keras

spektral                                              

scikit-learn

seaborn                                              

pymongo

fastapi                                                 

pydantic                                        

joblib                                                   

json

bson                                                    

bash

Docker                                                

Docker-compose

## Dataset

The Dataset will contain S.M.A.R.T data. SMART/S.M.A.R.T stands for Self-Monitoring, Analysis and Reporting Technology. It is basically a system that collects information about a hard disk drive (HDD) and solid state drive (SDD), and allows you to run some tests on the drive to determine its approximate health.

## Usage

Run bash_send.sh on the device that is connected with the HDD or SDD.

Provide executable permission to the bash file using 
chmod +x bash_send.sh

and run the script as a root user using 

./bash_send.sh &
provide disk partition name in the format /dev/sdx where x stands for any letter.

Run api_fetch.py in the server where MongoDB instance was running on.
