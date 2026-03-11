# EPM-Q Evaluation Report

**Results**: `seed-2.0-new`

## 🏆 EPM-Q Scoreboard

### **EPM-Index: 87.62**
*(scientific baseline: 100.0)*

| Dimension (Weight) | Score | Details |
| :--- | :--- | :--- |
| **Outcome** (0.4) | **104.07** | RDI: 90.9 | E_tot: 87.2 | S_net: 134.1 |
| **Efficiency** (0.3) | **59.84** | Rho: 55.7 | S_proj: 53.1 | Tau: 70.8 |
| **Stability** (0.3) | **85.05** | R_pos: 83.1 | Align: 84.0 | Pen: 88.1 |

---

## 📊 Summary Statistics

### Overall Performance

- **Total cases**: 30
- **Success**: 28
- **Failure**: 2
- **Success rate**: 93.3%

### Successful Cases

- **Avg turns**: 24.68
- **Median turns**: 23.5
- **Fastest**: 12 turns
- **Slowest**: 44 turns
- **Avg net score**: 63.11
- **Avg net score/turn**: 2.65
- **Avg positive energy ratio**: 84.6%
- **Avg alignment**: 0.703
- **Avg penalty rate**: 0.32

### Failed Cases Analysis

- **Avg turns**: 23.5
- **Avg distance improvement**: 37.0%
- **Avg energy achievement**: 39.4%
- **Avg positive energy ratio**: 61.6%

**Failure type distribution**:

- Direction Collapse: 1 cases
- Stagnation: 1 cases

### By Dominant Axis

| Dominant Axis | Cases | Success Rate |
|-------|-------|-------|
| C | 10 | 90.0% |
| A | 10 | 90.0% |
| P | 10 | 100.0% |

### By Difficulty

| Difficulty | Cases | Success Rate |
|-----|-------|-------|
| Easy | 4 | 75.0% |
| Medium | 10 | 100.0% |
| Hard | 11 | 90.9% |
| Very Hard | 5 | 100.0% |

---

## 📋 Detailed Data Table

| Case_ID       | Dominant_Axis   | Difficulty   | Success   |       Turns |     Total_Net_Score |   Distance_Improvement% |   Energy_Achievement% |   Positive_Energy_Ratio% | Failure_Type   |
|:-----------|:------|:-----|:-----|---------:|--------:|---------:|---------:|---------:|:-------|
| script_003 | A     | Medium   | Yes    | 23       | 54      | 100      | 102.1    |  83.3    | -      |
| script_010 | A     | Medium   | Yes    | 24       | 59      |  90.1    | 100      |  80      | -      |
| script_011 | P     | Very Hard   | Yes    | 33       | 84      |  89.5    | 103.5    |  73.5    | -      |
| script_020 | A     | Easy   | Yes    | 12       | 37      | 100      | 101.3    |  92.3    | -      |
| script_021 | C     | Easy   | Yes    | 13       | 41      |  87      | 100      |  85.7    | -      |
| script_029 | C     | Easy   | Yes    | 14       | 42      |  95.5    | 100.9    |  93.3    | -      |
| script_042 | A     | Medium   | Yes    | 22       | 56      |  96.7    | 100.1    |  87      | -      |
| script_059 | C     | Hard   | Yes    | 22       | 60      |  93.7    | 104.2    |  95.7    | -      |
| script_063 | P     | Hard   | Yes    | 44       | 91      |  71.8    | 102      |  73.3    | -      |
| script_081 | C     | Medium   | Yes    | 29       | 63      |  89.7    | 104.6    |  83.3    | -      |
| script_095 | P     | Hard   | Yes    | 43       | 91      |   3.8    | 101.4    |  65.9    | -      |
| script_128 | A     | Hard   | Yes    | 24       | 60      |  72.4    | 101      |  88      | -      |
| script_161 | C     | Medium   | Yes    | 19       | 56      | 100      | 115      |  95      | -      |
| script_195 | P     | Medium   | Yes    | 19       | 56      | 100      | 103.6    |  95      | -      |
| script_215 | C     | Hard   | Yes    | 28       | 68      |  86.9    | 100.5    |  86.2    | -      |
| script_222 | C     | Hard   | Yes    | 34       | 75      |  75.3    | 105      |  77.1    | -      |
| script_238 | A     | Hard   | Yes    | 25       | 70      |  85.4    | 103.5    |  84.6    | -      |
| script_243 | A     | Hard   | No    | 17       | 28      |   8.6    |  11.2    |  55.6    | Direction Collapse   |
| script_262 | P     | Medium   | Yes    | 16       | 48      | 100      | 103.9    |  94.1    | -      |
| script_263 | P     | Medium   | Yes    | 15       | 45      |  88.5    | 104.3    |  87.5    | -      |
| script_269 | C     | Easy   | No    | 30       | 55      |  65.4    |  67.6    |  67.7    | Stagnation   |
| script_282 | A     | Hard   | Yes    | 20       | 56      |  87.2    | 102.2    |  85.7    | -      |
| script_288 | C     | Hard   | Yes    | 29       | 73      |  91.2    | 112.5    |  70      | -      |
| script_304 | P     | Medium   | Yes    | 18       | 51      |  96.7    | 100.7    |  94.7    | -      |
| script_327 | P     | Very Hard   | Yes    | 31       | 77      |  91.5    | 104.3    |  78.1    | -      |
| script_349 | P     | Very Hard   | Yes    | 24       | 68      | 100      | 101.4    |  92      | -      |
| script_355 | C     | Hard   | Yes    | 31       | 73      |  93.9    | 104.8    |  81.2    | -      |
| script_363 | P     | Very Hard   | Yes    | 40       | 96      |   0.6    | 102.5    |  70.7    | -      |
| script_366 | A     | Medium   | Yes    | 21       | 58      |  90      | 103.4    |  86.4    | -      |
| script_391 | A     | Very Hard   | Yes    | 18       | 59      | 100      | 101.4    |  89.5    | -      |
| Mean        |       |      |      | 24.6     | 61.6667 |  81.7133 |  98.9633 |  83.08   |        |
| Std        |       |      |      |  8.51611 | 16.2084 |  27.7636 |  18.1011 |  10.1342 |        |
| Min        |       |      |      | 12       | 28      |   0.6    |  11.2    |  55.6    |        |
| Max        |       |      |      | 44       | 96      | 100      | 115      |  95.7    |        |

*Full data available in CSV/Excel files*
