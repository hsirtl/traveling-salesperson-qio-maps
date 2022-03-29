import json
import logging
import os
import datetime

import azure.functions as func

from azure.quantum import Workspace
from azure.quantum.optimization import Problem, ProblemType
from azure.quantum.optimization import SimulatedAnnealing, ParallelTempering, Tabu, QuantumMonteCarlo

from shared_code import travelingsalesperson, mapsaccess as maps


def main(req: func.HttpRequest) -> func.HttpResponse:
    logging.info('GetRoute function called.')
    inputProblem = {}

    try:
        req_body = req.get_json()
    except ValueError:
        pass
    else:
        inputProblem = req_body.get('problem')

    logging.info(f'Input Problem: {inputProblem}')

    # Copy the settings for your workspace below
    workspace = Workspace (
        subscription_id = os.environ["SubscriptionId"],
        resource_group = os.environ["ResourceGroup"],
        name = os.environ["WorkspaceName"],
        location = os.environ["WorkspaceLocation"]
    )

    inputProblemType = inputProblem.get("type")
    inputProblemCrit = inputProblem.get("optimizeBy")
    inputProblemData = inputProblem.get("data")

    destinations = inputProblemData.get("destinations")
    extDestinations = maps.addCoordinates(destinations)
    costMatrix = maps.getCostMatrix(extDestinations, inputProblemCrit)

    terms = []

    # Create cost function based on inputBlobData problem description
    if inputProblemType == "travelingsalesperson":
        terms = travelingsalesperson.createCostFunction({ 'nodes': destinations, 'distances': costMatrix})

    problem = Problem(name=inputProblemType, problem_type=ProblemType.pubo, terms=terms)
    solver = SimulatedAnnealing(workspace, timeout=100, seed=22)
    
    resultRawData = solver.optimize(problem)

    print(f'Result Raw Data: {resultRawData}')

    receiptData = {}
    receiptData["problem_type"] = inputProblemType
    receiptData["problem_crit"] = inputProblemCrit
    receiptData["destinations"] = extDestinations
    receiptData["distances"] = costMatrix
    receiptData["no_of_terms"] = str(len(terms))

    logging.info('Uploaded problem type: %s', inputProblemType)

    resultData = []
    nodes = inputProblemData.get('destinations')
    distances = receiptData.get('distances')

    # depending on the problem type extract business solution from job result
    resultData = travelingsalesperson.extractSolution({ 'nodes': nodes, 'distances': distances }, resultRawData)

    solutionData = {}
    #solutionData["receipt"] = receiptData
    solutionData["result"] = resultData

    return func.HttpResponse(json.dumps(solutionData), status_code=200)
