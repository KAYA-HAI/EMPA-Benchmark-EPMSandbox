# EPM-Q Evaluation Report

**Results**: `llama-3.1-8b-instruct_20251225_160804`

## 🏆 EPM-Q Scoreboard

### **EPM-Index: 14.29**
*(scientific baseline: 100.0)*

| Dimension (Weight) | Score | Details |
| :--- | :--- | :--- |
| **Outcome** (0.4) | **0.99** | RDI: 2.6 | E_tot: 0.0 | S_net: 0.4 |
| **Efficiency** (0.3) | **27.52** | Rho: 0.0 | S_proj: 0.0 | Tau: 82.5 |
| **Stability** (0.3) | **20.98** | R_pos: 19.5 | Align: 27.7 | Pen: 15.8 |

---

## 📊 Summary Statistics

### Overall Performance

- **Total cases**: 30
- **Success**: 0
- **Failure**: 30
- **Success rate**: 0.0%

### Failed Cases Analysis

- **Avg turns**: 15.07
- **Avg distance improvement**: -137.5%
- **Avg energy achievement**: -121.3%
- **Avg positive energy ratio**: 19.5%

**Failure type distribution**:

- Direction Collapse: 30 cases

### By Dominant Axis

| Dominant Axis | Cases | Success Rate |
|-------|-------|-------|
| C | 10 | 0.0% |
| A | 10 | 0.0% |
| P | 10 | 0.0% |

### By Difficulty

| Difficulty | Cases | Success Rate |
|-----|-------|-------|
| Easy | 4 | 0.0% |
| Medium | 10 | 0.0% |
| Hard | 11 | 0.0% |
| Very Hard | 5 | 0.0% |

---

## 📋 Detailed Data Table

| Case_ID       | Dominant_Axis   | Difficulty   | Success   |       Turns |      Total_Net_Score |    Distance_Improvement% |    Energy_Achievement% |   Positive_Energy_Ratio% | Failure_Type   |
|:-----------|:------|:-----|:-----|---------:|---------:|----------:|----------:|---------:|:-------|
| script_003 | A     | Medium   | No    | 12       |  -5      |  -99.9    |  -81      |  23.1    | Direction Collapse   |
| script_010 | A     | Medium   | No    | 21       | -29      | -195.3    | -177.7    |  22.7    | Direction Collapse   |
| script_011 | P     | Very Hard   | No    | 12       | -26      | -133.1    | -126      |   7.7    | Direction Collapse   |
| script_020 | A     | Easy   | No    | 12       |  -8      | -138.3    | -119      |  30.8    | Direction Collapse   |
| script_021 | C     | Easy   | No    | 12       | -15      | -154      | -129.1    |  15.4    | Direction Collapse   |
| script_029 | C     | Easy   | No    | 18       | -10      | -184.6    | -147.8    |  36.8    | Direction Collapse   |
| script_042 | A     | Medium   | No    | 17       | -22      | -162.2    | -147.3    |  16.7    | Direction Collapse   |
| script_059 | C     | Hard   | No    | 12       | -22      | -126.2    | -108.3    |  23.1    | Direction Collapse   |
| script_063 | P     | Hard   | No    | 17       | -28      | -158.8    | -134.6    |  22.2    | Direction Collapse   |
| script_081 | C     | Medium   | No    | 28       | -34      | -219.4    | -198      |  24.1    | Direction Collapse   |
| script_095 | P     | Hard   | No    | 17       | -29      | -155      | -141      |  11.1    | Direction Collapse   |
| script_128 | A     | Hard   | No    | 12       | -32      | -175.4    | -163.7    |   0      | Direction Collapse   |
| script_161 | C     | Medium   | No    | 14       |  -3      |  -73.7    |  -67.5    |  26.7    | Direction Collapse   |
| script_195 | P     | Medium   | No    | 14       |   5      |  -65.3    |  -50.4    |  40      | Direction Collapse   |
| script_215 | C     | Hard   | No    | 25       | -37      | -251.8    | -222.6    |  19.2    | Direction Collapse   |
| script_222 | C     | Hard   | No    | 12       |  -9      |  -86.6    |  -70.8    |  30.8    | Direction Collapse   |
| script_238 | A     | Hard   | No    | 12       | -18      | -112.6    | -102      |   7.7    | Direction Collapse   |
| script_243 | A     | Hard   | No    | 12       | -28      | -155.9    | -145.8    |   7.7    | Direction Collapse   |
| script_262 | P     | Medium   | No    | 23       | -17      | -199.3    | -171.7    |  29.2    | Direction Collapse   |
| script_263 | P     | Medium   | No    | 12       |  -8      | -101      |  -86.1    |  23.1    | Direction Collapse   |
| script_269 | C     | Easy   | No    | 12       | -16      | -157.9    | -140.2    |   0      | Direction Collapse   |
| script_282 | A     | Hard   | No    | 15       | -23      | -147      | -138.9    |  12.5    | Direction Collapse   |
| script_288 | C     | Hard   | No    | 14       | -25      | -125.3    | -116.6    |   6.7    | Direction Collapse   |
| script_304 | P     | Medium   | No    | 23       | -15      | -189.7    | -148.6    |  29.2    | Direction Collapse   |
| script_327 | P     | Very Hard   | No    | 12       | -10      |  -87.5    |  -77.7    |  15.4    | Direction Collapse   |
| script_349 | P     | Very Hard   | No    | 14       |  -7      |  -88.3    |  -79.2    |  33.3    | Direction Collapse   |
| script_355 | C     | Hard   | No    | 12       | -18      | -115.4    | -106.7    |   7.7    | Direction Collapse   |
| script_363 | P     | Very Hard   | No    | 12       |  -7      |  -70.3    |  -65.7    |  30.8    | Direction Collapse   |
| script_366 | A     | Medium   | No    | 12       | -13      | -124.7    | -109      |  15.4    | Direction Collapse   |
| script_391 | A     | Very Hard   | No    | 12       |  -9      |  -71.3    |  -65.8    |  15.4    | Direction Collapse   |
| Mean        |       |      |      | 15.0667  | -17.2667 | -137.527  | -121.293  |  19.4833 |        |
| Std        |       |      |      |  4.55566 |  10.3588 |   47.6361 |   42.2697 |  10.6458 |        |
| Min        |       |      |      | 12       | -37      | -251.8    | -222.6    |   0      |        |
| Max        |       |      |      | 28       |   5      |  -65.3    |  -50.4    |  40      |        |

*Full data available in CSV/Excel files*
