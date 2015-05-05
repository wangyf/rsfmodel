import numpy as np
import matplotlib.pyplot as plt
from scipy import integrate
from math import exp,log
from collections import namedtuple

class RateState(object):
    def __init__(self):
        # Rate and state model parameters
        self.mu0 = 0
        self.a = 0
        self.b = 0
        self.dc = 0
        self.k = 0
        self.v = 0
        self.vlp = 0
        self.vref = 1.
        self.model_time = [] # List of times we want answers at
        # Results of running the model
        self.results = namedtuple("results",["time","displacement","slider_velocity","friction","state1"])
        # Integrator settings
        self.abserr = 1.0e-12
        self.relerr = 1.0e-12
        self.loadpoint_velocity = []

    def _integrationStep(self, w, t, p):
        """
        Do the calculation for a time-step
        """
        mu, theta, self.v = w
        mu0, vlpa, a, b, dc, k = p

        # Not sure that this is the best way to handle this, but it's a start
        try:
            # Need to improve this for genalized (not 100 Hz) cases
            vlp = vlpa[int(t*100)]
        except:
            vlp = vlpa[-1]

        self.v = self.vref * exp((mu - mu0 - b * log(self.vref * theta / dc)) / a)

        dmu_dt = k * (vlp - self.v)
        dtheta_dt = 1. - self.v * theta / dc

        return [dmu_dt,dtheta_dt]

    def solve(self):
        """
        Runs the integrator to actually solve the model and returns a
        named tuple of results.
        """
        # Parameters for the model
        p = [self.mu0,self.loadpoint_velocity,self.a,self.b,self.dc,self.k]

        # Initial conditions at t = 0
        # mu = reference friction value, theta = dc/v, velocity = v
        w0 = [self.mu0,self.dc/self.v,self.v]

        # Solve it
        wsol = integrate.odeint(self._integrationStep, w0, self.model_time, args=(p,),
                                atol=self.abserr, rtol=self.relerr)

        self.results.friction = wsol[:,0]
        self.results.state1 = wsol[:,1]
        self.results.slider_velocity = self.vref * np.exp((self.results.friction - self.mu0 - self.b * np.log(self.vref * self.results.state1 / self.dc)) / self.a)

        return self.results
