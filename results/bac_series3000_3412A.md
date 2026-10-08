# Baltimore Aircoil Series 3000, model 3412A (single cell)
Source: BAC bulletin S244/1-K "Series 3000 Cooling Towers", Engineering Data, page 14 (Single Cell Unit table),
https://baltimoreaircoil.com/sites/default/files/2022-09/S3000A.pdf . Read 10/8/2026 from the rendered table; each value checked by eye.

| Field | Value | Exact words on the sheet |
|---|---|---|
| Nominal capacity | 412 tons | "3412A 412" (NOMINAL TONS column) |
| Motor | 25 HP | "25" (MOTOR HP) |
| Fan airflow | 103,700 CFM | "103700" (FAN CFM) |
| Operating weight | 18,580 lb | "18580" (WEIGHTS (lbs) OPER.) |
| Shipping weight | 8,420 lb | "8420" (SHIPPING) |
| Heaviest section | 8,420 lb | "8420" (HEAVIEST SECTION) |
| Length | 9'-9 1/4" | DIMENSIONS L, shared by 3412A and 3436A |
| Width | 20'-0 1/2" | DIMENSIONS W, shared by 3412A and 3436A |
| Height | 10'-9 1/8" | DIMENSIONS H, shared by 3412A and 3436A |

Notes a catalog team should see:
- "A nominal ton is defined as 3 GPM of water cooled from 95°F to 85°F with a 78°F entering wet bulb." (note 1)
- Operating weight is "for tower with the water level in the cold water basin at overflow." (note 2)
- "Do not use for construction. Refer to factory certified dimensions." (page header)

**The catch:** dimensions are printed once per group of models (merged cells). In the PDF's text layer, the first dimension
values after the 3412A row are 9'-9 1/4", 20'-0 1/2" and then 12'-1 1/8", the 3455A/3482A/3527A group's height. A tool that
copies the text in order would give the 3412A a height of 12'-1 1/8" instead of 10'-9 1/8". Reading the table as it appears on the
page gets it right, and the quote check flags merged-cell values for a person to confirm.
