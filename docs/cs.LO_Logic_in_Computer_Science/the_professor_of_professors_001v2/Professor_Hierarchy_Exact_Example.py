"""Exact finite Bayesian grading example for The Professor of Professors 001.
No ATP, LLM, sampling, or third-party dependencies are used.
"""
from fractions import Fraction as F
from math import comb
import csv
from pathlib import Path

def calculate(n):
    risk = F(0)
    error = F(0)
    mass = F(0)
    for k in range(n+1):
        a = F(comb(n,k)*3**k,4**n)
        b = F(comb(n,k)*3**(n-k),4**n)
        mass += (a+b)/2
        risk += a*b/(2*(a+b))
        error += min(a,b)/2
    assert mass == 1
    return risk, error

def main():
    prev = F(1,4)
    for n in range(1,25):
        risk, error = calculate(n)
        assert 0 < risk <= prev
        assert risk <= error
        prev = risk
    assert calculate(1) == (F(3,16), F(1,4))
    path = Path(__file__).with_name('Professor_Hierarchy_Exact_Example.csv')
    with path.open('w',newline='') as f:
        w = csv.writer(f)
        w.writerow(['level','fresh_binary_risk_exact','fresh_grade_risk_exact','copied_grade_risk_exact','bayes_class_error_exact','fresh_binary_risk_decimal'])
        for n in [1,2,4,8,12,16,24]:
            risk, error = calculate(n)
            w.writerow([n,str(risk),str(risk/16),str(F(3,256)),str(error),f'{float(risk):.9f}'])
    print('Exact risk and probability-mass checks passed for levels 1 through 24.')

if __name__ == '__main__':
    main()
