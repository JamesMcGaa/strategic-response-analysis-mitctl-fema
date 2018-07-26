\ Model StochLPNonfixedDummy
\ LP format - for model browsing. Use MPS format to capture full model detail.
Minimize
  40 Dallas,_Texas_carrier1_0000-0000SubLoc_00000
   + 79.2 Dallas,_Texas_carrier1_0000-0001SubLoc_00000
   + 8 Dallas,_Texas_carrier1_0000-0002SubLoc_00000
   + 45 Dallas,_Texas_carrier2_0000-0000SubLoc_00000
   + 89.1 Dallas,_Texas_carrier2_0000-0001SubLoc_00000
   + 9 Dallas,_Texas_carrier2_0000-0002SubLoc_00000
   + 10 San_Francisco,_California_carrier4_0000-0000SubLoc_00000
   + 19.8 San_Francisco,_California_carrier4_0000-0001SubLoc_00000
   + 3 San_Francisco,_California_carrier4_0000-0002SubLoc_00000
   + 15 San_Francisco,_California_carrier5_0000-0000SubLoc_00000
   + 29.7 San_Francisco,_California_carrier5_0000-0001SubLoc_00000
   + 4 San_Francisco,_California_carrier5_0000-0002SubLoc_00000
   + 20 San_Francisco,_California_carrier6_0000-0000SubLoc_00000
   + 39.6 San_Francisco,_California_carrier6_0000-0001SubLoc_00000
   + 5 San_Francisco,_California_carrier6_0000-0002SubLoc_00000
   + 4.5 Philadelphia,_Pennsylvania_carrier3_0000-0000SubLoc_00000
   + 8.91 Philadelphia,_Pennsylvania_carrier3_0000-0001SubLoc_00000
   + 0.9 Philadelphia,_Pennsylvania_carrier3_0000-0002SubLoc_00000
   + 5000 dummy_dummycarrier_0000-0000SubLoc_00000
   + 9900 dummy_dummycarrier_0000-0001SubLoc_00000
   + 1000 dummy_dummycarrier_0000-0002SubLoc_00000
Subject To
 DEMAND<0000-0000SubLoc_00000>:
   - Dallas,_Texas_carrier1_0000-0000SubLoc_00000
   - Dallas,_Texas_carrier2_0000-0000SubLoc_00000
   - San_Francisco,_California_carrier4_0000-0000SubLoc_00000
   - San_Francisco,_California_carrier5_0000-0000SubLoc_00000
   - San_Francisco,_California_carrier6_0000-0000SubLoc_00000
   - Philadelphia,_Pennsylvania_carrier3_0000-0000SubLoc_00000
   - dummy_dummycarrier_0000-0000SubLoc_00000 = -100
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
 TOTALINVENTORY<>: - Dallas,_Texas_NONFIXEDCAPACITY
   - San_Francisco,_California_NONFIXEDCAPACITY
   - Philadelphia,_Pennsylvania_NONFIXEDCAPACITY = -930
 TOTALINVENTORYDummy<>: - dummy_NONFIXEDCAPACITY = -1e+06
 DEPOT<dummy_dummycarrier>: - dummy_dummycarrier_0000-0000SubLoc_00000
   + dummy_NONFIXEDCAPACITY >= 0
 DEPOT<Dallas,_Texas_carrier2>:
   - Dallas,_Texas_carrier1_0000-0000SubLoc_00000
   - Dallas,_Texas_carrier2_0000-0000SubLoc_00000
   + Dallas,_Texas_NONFIXEDCAPACITY >= 0
 DEPOT<San_Francisco,_California_carrier6>:
   - San_Francisco,_California_carrier4_0000-0000SubLoc_00000
   - San_Francisco,_California_carrier5_0000-0000SubLoc_00000
   - San_Francisco,_California_carrier6_0000-0000SubLoc_00000
   + San_Francisco,_California_NONFIXEDCAPACITY >= 0
 DEPOT<Philadelphia,_Pennsylvania_carrier3>:
   - Philadelphia,_Pennsylvania_carrier3_0000-0000SubLoc_00000
   + Philadelphia,_Pennsylvania_NONFIXEDCAPACITY >= 0
 DEPOT<dummy_dummycarrier>: - dummy_dummycarrier_0000-0001SubLoc_00000
   + dummy_NONFIXEDCAPACITY >= 0
 DEPOT<Dallas,_Texas_carrier2>:
   - Dallas,_Texas_carrier1_0000-0001SubLoc_00000
   - Dallas,_Texas_carrier2_0000-0001SubLoc_00000
   + Dallas,_Texas_NONFIXEDCAPACITY >= 0
 DEPOT<San_Francisco,_California_carrier6>:
   - San_Francisco,_California_carrier4_0000-0001SubLoc_00000
   - San_Francisco,_California_carrier5_0000-0001SubLoc_00000
   - San_Francisco,_California_carrier6_0000-0001SubLoc_00000
   + San_Francisco,_California_NONFIXEDCAPACITY >= 0
 DEPOT<Philadelphia,_Pennsylvania_carrier3>:
   - Philadelphia,_Pennsylvania_carrier3_0000-0001SubLoc_00000
   + Philadelphia,_Pennsylvania_NONFIXEDCAPACITY >= 0
 DEPOT<dummy_dummycarrier>: - dummy_dummycarrier_0000-0002SubLoc_00000
   + dummy_NONFIXEDCAPACITY >= 0
 DEPOT<Dallas,_Texas_carrier2>:
   - Dallas,_Texas_carrier1_0000-0002SubLoc_00000
   - Dallas,_Texas_carrier2_0000-0002SubLoc_00000
   + Dallas,_Texas_NONFIXEDCAPACITY >= 0
 DEPOT<San_Francisco,_California_carrier6>:
   - San_Francisco,_California_carrier4_0000-0002SubLoc_00000
   - San_Francisco,_California_carrier5_0000-0002SubLoc_00000
   - San_Francisco,_California_carrier6_0000-0002SubLoc_00000
   + San_Francisco,_California_NONFIXEDCAPACITY >= 0
 DEPOT<Philadelphia,_Pennsylvania_carrier3>:
   - Philadelphia,_Pennsylvania_carrier3_0000-0002SubLoc_00000
   + Philadelphia,_Pennsylvania_NONFIXEDCAPACITY >= 0
Bounds
 Dallas,_Texas_carrier1 <= 10000
 Dallas,_Texas_carrier2 <= 2000
 San_Francisco,_California_carrier4 <= 40000
 San_Francisco,_California_carrier5 <= 50000
 San_Francisco,_California_carrier6 <= 60000
 Philadelphia,_Pennsylvania_carrier3 <= 100
 Dallas,_Texas_NONFIXEDCAPACITY <= 930
 San_Francisco,_California_NONFIXEDCAPACITY <= 930
 Philadelphia,_Pennsylvania_NONFIXEDCAPACITY <= 930
 dummy_NONFIXEDCAPACITY <= 1e+06
End
