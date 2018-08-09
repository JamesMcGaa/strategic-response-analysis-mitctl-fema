\ Model StochLPNonfixedDummy
\ LP format - for model browsing. Use MPS format to capture full model detail.
Minimize
  18.33315 Dallas,_Texas_carrier1_0000-0000_SubLoc_00000
   + 18.33315 Dallas,_Texas_carrier1_0000-0001_SubLoc_00000
   + 1.99998 Dallas,_Texas_carrier1_0000-0002_SubLoc_00000
   + 21.66645 Dallas,_Texas_carrier2_0000-0000_SubLoc_00000
   + 21.66645 Dallas,_Texas_carrier2_0000-0001_SubLoc_00000
   + 5.33328 Dallas,_Texas_carrier2_0000-0002_SubLoc_00000
   + 6.6666 San_Francisco,_California_carrier4_0000-0000_SubLoc_00000
   + 6.6666 San_Francisco,_California_carrier4_0000-0001_SubLoc_00000
   + 26.6664 San_Francisco,_California_carrier4_0000-0002_SubLoc_00000
   + 9.9999 San_Francisco,_California_carrier5_0000-0000_SubLoc_00000
   + 9.9999 San_Francisco,_California_carrier5_0000-0001_SubLoc_00000
   + 29.9997 San_Francisco,_California_carrier5_0000-0002_SubLoc_00000
   + 13.3332 San_Francisco,_California_carrier6_0000-0000_SubLoc_00000
   + 13.3332 San_Francisco,_California_carrier6_0000-0001_SubLoc_00000
   + 33.333 San_Francisco,_California_carrier6_0000-0002_SubLoc_00000
   + 2.99997 Philadelphia,_Pennsylvania_carrier3_0000-0000_SubLoc_00000
   + 2.99997 Philadelphia,_Pennsylvania_carrier3_0000-0001_SubLoc_00000
   + 25.99974 Philadelphia,_Pennsylvania_carrier3_0000-0002_SubLoc_00000
   + 3333.3 dummy_dummycarrier_0000-0000_SubLoc_00000
   + 3333.3 dummy_dummycarrier_0000-0001_SubLoc_00000
   + 3333.3 dummy_dummycarrier_0000-0002_SubLoc_00000
Subject To
 DEMAND<0000-0000_SubLoc_00000>:
   - Dallas,_Texas_carrier1_0000-0000_SubLoc_00000
   - Dallas,_Texas_carrier2_0000-0000_SubLoc_00000
   - San_Francisco,_California_carrier4_0000-0000_SubLoc_00000
   - San_Francisco,_California_carrier5_0000-0000_SubLoc_00000
   - San_Francisco,_California_carrier6_0000-0000_SubLoc_00000
   - Philadelphia,_Pennsylvania_carrier3_0000-0000_SubLoc_00000
   - dummy_dummycarrier_0000-0000_SubLoc_00000 = -9300
 DEMAND<0000-0001_SubLoc_00000>:
   - Dallas,_Texas_carrier1_0000-0001_SubLoc_00000
   - Dallas,_Texas_carrier2_0000-0001_SubLoc_00000
   - San_Francisco,_California_carrier4_0000-0001_SubLoc_00000
   - San_Francisco,_California_carrier5_0000-0001_SubLoc_00000
   - San_Francisco,_California_carrier6_0000-0001_SubLoc_00000
   - Philadelphia,_Pennsylvania_carrier3_0000-0001_SubLoc_00000
   - dummy_dummycarrier_0000-0001_SubLoc_00000 = -800
 DEMAND<0000-0002_SubLoc_00000>:
   - Dallas,_Texas_carrier1_0000-0002_SubLoc_00000
   - Dallas,_Texas_carrier2_0000-0002_SubLoc_00000
   - San_Francisco,_California_carrier4_0000-0002_SubLoc_00000
   - San_Francisco,_California_carrier5_0000-0002_SubLoc_00000
   - San_Francisco,_California_carrier6_0000-0002_SubLoc_00000
   - Philadelphia,_Pennsylvania_carrier3_0000-0002_SubLoc_00000
   - dummy_dummycarrier_0000-0002_SubLoc_00000 = -500
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
   - San_Francisco,_California_NONFIXEDCAPACITY = -9300
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
 Dallas,_Texas_carrier10000-0000 <= 100000
 Dallas,_Texas_carrier10000-0001 <= 100000
 Dallas,_Texas_carrier10000-0002 <= 100000
 Dallas,_Texas_carrier20000-0000 <= 20000
 Dallas,_Texas_carrier20000-0001 <= 20000
 Dallas,_Texas_carrier20000-0002 <= 20000
 San_Francisco,_California_carrier40000-0000 <= 400000
 San_Francisco,_California_carrier40000-0001 <= 400000
 San_Francisco,_California_carrier40000-0002 <= 400000
 San_Francisco,_California_carrier50000-0000 <= 500000
 San_Francisco,_California_carrier50000-0001 <= 500000
 San_Francisco,_California_carrier50000-0002 <= 500000
 San_Francisco,_California_carrier60000-0000 <= 600000
 San_Francisco,_California_carrier60000-0001 <= 600000
 San_Francisco,_California_carrier60000-0002 <= 600000
 Philadelphia,_Pennsylvania_carrier30000-0000 <= 1000
 Philadelphia,_Pennsylvania_carrier30000-0001 <= 1000
 Philadelphia,_Pennsylvania_carrier30000-0002 <= 1000
 Dallas,_Texas_NONFIXEDCAPACITY <= 9300
 Philadelphia,_Pennsylvania_NONFIXEDCAPACITY <= 9300
 San_Francisco,_California_NONFIXEDCAPACITY <= 9300
 dummy_NONFIXEDCAPACITY <= 1e+08
End
