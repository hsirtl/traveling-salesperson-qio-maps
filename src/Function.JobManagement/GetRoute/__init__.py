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

    # check if lat/lon information is already included
    if len(destinations[0]) > 1:
        extDestinations = destinations
    else :
        extDestinations = maps.addCoordinates(destinations)
        
    costMatrix = maps.getCostMatrix(extDestinations, inputProblemCrit)

    # Create cost function based on inputBlobData problem description
    terms = travelingsalesperson.createCostFunction({ 'nodes': destinations, 'distances': costMatrix})

    # configure the problem and submit it to an optimization solver
    problem = Problem(name=inputProblemType, problem_type=ProblemType.pubo, terms=terms)
    solver = SimulatedAnnealing(workspace, timeout=100, seed=22)
    resultRawData = solver.optimize(problem)

    nodes = inputProblemData.get('destinations')

    # depending on the problem type extract business solution from job result
    resultData = travelingsalesperson.extractSolution({ 'nodes': nodes, 'distances': costMatrix }, resultRawData)

    solutionData = {}
    solutionData["result"] = resultData

    return func.HttpResponse(json.dumps(solutionData), status_code=200)
