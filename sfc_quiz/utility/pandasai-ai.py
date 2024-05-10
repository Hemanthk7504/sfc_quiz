api_key = "$2a$10$oYsm/9aTg4TJPvQDlSmSu.FdgSSUh.y6b2wtkOQqNPmcxyGZMhoii"

import os
import pandas as pd
from pandasai import Agent

# Sample DataFrame
sales_by_country ="""Supplier 	Order No.	Item No.	Item Description	Item Cost	Quantity	Cost per order
Hulkey Fasteners	Aug11001	1122	Airframe fasteners	$4.25	19,500	$82,875.00
Alum Sheeting	Aug11002	1243	Airframe fasteners	$4.25	10,000	$42,500.00
Fast‐Tie Aerospace	Aug11003	5462	Shielded Cable/ft.	$1.05	23,000	$24,150.00
Fast‐Tie Aerospace	Aug11004	5462	Shielded Cable/ft.	$1.05	21,500	$22,575.00
Steelpin Inc.	Aug11005	5319	Shielded Cable/ft.	$1.10	17,500	$19,250.00
Fast‐Tie Aerospace	Aug11006	5462	Shielded Cable/ft.	$1.05	22,500	$23,625.00
Steelpin Inc.	Aug11007	4312	Bolt‐nut package	$3.75	4,250	$15,937.50
Durrable Products	Aug11008	7258	Pressure Gauge	$90.00	100	$9,000.00
Fast‐Tie Aerospace	Aug11009	6321	O‐Ring	$2.45	1,300	$3,185.00
Fast‐Tie Aerospace	Aug11010	5462	Shielded Cable/ft.	$1.05	22,500	$23,625.00
Steelpin Inc.	Aug11011	5319	Shielded Cable/ft.	$1.10	18,100	$19,910.00
Hulkey Fasteners	Aug11012	3166	Electrical Connector	$1.25	5,600	$7,000.00
Hulkey Fasteners	Aug11013	9966	Hatch Decal	$0.75	500	$375.00
Steelpin Inc.	Aug11014	5234	Electrical Connector	$1.65	4,500	$7,425.00
Steelpin Inc.	Sep11001	4312	Bolt‐nut package	$3.75	4,200	$15,750.00
Alum Sheeting	Sep11002	5417	Control Panel	$255.00	406	$103,530.00
Hulkey Fasteners	Sep11003	3166	Electrical Connector	$1.25	5,500	$6,875.00
Steelpin Inc.	Sep11004	5234	Electrical Connector	$1.65	4,850	$8,002.50
Steelpin Inc.	Sep11005	4312	Bolt‐nut package	$3.75	4,150	$15,562.50
Hulkey Fasteners	Sep11006	1122	Airframe fasteners	$4.25	15,500	$65,875.00
Spacetime Technologies	Sep11007	4111	Bolt‐nut package	$3.55	4,800	$17,040.00
Alum Sheeting	Sep11008	1243	Airframe fasteners	$4.25	9,000	$38,250.00
Durrable Products	Sep11009	7258	Pressure Gauge	$90.00	120	$10,800.00
Steelpin Inc.	Sep11010	5234	Electrical Connector	$1.65	4,750	$7,837.50
Hulkey Fasteners	Sep11011	1122	Airframe fasteners	$4.25	12,500	$53,125.00
Hulkey Fasteners	Sep11012	5066	Shielded Cable/ft.	$0.95	25,000	$23,750.00
Hulkey Fasteners	Sep11013	3166	Electrical Connector	$1.25	5,650	$7,062.50
Hulkey Fasteners	Sep11014	1122	Airframe fasteners	$4.25	15,000	$63,750.00
Spacetime Technologies	Sep11015	4111	Bolt‐nut package	$3.55	4,585	$16,276.75
Hulkey Fasteners	Sep11016	3166	Electrical Connector	$1.25	5,425	$6,781.25
Fast‐Tie Aerospace	Sep11017	6321	O‐Ring	$2.45	1,200	$2,940.00
Steelpin Inc.	Sep11018	5319	Shielded Cable/ft.	$1.10	16,500	$18,150.00
Spacetime Technologies	Sep11019	4111	Bolt‐nut package	$3.55	4,200	$14,910.00
Hulkey Fasteners	Sep11020	5066	Shielded Cable/ft.	$0.95	17,500	$16,625.00
Spacetime Technologies	Sep11021	9752	Gasket	$4.05	1,500	$6,075.00
Spacetime Technologies	Sep11022	4111	Bolt‐nut package	$3.55	4,250	$15,087.50
Pylon Accessories	Sep11023	9764	Gasket	$3.75	1,980	$7,425.00
Pylon Accessories	Sep11024	9764	Gasket	$3.75	1,750	$6,562.50
Spacetime Technologies	Sep11025	9752	Gasket	$4.05	1,550	$6,277.50
Spacetime Technologies	Sep11026	4111	Bolt‐nut package	$3.55	4,200	$14,910.00
Durrable Products	Sep11027	1369	Airframe fasteners	$4.20	15,000	$63,000.00
Manley Valve	Sep11028	6431	O‐Ring	$2.85	1,300	$3,705.00
Fast‐Tie Aerospace	Sep11029	6321	O‐Ring	$2.45	2,500	$6,125.00
Pylon Accessories	Sep11030	9764	Gasket	$3.75	1,850	$6,937.50
Durrable Products	Sep11031	1369	Airframe fasteners	$4.20	14,000	$58,800.00
Hulkey Fasteners	Sep11032	1122	Airframe fasteners	$4.25	14,500	$61,625.00
Pylon Accessories	Sep11033	9764	Gasket	$3.75	1,800	$6,750.00
Durrable Products	Sep11034	1369	Airframe fasteners	$4.20	10,000	$42,000.00
Spacetime Technologies	Oct11001	5125	Shielded Cable/ft.	$1.15	15,000	$17,250.00
Durrable Products	Oct11002	9399	Gasket	$3.65	1,250	$4,562.50
Manley Valve	Oct11003	6431	O‐Ring	$2.85	1,350	$3,847.50
Pylon Accessories	Oct11004	6433	O‐Ring	$2.95	1,500	$4,425.00
Fast‐Tie Aerospace	Oct11005	5166	Electrical Connector	$1.25	5,650	$7,062.50
Hulkey Fasteners	Oct11006	1122	Airframe fasteners	$4.25	18,000	$76,500.00
Durrable Products	Oct11007	9399	Gasket	$3.65	1,450	$5,292.50
Spacetime Technologies	Oct11008	6489	O‐Ring	$3.00	1,100	$3,300.00
Durrable Products	Oct11009	9399	Gasket	$3.65	1,985	$7,245.25
Spacetime Technologies	Oct11010	4111	Bolt‐nut package	$3.55	4,600	$16,330.00
Durrable Products	Oct11011	4569	Bolt‐nut package	$3.50	3,900	$13,650.00
Manley Valve	Oct11012	6431	O‐Ring	$2.85	1,250	$3,562.50
Durrable Products	Oct11013	9399	Gasket	$3.65	1,470	$5,365.50
Durrable Products	Oct11014	5454	Control Panel	$220.00	550	$121,000.00
Spacetime Technologies	Oct11015	6489	O‐Ring	$3.00	900	$2,700.00
Alum Sheeting	Oct11016	1243	Airframe fasteners	$4.25	10,500	$44,625.00
Steelpin Inc.	Oct11017	8008	Machined Valve	$645.00	100	$64,500.00
Manley Valve	Oct11018	7258	Pressure Gauge	$100.50	90	$9,045.00
Manley Valve	Oct11019	8148	Machined Valve	$655.50	125	$81,937.50
Hulkey Fasteners	Oct11020	1122	Airframe fasteners	$4.25	17,000	$72,250.00
Fast‐Tie Aerospace	Oct11021	6321	O‐Ring	$2.45	1,250	$3,062.50
Alum Sheeting	Oct11022	4224	Bolt‐nut package	$3.95	4,500	$17,775.00
Durrable Products	Oct11023	5454	Control Panel	$220.00	500	$110,000.00
Manley Valve	Oct11024	7258	Pressure Gauge	$100.50	100	$10,050.00
Steelpin Inc.	Oct11025	8008	Machined Valve	$645.00	150	$96,750.00
Alum Sheeting	Oct11026	5417	Control Panel	$255.00	500	$127,500.00
Manley Valve	Oct11027	7258	Pressure Gauge	$100.50	95	$9,547.50
Alum Sheeting	Oct11028	5634	Side Panel	$185.00	150	$27,750.00
Durrable Products	Oct11029	5275	Shielded Cable/ft.	$1.00	25,000	$25,000.00
Fast‐Tie Aerospace	Oct11030	6321	O‐Ring	$2.45	1,500	$3,675.00
Fast‐Tie Aerospace	Oct11031	5689	Side Panel	$175.00	155	$27,125.00
Hulkey Fasteners	Oct11032	1122	Airframe fasteners	$4.25	17,500	$74,375.00
Steelpin Inc.	Oct11033	5677	Side Panel	$195.00	130	$25,350.00
Steelpin Inc.	Oct11034	8008	Machined Valve	$645.00	120	$77,400.00
Spacetime Technologies	Oct11035	6489	O‐Ring	$3.00	1,050	$3,150.00
Alum Sheeting	Oct11036	5634	Side Panel	$185.00	140	$25,900.00
Manley Valve	Nov11001	9977	Panel Decal	$1.00	525	$525.00
Manley Valve	Nov11002	9955	Door Decal	$0.55	150	$82.50
Fast‐Tie Aerospace	Nov11003	5689	Side Panel	$175.00	150	$26,250.00
Fast‐Tie Aerospace	Nov11004	7268	Pressure Gauge	$95.00	110	$10,450.00
Steelpin Inc.	Nov11005	5677	Side Panel	$195.00	120	$23,400.00
Manley Valve	Nov11006	9967	Hatch Decal	$0.85	550	$467.50
Fast‐Tie Aerospace	Nov11007	7268	Pressure Gauge	$95.00	105	$9,975.00
Fast‐Tie Aerospace	Nov11008	5689	Side Panel	$175.00	175	$30,625.00
Steelpin Inc.	Nov11009	5677	Side Panel	$195.00	110	$21,450.00
Manley Valve	Nov11010	9955	Door Decal	$0.55	125	$68.75"""

df = pd.read_csv(pd.io.common.StringIO(sales_by_country), sep='\t', engine='python')

data = pd.DataFrame(df)
os.environ["PANDASAI_API_KEY"] = api_key

agent = Agent(df)
agent.chat('create a separate dataframe for the Steelpin Inc')
## Output
# China, United States, Japan, Germany, Australia