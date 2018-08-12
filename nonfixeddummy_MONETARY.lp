\ Model StochLPNonfixedDummy
\ LP format - for model browsing. Use MPS format to capture full model detail.
Minimize
  0.03499965 Dallas,_Texas_carrier1_0000-0000_SubLoc_00000
   + 0.03499965 Dallas,_Texas_carrier1_0000-0001_SubLoc_00000
   + 0.000699993 Dallas,_Texas_carrier1_0000-0002_SubLoc_00000
   + 0.0366663 Dallas,_Texas_carrier2_0000-0000_SubLoc_00000
   + 0.0366663 Dallas,_Texas_carrier2_0000-0001_SubLoc_00000
   + 0.000733326 Dallas,_Texas_carrier2_0000-0002_SubLoc_00000
   + 0.00799992 San_Francisco,_California_carrier4_0000-0000_SubLoc_00000
   + 0.00799992 San_Francisco,_California_carrier4_0000-0001_SubLoc_00000
   + 0.05599944 San_Francisco,_California_carrier4_0000-0002_SubLoc_00000
   + 0.00833325 San_Francisco,_California_carrier5_0000-0000_SubLoc_00000
   + 0.00833325 San_Francisco,_California_carrier5_0000-0001_SubLoc_00000
   + 0.05833275 San_Francisco,_California_carrier5_0000-0002_SubLoc_00000
   + 0.00866658 San_Francisco,_California_carrier6_0000-0000_SubLoc_00000
   + 0.00866658 San_Francisco,_California_carrier6_0000-0001_SubLoc_00000
   + 0.06066606 San_Francisco,_California_carrier6_0000-0002_SubLoc_00000
   + 0.000766659 Philadelphia,_Pennsylvania_carrier3_0000-0000_SubLoc_00000
   + 0.000766659 Philadelphia,_Pennsylvania_carrier3_0000-0001_SubLoc_00000
   + 0.05366613 Philadelphia,_Pennsylvania_carrier3_0000-0002_SubLoc_00000
   + 3.3333 dummy_dummycarrier_0000-0000_SubLoc_00000
   + 3.3333 dummy_dummycarrier_0000-0001_SubLoc_00000
   + 3.3333 dummy_dummycarrier_0000-0002_SubLoc_00000
