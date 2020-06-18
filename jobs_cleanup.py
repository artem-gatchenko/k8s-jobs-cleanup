#!/usr/bin/env python3

import logging
import yaml
import sys
import os
import time
from datetime import datetime
from kubernetes import client, config, utils
import kubernetes.client
from kubernetes.client.rest import ApiException


cleanupTimeout = os.environ.get('CLEANUP_TIMEOUT', '60')
kubeNamespace = os.environ.get('KUBERNETES_NAMESPACE', 'default')
dateFormat = "%Y-%m-%d %H:%M:%S"

# Set logging
logging.basicConfig(stream=sys.stdout, level=logging.INFO)

# Setup K8 configs
config.load_incluster_config()
configuration = kubernetes.client.Configuration()
api_instance = kubernetes.client.BatchV1Api(kubernetes.client.ApiClient(configuration))


def kube_cleanup_finished_jobs(namespace=kubeNamespace, state='Finished'):
    deleteoptions = client.V1DeleteOptions(propagation_policy='Background')
    try: 
        jobs = api_instance.list_namespaced_job(namespace,
                                                pretty=True,
                                                timeout_seconds=0)
    except ApiException as e:
        print("Exception when calling BatchV1Api->list_namespaced_job: %s\n" % e)
    
    for job in jobs.items:
        logging.debug(job)
        jobname = job.metadata.name
        jobstatus = job.status.conditions
        completionTime = job.status.completion_time
        if job.status.succeeded == 1:
            currentTime = datetime.utcnow().strftime(dateFormat)
            currentTime = datetime.strptime(currentTime, dateFormat)

            completionTime = completionTime.strftime(dateFormat)
            completionTime = datetime.strptime(completionTime, dateFormat)

            diffTime = (currentTime - completionTime).total_seconds()

            if int(diffTime) >= int(cleanupTimeout):
                logging.info("Cleaning up Job: {}. Finished at: {}".format(jobname, job.status.completion_time))
                try: 
                    api_response = api_instance.delete_namespaced_job(jobname,
                                                                      namespace,
                                                                      body = deleteoptions,
                                                                      grace_period_seconds = 0)
                    logging.debug(api_response)
                except ApiException as e:
                    print("Exception when calling BatchV1Api->delete_namespaced_job: %s\n" % e)

        else:
            if jobstatus is None and job.status.active == 1:
                jobstatus = 'active'
            logging.info("Job: {} not cleaned up. Current status: {}".format(jobname, jobstatus))

    return 0
    

if __name__ == '__main__':
    kube_cleanup_finished_jobs()
    sys.exit(0)
