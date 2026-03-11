# EPM-Q Evaluation Report

**Results**: `qwen3-32b_resampled`

## 🏆 EPM-Q Scoreboard

### **EPM-Index: 14.77**
*(scientific baseline: 100.0)*

| Dimension (Weight) | Score | Details |
| :--- | :--- | :--- |
| **Outcome** (0.4) | **4.37** | RDI: 5.3 | E_tot: 0.0 | S_net: 7.7 |
| **Efficiency** (0.3) | **25.94** | Rho: 0.0 | S_proj: 0.0 | Tau: 77.7 |
| **Stability** (0.3) | **19.58** | R_pos: 20.9 | Align: 30.0 | Pen: 7.9 |

---

## 📊 Summary Statistics

### Overall Performance

- **Total cases**: 30
- **Success**: 0
- **Failure**: 30
- **Success rate**: 0.0%

### Failed Cases Analysis

- **Avg turns**: 14.9
- **Avg distance improvement**: -123.9%
- **Avg energy achievement**: -99.3%
- **Avg positive energy ratio**: 20.9%

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

| Case_ID       | Dominant_Axis   | Difficulty   | Success   |      Turns |       Total_Net_Score |    Distance_Improvement% |    Energy_Achievement% |   Positive_Energy_Ratio% | Failure_Type   |
|:-----------|:------|:-----|:-----|--------:|----------:|----------:|----------:|---------:|:-------|
| script_003 | A     | Medium   | No    | 12      |  -2       | -104.1    |  -87.6    |  23.1    | Direction Collapse   |
| script_010 | A     | Medium   | No    | 15      | -23       | -185.2    | -165.8    |  12.5    | Direction Collapse   |
| script_011 | P     | Very Hard   | No    | 12      | -21       | -132.2    | -119.5    |   7.7    | Direction Collapse   |
| script_020 | A     | Easy   | No    | 14      |   1       | -165.2    | -126.8    |  26.7    | Direction Collapse   |
| script_021 | C     | Easy   | No    | 17      | -12       | -215.5    | -166.7    |  22.2    | Direction Collapse   |
| script_029 | C     | Easy   | No    | 12      |   2       | -101.3    |  -81.6    |  23.1    | Direction Collapse   |
| script_042 | A     | Medium   | No    | 12      |  13       |  -46.8    |  -35.6    |  30.8    | Direction Collapse   |
| script_059 | C     | Hard   | No    | 12      |  -9       | -109.2    |  -89.4    |  23.1    | Direction Collapse   |
| script_063 | P     | Hard   | No    | 12      | -14       | -131.8    | -104.2    |   7.7    | Direction Collapse   |
| script_081 | C     | Medium   | No    | 19      |  18       |  -85.1    |  -34.5    |  35      | Direction Collapse   |
| script_095 | P     | Hard   | No    | 14      |  -6       | -101.2    |  -75.5    |  20      | Direction Collapse   |
| script_128 | A     | Hard   | No    | 24      | -34       | -257.1    | -228.9    |  12      | Direction Collapse   |
| script_161 | C     | Medium   | No    | 12      |  -6       | -132.6    |  -87.1    |   7.7    | Direction Collapse   |
| script_195 | P     | Medium   | No    | 12      |   4       |  -67.7    |  -57.7    |  30.8    | Direction Collapse   |
| script_215 | C     | Hard   | No    | 40      |  11       | -272.8    | -191.2    |  24.4    | Direction Collapse   |
| script_222 | C     | Hard   | No    | 15      |  24       |  -13      |    1.4    |  56.2    | Direction Collapse   |
| script_238 | A     | Hard   | No    | 12      |  -6       |  -76.9    |  -69.5    |  23.1    | Direction Collapse   |
| script_243 | A     | Hard   | No    | 14      |   2       |  -89      |  -76.3    |  20      | Direction Collapse   |
| script_262 | P     | Medium   | No    | 15      |  -5       | -144.4    | -116.3    |  25      | Direction Collapse   |
| script_263 | P     | Medium   | No    | 24      |  20       | -118.9    |  -65.5    |  40      | Direction Collapse   |
| script_269 | C     | Easy   | No    | 12      |  -9       | -140.3    | -118.6    |  15.4    | Direction Collapse   |
| script_282 | A     | Hard   | No    | 17      |  -4       | -139.3    | -122.9    |  22.2    | Direction Collapse   |
| script_288 | C     | Hard   | No    | 12      |  -3       |  -88.2    |  -73.2    |  15.4    | Direction Collapse   |
| script_304 | P     | Medium   | No    | 12      | -29       | -175.5    | -148.9    |   0      | Direction Collapse   |
| script_327 | P     | Very Hard   | No    | 15      |  -9       | -114.6    |  -99.3    |  18.8    | Direction Collapse   |
| script_349 | P     | Very Hard   | No    | 12      |   1       |  -61.4    |  -52.5    |  30.8    | Direction Collapse   |
| script_355 | C     | Hard   | No    | 12      | -14       | -128.1    | -108.2    |   7.7    | Direction Collapse   |
| script_363 | P     | Very Hard   | No    | 12      |   7       |  -51.1    |  -40.3    |  38.5    | Direction Collapse   |
| script_366 | A     | Medium   | No    | 12      | -15       | -146.7    | -128.3    |   7.7    | Direction Collapse   |
| script_391 | A     | Very Hard   | No    | 12      | -15       | -122.1    | -107.9    |   0      | Direction Collapse   |
| Mean        |       |      |      | 14.9    |  -4.43333 | -123.91   |  -99.28   |  20.92   |        |
| Std        |       |      |      |  5.7736 |  13.6879  |   57.7343 |   49.2604 |  12.4014 |        |
| Min        |       |      |      | 12      | -34       | -272.8    | -228.9    |   0      |        |
| Max        |       |      |      | 40      |  24       |  -13      |    1.4    |  56.2    |        |

*Full data available in CSV/Excel files*
