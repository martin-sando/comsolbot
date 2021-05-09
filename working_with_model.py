import os
import mph

def change_params(model, params):
    for key in params.keys():
        model.parameter(key, params[key])
    model.save()


def run_model(model):
    model.solve()
    lambdas = [float(s.split('=')[1]) for s in model.solutions() if s.startswith('lambda=')]
    res = list([a[0] for a in model.java.result().numerical('gev1').computeResult()[0]])
    return lambdas, res

