\ Model StochLP
\ LP format - for model browsing. Use MPS format to capture full model detail.
Minimize
  35 Dallas,_Texas_carrier1_0000-0000SubLoc_00000
   + 69.3 Dallas,_Texas_carrier1_0000-0001SubLoc_00000
   + 7 Dallas,_Texas_carrier1_0000-0002SubLoc_00000
   + 35 Dallas,_Texas_carrier2_0000-0000SubLoc_00000
   + 69.3 Dallas,_Texas_carrier2_0000-0001SubLoc_00000
   + 7 Dallas,_Texas_carrier2_0000-0002SubLoc_00000
   + 5 San_Francisco,_California_carrier4_0000-0000SubLoc_00000
   + 9.9 San_Francisco,_California_carrier4_0000-0001SubLoc_00000
   + 2 San_Francisco,_California_carrier4_0000-0002SubLoc_00000
   + 5 San_Francisco,_California_carrier5_0000-0000SubLoc_00000
   + 9.9 San_Francisco,_California_carrier5_0000-0001SubLoc_00000
   + 2 San_Francisco,_California_carrier5_0000-0002SubLoc_00000
   + 5 San_Francisco,_California_carrier6_0000-0000SubLoc_00000
   + 9.9 San_Francisco,_California_carrier6_0000-0001SubLoc_00000
   + 2 San_Francisco,_California_carrier6_0000-0002SubLoc_00000
   + 0.5 Philadelphia,_Pennsylvania_carrier3_0000-0000SubLoc_00000
   + 0.99 Philadelphia,_Pennsylvania_carrier3_0000-0001SubLoc_00000
   + 0.1 Philadelphia,_Pennsylvania_carrier3_0000-0002SubLoc_00000
Subject To
 CARRIERCAPACITY<Dallas,_Texas_carrier1>: - Dallas,_Texas_carrier1
   >= -100000
 CARRIERCAPACITY<Dallas,_Texas_carrier2>: - Dallas,_Texas_carrier2
   >= -200000
 CARRIERCAPACITY<San_Francisco,_California_carrier4>:
   - San_Francisco,_California_carrier4 >= -400000
 CARRIERCAPACITY<San_Francisco,_California_carrier5>:
   - San_Francisco,_California_carrier5 >= -500000
 CARRIERCAPACITY<San_Francisco,_California_carrier6>:
   - San_Francisco,_California_carrier6 >= -6e+07
 CARRIERCAPACITY<Philadelphia,_Pennsylvania_carrier3>:
   - Philadelphia,_Pennsylvania_carrier3 >= -15
 DEMAND<0000-0000SubLoc_00000>:
   - Dallas,_Texas_carrier1_0000-0000SubLoc_00000
   - Dallas,_Texas_carrier2_0000-0000SubLoc_00000
   - San_Francisco,_California_carrier4_0000-0000SubLoc_00000
   - San_Francisco,_California_carrier5_0000-0000SubLoc_00000
   - San_Francisco,_California_carrier6_0000-0000SubLoc_00000
   - Philadelphia,_Pennsylvania_carrier3_0000-0000SubLoc_00000 = -100
 DEMAND<0000-0001SubLoc_00000>:
   - Dallas,_Texas_carrier1_0000-0001SubLoc_00000
   - Dallas,_Texas_carrier2_0000-0001SubLoc_00000
   - San_Francisco,_California_carrier4_0000-0001SubLoc_00000
   - San_Francisco,_California_carrier5_0000-0001SubLoc_00000
   - San_Francisco,_California_carrier6_0000-0001SubLoc_00000
   - Philadelphia,_Pennsylvania_carrier3_0000-0001SubLoc_00000 = -80
 DEMAND<0000-0002SubLoc_00000>:
   - Dallas,_Texas_carrier1_0000-0002SubLoc_00000
   - Dallas,_Texas_carrier2_0000-0002SubLoc_00000
   - San_Francisco,_California_carrier4_0000-0002SubLoc_00000
   - San_Francisco,_California_carrier5_0000-0002SubLoc_00000
   - San_Francisco,_California_carrier6_0000-0002SubLoc_00000
   - Philadelphia,_Pennsylvania_carrier3_0000-0002SubLoc_00000 = -50
 FLOW<Dallas,_Texas_carrier1>: Dallas,_Texas_carrier1
   - Dallas,_Texas_carrier1_0000-0000SubLoc_00000
   - Dallas,_Texas_carrier1_0000-0001SubLoc_00000
   - Dallas,_Texas_carrier1_0000-0002SubLoc_00000 = 0
 FLOW<Dallas,_Texas_carrier2>: Dallas,_Texas_carrier2
   - Dallas,_Texas_carrier2_0000-0000SubLoc_00000
   - Dallas,_Texas_carrier2_0000-0001SubLoc_00000
   - Dallas,_Texas_carrier2_0000-0002SubLoc_00000 = 0
 FLOW<San_Francisco,_California_carrier4>:
   San_Francisco,_California_carrier4
   - San_Francisco,_California_carrier4_0000-0000SubLoc_00000
   - San_Francisco,_California_carrier4_0000-0001SubLoc_00000
   - San_Francisco,_California_carrier4_0000-0002SubLoc_00000 = 0
 FLOW<San_Francisco,_California_carrier5>:
   San_Francisco,_California_carrier5
   - San_Francisco,_California_carrier5_0000-0000SubLoc_00000
   - San_Francisco,_California_carrier5_0000-0001SubLoc_00000
   - San_Francisco,_California_carrier5_0000-0002SubLoc_00000 = 0
 FLOW<San_Francisco,_California_carrier6>:
   San_Francisco,_California_carrier6
   - San_Francisco,_California_carrier6_0000-0000SubLoc_00000
   - San_Francisco,_California_carrier6_0000-0001SubLoc_00000
   - San_Francisco,_California_carrier6_0000-0002SubLoc_00000 = 0
 FLOW<Philadelphia,_Pennsylvania_carrier3>:
   Philadelphia,_Pennsylvania_carrier3
   - Philadelphia,_Pennsylvania_carrier3_0000-0000SubLoc_00000
   - Philadelphia,_Pennsylvania_carrier3_0000-0001SubLoc_00000
   - Philadelphia,_Pennsylvania_carrier3_0000-0002SubLoc_00000 = 0
 DEPOT<Dallas,_Texas>: - Dallas,_Texas_carrier1 - Dallas,_Texas_carrier2
   >= -700
 DEPOT<San_Francisco,_California>: - San_Francisco,_California_carrier4
   - San_Francisco,_California_carrier5
   - San_Francisco,_California_carrier6 >= -200
 DEPOT<Philadelphia,_Pennsylvania>: - Philadelphia,_Pennsylvania_carrier3
   >= -30
Bounds
End
