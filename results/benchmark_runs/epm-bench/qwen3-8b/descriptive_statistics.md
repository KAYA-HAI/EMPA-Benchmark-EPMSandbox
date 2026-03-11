# EPM-Q Evaluation Report

**Results**: `qwen3-8b_20260122_210701`

## 🏆 EPM-Q Scoreboard

### **EPM-Index: 12.16**
*(scientific baseline: 100.0)*

| Dimension (Weight) | Score | Details |
| :--- | :--- | :--- |
| **Outcome** (0.4) | **0.71** | RDI: 1.2 | E_tot: 0.0 | S_net: 0.9 |
| **Efficiency** (0.3) | **28.34** | Rho: 0.0 | S_proj: 0.0 | Tau: 85.0 |
| **Stability** (0.3) | **15.52** | R_pos: 16.1 | Align: 25.5 | Pen: 5.0 |

---

## 📊 Summary Statistics

### Overall Performance

- **Total cases**: 30
- **Success**: 0
- **Failure**: 30
- **Success rate**: 0.0%

### Failed Cases Analysis

- **Avg turns**: 13.6
- **Avg distance improvement**: -138.0%
- **Avg energy achievement**: -117.9%
- **Avg positive energy ratio**: 16.1%

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

| Case_ID       | Dominant_Axis   | Difficulty   | Success   |       Turns |    Total_Net_Score |    Distance_Improvement% |    Energy_Achievement% |   Positive_Energy_Ratio% | Failure_Type   |
|:-----------|:------|:-----|:-----|---------:|-------:|----------:|----------:|---------:|:-------|
| script_003 | A     | Medium   | No    | 12       |  -2    | -107.3    |  -91.5    | 15.4     | Direction Collapse   |
| script_010 | A     | Medium   | No    | 12       | -30    | -187      | -173.1    |  0       | Direction Collapse   |
| script_011 | P     | Very Hard   | No    | 12       | -25    | -122.5    | -115.4    | 15.4     | Direction Collapse   |
| script_020 | A     | Easy   | No    | 12       |   4    | -105.2    |  -85.3    | 38.5     | Direction Collapse   |
| script_021 | C     | Easy   | No    | 15       |  -8    | -172.9    | -134.7    | 18.8     | Direction Collapse   |
| script_029 | C     | Easy   | No    | 23       |  -5    | -240.6    | -175.1    | 37.5     | Direction Collapse   |
| script_042 | A     | Medium   | No    | 16       |  -2    | -119.5    | -102.3    | 23.5     | Direction Collapse   |
| script_059 | C     | Hard   | No    | 12       |  -5    | -104      |  -82      | 15.4     | Direction Collapse   |
| script_063 | P     | Hard   | No    | 12       | -17    | -121.3    |  -97.9    |  7.7     | Direction Collapse   |
| script_081 | C     | Medium   | No    | 16       | -22    | -156.8    | -140.9    | 23.5     | Direction Collapse   |
| script_095 | P     | Hard   | No    | 12       | -31    | -158.8    | -140.2    |  0       | Direction Collapse   |
| script_128 | A     | Hard   | No    | 12       | -34    | -175.4    | -165.5    |  7.7     | Direction Collapse   |
| script_161 | C     | Medium   | No    | 12       |  -7    | -119.3    |  -86.1    |  7.7     | Direction Collapse   |
| script_195 | P     | Medium   | No    | 15       |   0    | -108.1    |  -91.9    | 25       | Direction Collapse   |
| script_215 | C     | Hard   | No    | 12       | -15    | -117.5    | -100.1    | 23.1     | Direction Collapse   |
| script_222 | C     | Hard   | No    | 12       | -11    | -107.5    |  -93      |  7.7     | Direction Collapse   |
| script_238 | A     | Hard   | No    | 12       | -15    | -117.1    | -106.3    |  7.7     | Direction Collapse   |
| script_243 | A     | Hard   | No    | 12       | -35    | -180.6    | -160.6    |  0       | Direction Collapse   |
| script_262 | P     | Medium   | No    | 12       |  -3    | -105.7    |  -89.9    | 15.4     | Direction Collapse   |
| script_263 | P     | Medium   | No    | 12       | -26    | -197.3    | -165.1    |  7.7     | Direction Collapse   |
| script_269 | C     | Easy   | No    | 12       | -10    | -129.2    | -112.2    | 15.4     | Direction Collapse   |
| script_282 | A     | Hard   | No    | 13       |  -3    | -106.4    |  -88.2    | 21.4     | Direction Collapse   |
| script_288 | C     | Hard   | No    | 24       | -22    | -237.1    | -202.8    | 16       | Direction Collapse   |
| script_304 | P     | Medium   | No    | 12       | -11    | -128.8    | -103.1    | 15.4     | Direction Collapse   |
| script_327 | P     | Very Hard   | No    | 15       | -10    | -102.8    |  -86.7    | 25       | Direction Collapse   |
| script_349 | P     | Very Hard   | No    | 19       | -47    | -228.7    | -212.4    | 15       | Direction Collapse   |
| script_355 | C     | Hard   | No    | 12       | -16    | -118.1    | -106.4    |  7.7     | Direction Collapse   |
| script_363 | P     | Very Hard   | No    | 12       |   7    |  -53.1    |  -39.9    | 30.8     | Direction Collapse   |
| script_366 | A     | Medium   | No    | 12       | -16    | -139.6    | -123.8    | 15.4     | Direction Collapse   |
| script_391 | A     | Very Hard   | No    | 12       |  -3    |  -72.7    |  -63.7    | 23.1     | Direction Collapse   |
| Mean        |       |      |      | 13.6     | -14    | -138.03   | -117.87   | 16.0967  |        |
| Std        |       |      |      |  3.20129 |  12.86 |   46.2711 |   40.9453 |  9.91921 |        |
| Min        |       |      |      | 12       | -47    | -240.6    | -212.4    |  0       |        |
| Max        |       |      |      | 24       |   7    |  -53.1    |  -39.9    | 38.5     |        |

*Full data available in CSV/Excel files*