Subject To
 CARRIER<Dallas,_Texas_carrier1_0000-0000>>:
   - Dallas,_Texas_carrier10000-0000 >= -2e+06
 CARRIER<Dallas,_Texas_carrier1_0000-0001>>:
   - Dallas,_Texas_carrier10000-0001 >= -2e+06
 CARRIER<Dallas,_Texas_carrier1_0000-0002>>:
   - Dallas,_Texas_carrier10000-0002 >= -2e+06
 CARRIER<Dallas,_Texas_carrier2_0000-0000>>:
   - Dallas,_Texas_carrier20000-0000 >= -400000
 CARRIER<Dallas,_Texas_carrier2_0000-0001>>:
   - Dallas,_Texas_carrier20000-0001 >= -400000
 CARRIER<Dallas,_Texas_carrier2_0000-0002>>:
   - Dallas,_Texas_carrier20000-0002 >= -400000
 CARRIER<San_Francisco,_California_carrier4_0000-0000>>:
   - San_Francisco,_California_carrier40000-0000 >= -8e+06
 CARRIER<San_Francisco,_California_carrier4_0000-0001>>:
   - San_Francisco,_California_carrier40000-0001 >= -8e+06
 CARRIER<San_Francisco,_California_carrier4_0000-0002>>:
   - San_Francisco,_California_carrier40000-0002 >= -8e+06
 CARRIER<San_Francisco,_California_carrier5_0000-0000>>:
   - San_Francisco,_California_carrier50000-0000 >= -1e+07
 CARRIER<San_Francisco,_California_carrier5_0000-0001>>:
   - San_Francisco,_California_carrier50000-0001 >= -1e+07
 CARRIER<San_Francisco,_California_carrier5_0000-0002>>:
   - San_Francisco,_California_carrier50000-0002 >= -1e+07
 CARRIER<San_Francisco,_California_carrier6_0000-0000>>:
   - San_Francisco,_California_carrier60000-0000 >= -1.2e+07
 CARRIER<San_Francisco,_California_carrier6_0000-0001>>:
   - San_Francisco,_California_carrier60000-0001 >= -1.2e+07
 CARRIER<San_Francisco,_California_carrier6_0000-0002>>:
   - San_Francisco,_California_carrier60000-0002 >= -1.2e+07
 CARRIER<Philadelphia,_Pennsylvania_carrier3_0000-0000>>:
   - Philadelphia,_Pennsylvania_carrier30000-0000 >= -20000
 CARRIER<Philadelphia,_Pennsylvania_carrier3_0000-0001>>:
   - Philadelphia,_Pennsylvania_carrier30000-0001 >= -20000
 CARRIER<Philadelphia,_Pennsylvania_carrier3_0000-0002>>:
   - Philadelphia,_Pennsylvania_carrier30000-0002 >= -20000
 DEMAND<0000-0000_SubLoc_00000>:
   - Dallas,_Texas_carrier1_0000-0000_SubLoc_00000
   - Dallas,_Texas_carrier2_0000-0000_SubLoc_00000
   - San_Francisco,_California_carrier4_0000-0000_SubLoc_00000
   - San_Francisco,_California_carrier5_0000-0000_SubLoc_00000
   - San_Francisco,_California_carrier6_0000-0000_SubLoc_00000
   - Philadelphia,_Pennsylvania_carrier3_0000-0000_SubLoc_00000
   - dummy_dummycarrier_0000-0000_SubLoc_00000 = -930000
 DEMAND<0000-0001_SubLoc_00000>:
   - Dallas,_Texas_carrier1_0000-0001_SubLoc_00000
   - Dallas,_Texas_carrier2_0000-0001_SubLoc_00000
   - San_Francisco,_California_carrier4_0000-0001_SubLoc_00000
   - San_Francisco,_California_carrier5_0000-0001_SubLoc_00000
   - San_Francisco,_California_carrier6_0000-0001_SubLoc_00000
   - Philadelphia,_Pennsylvania_carrier3_0000-0001_SubLoc_00000
   - dummy_dummycarrier_0000-0001_SubLoc_00000 = -80000
 DEMAND<0000-0002_SubLoc_00000>:
   - Dallas,_Texas_carrier1_0000-0002_SubLoc_00000
   - Dallas,_Texas_carrier2_0000-0002_SubLoc_00000
   - San_Francisco,_California_carrier4_0000-0002_SubLoc_00000
   - San_Francisco,_California_carrier5_0000-0002_SubLoc_00000
   - San_Francisco,_California_carrier6_0000-0002_SubLoc_00000
   - Philadelphia,_Pennsylvania_carrier3_0000-0002_SubLoc_00000
   - dummy_dummycarrier_0000-0002_SubLoc_00000 = -50000
 FLOW<dummy_dummycarrier_0000-0000>: dummy_dummycarrier_0000-0000
   - dummy_dummycarrier_0000-0000_SubLoc_00000 = 0
 FLOW<Dallas,_Texas_carrier1_0000-0000>: Dallas,_Texas_carrier10000-0000
   - Dallas,_Texas_carrier1_0000-0000_SubLoc_00000 = 0
 FLOW<Dallas,_Texas_carrier2_0000-0000>: Dallas,_Texas_carrier20000-0000
   - Dallas,_Texas_carrier2_0000-0000_SubLoc_00000 = 0
 FLOW<San_Francisco,_California_carrier4_0000-0000>:
   San_Francisco,_California_carrier40000-0000
   - San_Francisco,_California_carrier4_0000-0000_SubLoc_00000 = 0
 FLOW<San_Francisco,_California_carrier5_0000-0000>:
   San_Francisco,_California_carrier50000-0000
   - San_Francisco,_California_carrier5_0000-0000_SubLoc_00000 = 0
 FLOW<San_Francisco,_California_carrier6_0000-0000>:
   San_Francisco,_California_carrier60000-0000
   - San_Francisco,_California_carrier6_0000-0000_SubLoc_00000 = 0
 FLOW<Philadelphia,_Pennsylvania_carrier3_0000-0000>:
   Philadelphia,_Pennsylvania_carrier30000-0000
   - Philadelphia,_Pennsylvania_carrier3_0000-0000_SubLoc_00000 = 0
 FLOW<dummy_dummycarrier_0000-0001>: dummy_dummycarrier_0000-0001
   - dummy_dummycarrier_0000-0001_SubLoc_00000 = 0
 FLOW<Dallas,_Texas_carrier1_0000-0001>: Dallas,_Texas_carrier10000-0001
   - Dallas,_Texas_carrier1_0000-0001_SubLoc_00000 = 0
 FLOW<Dallas,_Texas_carrier2_0000-0001>: Dallas,_Texas_carrier20000-0001
   - Dallas,_Texas_carrier2_0000-0001_SubLoc_00000 = 0
 FLOW<San_Francisco,_California_carrier4_0000-0001>:
   San_Francisco,_California_carrier40000-0001
   - San_Francisco,_California_carrier4_0000-0001_SubLoc_00000 = 0
 FLOW<San_Francisco,_California_carrier5_0000-0001>:
   San_Francisco,_California_carrier50000-0001
   - San_Francisco,_California_carrier5_0000-0001_SubLoc_00000 = 0
 FLOW<San_Francisco,_California_carrier6_0000-0001>:
   San_Francisco,_California_carrier60000-0001
   - San_Francisco,_California_carrier6_0000-0001_SubLoc_00000 = 0
 FLOW<Philadelphia,_Pennsylvania_carrier3_0000-0001>:
   Philadelphia,_Pennsylvania_carrier30000-0001
   - Philadelphia,_Pennsylvania_carrier3_0000-0001_SubLoc_00000 = 0
 FLOW<dummy_dummycarrier_0000-0002>: dummy_dummycarrier_0000-0002
   - dummy_dummycarrier_0000-0002_SubLoc_00000 = 0
 FLOW<Dallas,_Texas_carrier1_0000-0002>: Dallas,_Texas_carrier10000-0002
   - Dallas,_Texas_carrier1_0000-0002_SubLoc_00000 = 0
 FLOW<Dallas,_Texas_carrier2_0000-0002>: Dallas,_Texas_carrier20000-0002
   - Dallas,_Texas_carrier2_0000-0002_SubLoc_00000 = 0
 FLOW<San_Francisco,_California_carrier4_0000-0002>:
   San_Francisco,_California_carrier40000-0002
   - San_Francisco,_California_carrier4_0000-0002_SubLoc_00000 = 0
 FLOW<San_Francisco,_California_carrier5_0000-0002>:
   San_Francisco,_California_carrier50000-0002
   - San_Francisco,_California_carrier5_0000-0002_SubLoc_00000 = 0
 FLOW<San_Francisco,_California_carrier6_0000-0002>:
   San_Francisco,_California_carrier60000-0002
   - San_Francisco,_California_carrier6_0000-0002_SubLoc_00000 = 0
 FLOW<Philadelphia,_Pennsylvania_carrier3_0000-0002>:
   Philadelphia,_Pennsylvania_carrier30000-0002
   - Philadelphia,_Pennsylvania_carrier3_0000-0002_SubLoc_00000 = 0
 TOTALINVENTORY<>: - Dallas,_Texas_NONFIXEDCAPACITY
   - Philadelphia,_Pennsylvania_NONFIXEDCAPACITY
   - San_Francisco,_California_NONFIXEDCAPACITY = -930000
 TOTALINVENTORYDummy<>: - dummy_NONFIXEDCAPACITY = -1e+08
 DEPOT<dummy_0000-0000>: - dummy_dummycarrier_0000-0000
   + dummy_NONFIXEDCAPACITY >= 0
 DEPOT<Dallas,_Texas_0000-0000>: - Dallas,_Texas_carrier10000-0000
   - Dallas,_Texas_carrier20000-0000 + Dallas,_Texas_NONFIXEDCAPACITY >= 0
 DEPOT<San_Francisco,_California_0000-0000>:
   - San_Francisco,_California_carrier40000-0000
   - San_Francisco,_California_carrier50000-0000
   - San_Francisco,_California_carrier60000-0000
   + San_Francisco,_California_NONFIXEDCAPACITY >= 0
 DEPOT<Philadelphia,_Pennsylvania_0000-0000>:
   - Philadelphia,_Pennsylvania_carrier30000-0000
   + Philadelphia,_Pennsylvania_NONFIXEDCAPACITY >= 0
 DEPOT<dummy_0000-0001>: - dummy_dummycarrier_0000-0001
   + dummy_NONFIXEDCAPACITY >= 0
 DEPOT<Dallas,_Texas_0000-0001>: - Dallas,_Texas_carrier10000-0001
   - Dallas,_Texas_carrier20000-0001 + Dallas,_Texas_NONFIXEDCAPACITY >= 0
 DEPOT<San_Francisco,_California_0000-0001>:
   - San_Francisco,_California_carrier40000-0001
   - San_Francisco,_California_carrier50000-0001
   - San_Francisco,_California_carrier60000-0001
   + San_Francisco,_California_NONFIXEDCAPACITY >= 0
 DEPOT<Philadelphia,_Pennsylvania_0000-0001>:
   - Philadelphia,_Pennsylvania_carrier30000-0001
   + Philadelphia,_Pennsylvania_NONFIXEDCAPACITY >= 0
 DEPOT<dummy_0000-0002>: - dummy_dummycarrier_0000-0002
   + dummy_NONFIXEDCAPACITY >= 0
 DEPOT<Dallas,_Texas_0000-0002>: - Dallas,_Texas_carrier10000-0002
   - Dallas,_Texas_carrier20000-0002 + Dallas,_Texas_NONFIXEDCAPACITY >= 0
 DEPOT<San_Francisco,_California_0000-0002>:
   - San_Francisco,_California_carrier40000-0002
   - San_Francisco,_California_carrier50000-0002
   - San_Francisco,_California_carrier60000-0002
   + San_Francisco,_California_NONFIXEDCAPACITY >= 0
 DEPOT<Philadelphia,_Pennsylvania_0000-0002>:
   - Philadelphia,_Pennsylvania_carrier30000-0002
   + Philadelphia,_Pennsylvania_NONFIXEDCAPACITY >= 0
Bounds
 Dallas,_Texas_NONFIXEDCAPACITY <= 930000
 Philadelphia,_Pennsylvania_NONFIXEDCAPACITY <= 930000
 San_Francisco,_California_NONFIXEDCAPACITY <= 930000
 dummy_NONFIXEDCAPACITY <= 1e+08
End
