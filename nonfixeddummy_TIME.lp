\ Model StochLPNonfixedDummy
\ LP format - for model browsing. Use MPS format to capture full model detail.
Minimize
  27.5 Dallas,_Texas_DT_Carrier_0000-0000_SubLoc_00000
   + 37.5 Dallas,_Texas_DT_Carrier_0000-0001_SubLoc_00000
   + 32.5 Washington_D.C.,_Washington_D.C._WDC_Carrier_0000-0000_SubLoc_00000
   + 40 Washington_D.C.,_Washington_D.C._WDC_Carrier_0000-0001_SubLoc_00000
   + 13 San_Francisco,_California_SF_Carrier_0000-0000_SubLoc_00000
   + 25 San_Francisco,_California_SF_Carrier_0000-0001_SubLoc_00000
   + 500000 dummy_dummycarrier_0000-0000_SubLoc_00000
   + 500000 dummy_dummycarrier_0000-0001_SubLoc_00000
Subject To
 CARRIER<Dallas,_Texas_DT_Carrier_0000-0000>>:
   - Dallas,_Texas_DT_Carrier0000-0000 >= -200000
 CARRIER<Dallas,_Texas_DT_Carrier_0000-0001>>:
   - Dallas,_Texas_DT_Carrier0000-0001 >= -200000
 CARRIER<Washington_D.C.,_Washington_D.C._WDC_Carrier_0000-0000>>:
   - Washington_D.C.,_Washington_D.C._WDC_Carrier0000-0000 >= -200000
 CARRIER<Washington_D.C.,_Washington_D.C._WDC_Carrier_0000-0001>>:
   - Washington_D.C.,_Washington_D.C._WDC_Carrier0000-0001 >= -200000
 CARRIER<San_Francisco,_California_SF_Carrier_0000-0000>>:
   - San_Francisco,_California_SF_Carrier0000-0000 >= -200000
 CARRIER<San_Francisco,_California_SF_Carrier_0000-0001>>:
   - San_Francisco,_California_SF_Carrier0000-0001 >= -200000
 DEMAND<0000-0000_SubLoc_00000>:
   - Dallas,_Texas_DT_Carrier_0000-0000_SubLoc_00000
   - Washington_D.C.,_Washington_D.C._WDC_Carrier_0000-0000_SubLoc_00000
   - San_Francisco,_California_SF_Carrier_0000-0000_SubLoc_00000
   - dummy_dummycarrier_0000-0000_SubLoc_00000 = -2
 DEMAND<0000-0001_SubLoc_00000>:
   - Dallas,_Texas_DT_Carrier_0000-0001_SubLoc_00000
   - Washington_D.C.,_Washington_D.C._WDC_Carrier_0000-0001_SubLoc_00000
   - San_Francisco,_California_SF_Carrier_0000-0001_SubLoc_00000
   - dummy_dummycarrier_0000-0001_SubLoc_00000 = -1
 FLOW<Dallas,_Texas_DT_Carrier_0000-0000>:
   Dallas,_Texas_DT_Carrier0000-0000
   - Dallas,_Texas_DT_Carrier_0000-0000_SubLoc_00000 = 0
 FLOW<Washington_D.C.,_Washington_D.C._WDC_Carrier_0000-0000>:
   Washington_D.C.,_Washington_D.C._WDC_Carrier0000-0000
   - Washington_D.C.,_Washington_D.C._WDC_Carrier_0000-0000_SubLoc_00000
   = 0
 FLOW<dummy_dummycarrier_0000-0000>: dummy_dummycarrier_0000-0000
   - dummy_dummycarrier_0000-0000_SubLoc_00000 = 0
 FLOW<San_Francisco,_California_SF_Carrier_0000-0000>:
   San_Francisco,_California_SF_Carrier0000-0000
   - San_Francisco,_California_SF_Carrier_0000-0000_SubLoc_00000 = 0
 FLOW<Dallas,_Texas_DT_Carrier_0000-0001>:
   Dallas,_Texas_DT_Carrier0000-0001
   - Dallas,_Texas_DT_Carrier_0000-0001_SubLoc_00000 = 0
 FLOW<Washington_D.C.,_Washington_D.C._WDC_Carrier_0000-0001>:
   Washington_D.C.,_Washington_D.C._WDC_Carrier0000-0001
   - Washington_D.C.,_Washington_D.C._WDC_Carrier_0000-0001_SubLoc_00000
   = 0
 FLOW<dummy_dummycarrier_0000-0001>: dummy_dummycarrier_0000-0001
   - dummy_dummycarrier_0000-0001_SubLoc_00000 = 0
 FLOW<San_Francisco,_California_SF_Carrier_0000-0001>:
   San_Francisco,_California_SF_Carrier0000-0001
   - San_Francisco,_California_SF_Carrier_0000-0001_SubLoc_00000 = 0
 TOTALINVENTORY<>: - Dallas,_Texas_NONFIXEDCAPACITY
   - Washington_D.C.,_Washington_D.C._NONFIXEDCAPACITY
   - San_Francisco,_California_NONFIXEDCAPACITY = -3
 TOTALINVENTORYDummy<>: - dummy_NONFIXEDCAPACITY = -1e+08
 DEPOT<Dallas,_Texas_0000-0000>: - Dallas,_Texas_DT_Carrier0000-0000
   + Dallas,_Texas_NONFIXEDCAPACITY >= 0
 DEPOT<Washington_D.C.,_Washington_D.C._0000-0000>:
   - Washington_D.C.,_Washington_D.C._WDC_Carrier0000-0000
   + Washington_D.C.,_Washington_D.C._NONFIXEDCAPACITY >= 0
 DEPOT<dummy_0000-0000>: - dummy_dummycarrier_0000-0000
   + dummy_NONFIXEDCAPACITY >= 0
 DEPOT<San_Francisco,_California_0000-0000>:
   - San_Francisco,_California_SF_Carrier0000-0000
   + San_Francisco,_California_NONFIXEDCAPACITY >= 0
 DEPOT<Dallas,_Texas_0000-0001>: - Dallas,_Texas_DT_Carrier0000-0001
   + Dallas,_Texas_NONFIXEDCAPACITY >= 0
 DEPOT<Washington_D.C.,_Washington_D.C._0000-0001>:
   - Washington_D.C.,_Washington_D.C._WDC_Carrier0000-0001
   + Washington_D.C.,_Washington_D.C._NONFIXEDCAPACITY >= 0
 DEPOT<dummy_0000-0001>: - dummy_dummycarrier_0000-0001
   + dummy_NONFIXEDCAPACITY >= 0
 DEPOT<San_Francisco,_California_0000-0001>:
   - San_Francisco,_California_SF_Carrier0000-0001
   + San_Francisco,_California_NONFIXEDCAPACITY >= 0
Bounds
 Dallas,_Texas_NONFIXEDCAPACITY <= 3
 Washington_D.C.,_Washington_D.C._NONFIXEDCAPACITY <= 3
 San_Francisco,_California_NONFIXEDCAPACITY <= 3
 dummy_NONFIXEDCAPACITY <= 1e+08
End
