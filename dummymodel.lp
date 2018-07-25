\ Model StochLP
\ LP format - for model browsing. Use MPS format to capture full model detail.
Minimize
  26.6664 Dallas,_Texas_carrier1_0000-0000SubLoc_00000
   + 26.66664 Dallas,_Texas_carrier1_0000-0001SubLoc_00000
   + 26.6664 Dallas,_Texas_carrier1_0000-0002SubLoc_00000
   + 29.9997 Dallas,_Texas_carrier2_0000-0000SubLoc_00000
   + 29.99997 Dallas,_Texas_carrier2_0000-0001SubLoc_00000
   + 29.9997 Dallas,_Texas_carrier2_0000-0002SubLoc_00000
   + 6.6666 San_Francisco,_California_carrier4_0000-0000SubLoc_00000
   + 6.66666 San_Francisco,_California_carrier4_0000-0001SubLoc_00000
   + 9.9999 San_Francisco,_California_carrier4_0000-0002SubLoc_00000
   + 9.9999 San_Francisco,_California_carrier5_0000-0000SubLoc_00000
   + 9.99999 San_Francisco,_California_carrier5_0000-0001SubLoc_00000
   + 13.3332 San_Francisco,_California_carrier5_0000-0002SubLoc_00000
   + 13.3332 San_Francisco,_California_carrier6_0000-0000SubLoc_00000
   + 13.33332 San_Francisco,_California_carrier6_0000-0001SubLoc_00000
   + 16.6665 San_Francisco,_California_carrier6_0000-0002SubLoc_00000
   + 2.99997 Philadelphia,_Pennsylvania_carrier3_0000-0000SubLoc_00000
   + 2.999997 Philadelphia,_Pennsylvania_carrier3_0000-0001SubLoc_00000
   + 2.99997 Philadelphia,_Pennsylvania_carrier3_0000-0002SubLoc_00000
   + 3333.3 dummy_dummycarrier_0000-0000SubLoc_00000
   + 3333.33 dummy_dummycarrier_0000-0001SubLoc_00000
   + 3333.3 dummy_dummycarrier_0000-0002SubLoc_00000
Subject To
 DEMAND<0000-0000SubLoc_00000>:
   - Dallas,_Texas_carrier1_0000-0000SubLoc_00000
   - Dallas,_Texas_carrier2_0000-0000SubLoc_00000
   - San_Francisco,_California_carrier4_0000-0000SubLoc_00000
   - San_Francisco,_California_carrier5_0000-0000SubLoc_00000
   - San_Francisco,_California_carrier6_0000-0000SubLoc_00000
   - Philadelphia,_Pennsylvania_carrier3_0000-0000SubLoc_00000
   - dummy_dummycarrier_0000-0000SubLoc_00000 = -940
 DEMAND<0000-0001SubLoc_00000>:
   - Dallas,_Texas_carrier1_0000-0001SubLoc_00000
   - Dallas,_Texas_carrier2_0000-0001SubLoc_00000
   - San_Francisco,_California_carrier4_0000-0001SubLoc_00000
   - San_Francisco,_California_carrier5_0000-0001SubLoc_00000
   - San_Francisco,_California_carrier6_0000-0001SubLoc_00000
   - Philadelphia,_Pennsylvania_carrier3_0000-0001SubLoc_00000
   - dummy_dummycarrier_0000-0001SubLoc_00000 = -80
 DEMAND<0000-0002SubLoc_00000>:
   - Dallas,_Texas_carrier1_0000-0002SubLoc_00000
   - Dallas,_Texas_carrier2_0000-0002SubLoc_00000
   - San_Francisco,_California_carrier4_0000-0002SubLoc_00000
   - San_Francisco,_California_carrier5_0000-0002SubLoc_00000
   - San_Francisco,_California_carrier6_0000-0002SubLoc_00000
   - Philadelphia,_Pennsylvania_carrier3_0000-0002SubLoc_00000
   - dummy_dummycarrier_0000-0002SubLoc_00000 = -50
 FLOW<dummy_dummycarrier>: dummy_dummycarrier
   - dummy_dummycarrier_0000-0000SubLoc_00000
   - dummy_dummycarrier_0000-0001SubLoc_00000
   - dummy_dummycarrier_0000-0002SubLoc_00000 = 0
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
 DEPOT<dummy_dummycarrier>: - dummy_dummycarrier_0000-0000SubLoc_00000
   >= -1e+06
 DEPOT<Dallas,_Texas_carrier2>:
   - Dallas,_Texas_carrier1_0000-0000SubLoc_00000
   - Dallas,_Texas_carrier2_0000-0000SubLoc_00000 >= -700
 DEPOT<San_Francisco,_California_carrier6>:
   - San_Francisco,_California_carrier4_0000-0000SubLoc_00000
   - San_Francisco,_California_carrier5_0000-0000SubLoc_00000
   - San_Francisco,_California_carrier6_0000-0000SubLoc_00000 >= -200
 DEPOT<Philadelphia,_Pennsylvania_carrier3>:
   - Philadelphia,_Pennsylvania_carrier3_0000-0000SubLoc_00000 >= -30
 DEPOT<dummy_dummycarrier>: - dummy_dummycarrier_0000-0001SubLoc_00000
   >= -1e+06
 DEPOT<Dallas,_Texas_carrier2>:
   - Dallas,_Texas_carrier1_0000-0001SubLoc_00000
   - Dallas,_Texas_carrier2_0000-0001SubLoc_00000 >= -700
 DEPOT<San_Francisco,_California_carrier6>:
   - San_Francisco,_California_carrier4_0000-0001SubLoc_00000
   - San_Francisco,_California_carrier5_0000-0001SubLoc_00000
   - San_Francisco,_California_carrier6_0000-0001SubLoc_00000 >= -200
 DEPOT<Philadelphia,_Pennsylvania_carrier3>:
   - Philadelphia,_Pennsylvania_carrier3_0000-0001SubLoc_00000 >= -30
 DEPOT<dummy_dummycarrier>: - dummy_dummycarrier_0000-0002SubLoc_00000
   >= -1e+06
 DEPOT<Dallas,_Texas_carrier2>:
   - Dallas,_Texas_carrier1_0000-0002SubLoc_00000
   - Dallas,_Texas_carrier2_0000-0002SubLoc_00000 >= -700
 DEPOT<San_Francisco,_California_carrier6>:
   - San_Francisco,_California_carrier4_0000-0002SubLoc_00000
   - San_Francisco,_California_carrier5_0000-0002SubLoc_00000
   - San_Francisco,_California_carrier6_0000-0002SubLoc_00000 >= -200
 DEPOT<Philadelphia,_Pennsylvania_carrier3>:
   - Philadelphia,_Pennsylvania_carrier3_0000-0002SubLoc_00000 >= -30
Bounds
 Dallas,_Texas_carrier1 <= 10000
 Dallas,_Texas_carrier2 <= 2000
 San_Francisco,_California_carrier4 <= 40000
 San_Francisco,_California_carrier5 <= 50000
 San_Francisco,_California_carrier6 <= 60000
 Philadelphia,_Pennsylvania_carrier3 <= 100
End
