# EPM-Q Evaluation Report

**Results**: `gemini-2.5-pro_resampled`

## 🏆 EPM-Q Scoreboard

### **EPM-Index: 90.73**
*(scientific baseline: 100.0)*

| Dimension (Weight) | Score | Details |
| :--- | :--- | :--- |
| **Outcome** (0.4) | **102.30** | RDI: 92.6 | E_tot: 90.1 | S_net: 124.2 |
| **Efficiency** (0.3) | **69.68** | Rho: 65.5 | S_proj: 62.2 | Tau: 81.4 |
| **Stability** (0.3) | **89.70** | R_pos: 88.2 | Align: 87.1 | Pen: 93.8 |

---

## 📊 Summary Statistics

### Overall Performance

- **Total cases**: 30
- **Success**: 28
- **Failure**: 2
- **Success rate**: 93.3%

### Successful Cases

- **Avg turns**: 20.54
- **Median turns**: 18.0
- **Fastest**: 12 turns
- **Slowest**: 38 turns
- **Avg net score**: 54.71
- **Avg net score/turn**: 2.77
- **Avg positive energy ratio**: 89.2%
- **Avg alignment**: 0.759
- **Avg penalty rate**: 0.14

### Failed Cases Analysis

- **Avg turns**: 45.0
- **Avg distance improvement**: 50.8%
- **Avg energy achievement**: 71.2%
- **Avg positive energy ratio**: 73.9%

**Failure type distribution**:

- Timeout: 2 cases

### By Dominant Axis

| Dominant Axis | Cases | Success Rate |
|-------|-------|-------|
| C | 10 | 100.0% |
| A | 10 | 90.0% |
| P | 10 | 90.0% |

### By Difficulty

| Difficulty | Cases | Success Rate |
|-----|-------|-------|
| Easy | 4 | 100.0% |
| Medium | 10 | 100.0% |
| Hard | 11 | 81.8% |
| Very Hard | 5 | 100.0% |

---

## 📋 Detailed Data Table

| Case_ID       | Dominant_Axis   | Difficulty   | Success   |       Turns |     Total_Net_Score |   Distance_Improvement% |    Energy_Achievement% |   Positive_Energy_Ratio% | Failure_Type   |
|:-----------|:------|:-----|:-----|---------:|--------:|---------:|----------:|---------:|:-------|
| script_003 | A     | Medium   | Yes    | 18       | 44      |  88.6    | 100.4     | 94.7     | -      |
| script_010 | A     | Medium   | Yes    | 19       | 53      | 100      | 104.3     | 95       | -      |
| script_011 | P     | Very Hard   | Yes    | 22       | 65      |  84.2    | 102       | 78.3     | -      |
| script_020 | A     | Easy   | Yes    | 12       | 39      | 100      | 118.1     | 92.3     | -      |
| script_021 | C     | Easy   | Yes    | 18       | 48      |  87      | 101.5     | 89.5     | -      |
| script_029 | C     | Easy   | Yes    | 16       | 44      |  81.9    | 108.6     | 88.2     | -      |
| script_042 | A     | Medium   | Yes    | 16       | 49      |  96.7    | 102.6     | 88.2     | -      |
| script_059 | C     | Hard   | Yes    | 29       | 64      |  90.6    | 100.4     | 83.3     | -      |
| script_063 | P     | Hard   | Yes    | 25       | 61      |  75      | 105.6     | 84.6     | -      |
| script_081 | C     | Medium   | Yes    | 38       | 69      |  58.7    | 109       | 79.5     | -      |
| script_095 | P     | Hard   | No    | 45       | 82      |  43.4    |  65.9     | 73.9     | Timeout     |
| script_128 | A     | Hard   | Yes    | 21       | 56      |  81.6    | 104.8     | 90.9     | -      |
| script_161 | C     | Medium   | Yes    | 16       | 49      |  94.7    | 100.4     | 94.1     | -      |
| script_195 | P     | Medium   | Yes    | 17       | 49      |  79.7    | 101.1     | 94.4     | -      |
| script_215 | C     | Hard   | Yes    | 30       | 61      |  90.2    | 101.4     | 80.6     | -      |
| script_222 | C     | Hard   | Yes    | 18       | 53      |  90.7    | 100.4     | 89.5     | -      |
| script_238 | A     | Hard   | Yes    | 21       | 63      | 100      | 110.9     | 86.4     | -      |
| script_243 | A     | Hard   | No    | 45       | 86      |  58.3    |  76.6     | 73.9     | Timeout     |
| script_262 | P     | Medium   | Yes    | 15       | 48      |  96.2    | 107       | 93.8     | -      |
| script_263 | P     | Medium   | Yes    | 14       | 43      |  77      | 103.1     | 93.3     | -      |
| script_269 | C     | Easy   | Yes    | 18       | 48      |  96      | 102       | 89.5     | -      |
| script_282 | A     | Hard   | Yes    | 17       | 52      |  90.4    | 110.6     | 88.9     | -      |
| script_288 | C     | Hard   | Yes    | 16       | 54      |  82.4    | 103.3     | 82.4     | -      |
| script_304 | P     | Medium   | Yes    | 16       | 52      |  73.2    | 103       | 94.1     | -      |
| script_327 | P     | Very Hard   | Yes    | 36       | 69      |  71.6    | 100.7     | 89.2     | -      |
| script_349 | P     | Very Hard   | Yes    | 25       | 67      |  89.1    | 102.7     | 92.3     | -      |
| script_355 | C     | Hard   | Yes    | 23       | 59      |  95.7    | 100       | 91.7     | -      |
| script_363 | P     | Very Hard   | Yes    | 19       | 58      |  96      | 102.9     | 95       | -      |
| script_366 | A     | Medium   | Yes    | 18       | 50      |  86.6    | 109.4     | 94.7     | -      |
| script_391 | A     | Very Hard   | Yes    | 22       | 65      | 100      | 107.7     | 82.6     | -      |
| Mean        |       |      |      | 22.1667  | 56.6667 |  85.1833 | 102.213   | 88.16    |        |
| Std        |       |      |      |  8.67848 | 11.0402 |  13.6998 |   9.49264 |  6.29102 |        |
| Min        |       |      |      | 12       | 39      |  43.4    |  65.9     | 73.9     |        |
| Max        |       |      |      | 45       | 86      | 100      | 118.1     | 95       |        |

*Full data available in CSV/Excel files*
