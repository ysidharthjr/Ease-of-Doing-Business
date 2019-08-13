# -*- coding: utf-8 -*-
"""
Created on Sun Aug 11 22:22:30 2019

@author: lenovo
"""

for _ in range(int(input())):
    n=int(input())
    c=list(map(int,input().split()))
    h=list(map(int,input().split()))
    ar=[0]*n
    for i in range(n):
        a=i-c[i]
        if a<0:
            a=0
        b=i+c[i]+1
        if b>n:
            b=n
        for j in range(a,b):
            ar[j]+=1

    sr=sorted(ar)
    h=sorted(h)
    if sr==h:
        print("YES")
    else:
        print("NO")