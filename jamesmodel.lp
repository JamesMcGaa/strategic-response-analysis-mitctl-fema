\ Model StochLP
\ LP format - for model browsing. Use MPS format to capture full model detail.
Minimize
  40 Dallas,_Texas_carrier1_0000-0000SubLoc_00000
   + 24 Dallas,_Texas_carrier1_0000-0001SubLoc_00000
   + 16 Dallas,_Texas_carrier1_0000-0002SubLoc_00000
   + 45 Dallas,_Texas_carrier2_0000-0000SubLoc_00000
   + 27 Dallas,_Texas_carrier2_0000-0001SubLoc_00000
   + 18 Dallas,_Texas_carrier2_0000-0002SubLoc_00000
   + 10 San_Francisco,_California_carrier4_0000-0000SubLoc_00000
   + 6 San_Francisco,_California_carrier4_0000-0001SubLoc_00000
   + 6 San_Francisco,_California_carrier4_0000-0002SubLoc_00000
   + 15 San_Francisco,_California_carrier5_0000-0000SubLoc_00000
   + 9 San_Francisco,_California_carrier5_0000-0001SubLoc_00000
   + 8 San_Francisco,_California_carrier5_0000-0002SubLoc_00000
   + 20 San_Francisco,_California_carrier6_0000-0000SubLoc_00000
   + 12 San_Francisco,_California_carrier6_0000-0001SubLoc_00000
   + 10 San_Francisco,_California_carrier6_0000-0002SubLoc_00000
   + 4.5 Philadelphia,_Pennsylvania_carrier3_0000-0000SubLoc_00000
   + 2.7 Philadelphia,_Pennsylvania_carrier3_0000-0001SubLoc_00000
   + 1.8 Philadelphia,_Pennsylvania_carrier3_0000-0002SubLoc_00000
Subject To
 CARRIERCAPACITY<Dallas,_Texas_carrier1>: - Dallas,_Texas_carrier1
   >= -10000
 CARRIERCAPACITY<Dallas,_Texas_carrier2>: - Dallas,_Texas_carrier2
   >= -2000
 CARRIERCAPACITY<San_Francisco,_California_carrier4>:
   - San_Francisco,_California_carrier4 >= -40000
 CARRIERCAPACITY<San_Francisco,_California_carrier5>:
   - San_Francisco,_California_carrier5 >= -50000
 CARRIERCAPACITY<San_Francisco,_California_carrier6>:
   - San_Francisco,_California_carrier6 >= -60000
 CARRIERCAPACITY<Philadelphia,_Pennsylvania_carrier3>:
   - Philadelphia,_Pennsylvania_carrier3 >= -100
 DEMAND<0000-0000SubLoc_00000>:
   - Dallas,_Texas_carrier1_0000-0000SubLoc_00000
   - Dallas,_Texas_carrier2_0000-0000SubLoc_00000
   - San_Francisco,_California_carrier4_0000-0000SubLoc_00000
   - San_Francisco,_California_carrier5_0000-0000SubLoc_00000
   - San_Francisco,_California_carrier6_0000-0000SubLoc_00000
   - Philadelphia,_Pennsylvania_carrier3_0000-0000SubLoc_00000 = -801
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
