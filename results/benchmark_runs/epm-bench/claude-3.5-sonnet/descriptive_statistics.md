# EPM-Q Evaluation Report

**Results**: `claude-3.5-sonnet_20251224_132944`

## 🏆 EPM-Q Scoreboard

### **EPM-Index: 85.12**
*(scientific baseline: 100.0)*

| Dimension (Weight) | Score | Details |
| :--- | :--- | :--- |
| **Outcome** (0.4) | **101.17** | RDI: 91.9 | E_tot: 83.3 | S_net: 128.3 |
| **Efficiency** (0.3) | **59.74** | Rho: 54.8 | S_proj: 52.2 | Tau: 72.3 |
| **Stability** (0.3) | **81.75** | R_pos: 79.0 | Align: 81.5 | Pen: 84.7 |

---

## 📊 Summary Statistics

### Overall Performance

- **Total cases**: 30
- **Success**: 25
- **Failure**: 5
- **Success rate**: 83.3%

### Successful Cases

- **Avg turns**: 21.92
- **Median turns**: 21.0
- **Fastest**: 12 turns
- **Slowest**: 32 turns
- **Avg net score**: 59.92
- **Avg net score/turn**: 2.78
- **Avg positive energy ratio**: 84.2%
- **Avg alignment**: 0.723
- **Avg penalty rate**: 0.3

### Failed Cases Analysis

- **Avg turns**: 29.6
- **Avg distance improvement**: 20.0%
- **Avg energy achievement**: 33.2%
- **Avg positive energy ratio**: 53.4%

**Failure type distribution**:

- Stagnation: 2 cases
- Timeout: 2 cases
- Direction Collapse: 1 cases

### By Dominant Axis

| Dominant Axis | Cases | Success Rate |
|-------|-------|-------|
| C | 10 | 80.0% |
| A | 10 | 100.0% |
| P | 10 | 70.0% |

### By Difficulty

| Difficulty | Cases | Success Rate |
|-----|-------|-------|
| Easy | 4 | 75.0% |
| Medium | 10 | 90.0% |
| Hard | 11 | 90.9% |
| Very Hard | 5 | 60.0% |

---

## 📋 Detailed Data Table

| Case_ID       | Dominant_Axis   | Difficulty   | Success   |       Turns |     Total_Net_Score |   Distance_Improvement% |   Energy_Achievement% |   Positive_Energy_Ratio% | Failure_Type   |
|:-----------|:------|:-----|:-----|---------:|--------:|---------:|---------:|---------:|:-------|
| script_003 | A     | Medium   | Yes    | 20       | 54      |  96.2    | 101.4    |  76.2    | -      |
| script_010 | A     | Medium   | Yes    | 19       | 54      |  86.8    | 103.3    |  90      | -      |
| script_011 | P     | Very Hard   | No    | 14       | -4      | -81.3    | -75.2    |   6.7    | Direction Collapse   |
| script_020 | A     | Easy   | Yes    | 12       | 37      |  90      | 103.8    |  92.3    | -      |
| script_021 | C     | Easy   | Yes    | 13       | 43      |  91.3    | 106.2    |  92.9    | -      |
| script_029 | C     | Easy   | Yes    | 17       | 48      | 100      | 110.9    |  83.3    | -      |
| script_042 | A     | Medium   | Yes    | 18       | 54      | 100      | 104      |  84.2    | -      |
| script_059 | C     | Hard   | Yes    | 21       | 59      |  96.9    | 101.2    |  90.9    | -      |
| script_063 | P     | Hard   | No    | 12       | 14      |   3      |   3      |  53.8    | Stagnation   |
| script_081 | C     | Medium   | No    | 45       | 74      |  62.6    |  64.8    |  67.4    | Timeout     |
| script_095 | P     | Hard   | Yes    | 30       | 75      |  91.8    | 103.2    |  80.6    | -      |
| script_128 | A     | Hard   | Yes    | 32       | 75      | 100      | 102.6    |  75.8    | -      |
| script_161 | C     | Medium   | Yes    | 23       | 60      | 100      | 110      |  83.3    | -      |
| script_195 | P     | Medium   | Yes    | 26       | 66      | 100      | 103.6    |  81.5    | -      |
| script_215 | C     | Hard   | Yes    | 19       | 56      |  96.7    | 101.9    |  75      | -      |
| script_222 | C     | Hard   | Yes    | 17       | 55      | 100      | 101.5    |  88.9    | -      |
| script_238 | A     | Hard   | Yes    | 22       | 63      | 100      | 102.6    |  82.6    | -      |
| script_243 | A     | Hard   | Yes    | 24       | 68      |  93.8    | 104.7    |  84      | -      |
| script_262 | P     | Medium   | Yes    | 20       | 51      | 100      | 103.5    |  85.7    | -      |
| script_263 | P     | Medium   | Yes    | 19       | 50      |  92.3    | 104.7    |  85      | -      |
| script_269 | C     | Easy   | No    | 32       | 60      |  83.9    |  91.6    |  69.7    | Stagnation   |
| script_282 | A     | Hard   | Yes    | 30       | 66      |  95.5    | 100.8    |  71      | -      |
| script_288 | C     | Hard   | Yes    | 21       | 61      | 100      | 101.5    |  90.9    | -      |
| script_304 | P     | Medium   | Yes    | 16       | 49      |  90      | 101      |  82.4    | -      |
| script_327 | P     | Very Hard   | Yes    | 26       | 71      |  97.2    | 101.7    |  81.5    | -      |
| script_349 | P     | Very Hard   | Yes    | 29       | 79      |  97.3    | 103.6    |  80      | -      |
| script_355 | C     | Hard   | Yes    | 27       | 73      | 100      | 108.1    |  85.7    | -      |
| script_363 | P     | Very Hard   | No    | 45       | 97      |  31.9    |  81.8    |  69.6    | Timeout     |
| script_366 | A     | Medium   | Yes    | 26       | 67      |  96.7    | 104.2    |  85.2    | -      |
| script_391 | A     | Very Hard   | Yes    | 21       | 64      | 100      | 103.1    |  95.5    | -      |
| Mean        |       |      |      | 23.2     | 57.9667 |  83.7533 |  91.97   |  79.0533 |        |
| Std        |       |      |      |  8.21017 | 18.9181 |  37.7614 |  37.2892 |  16.3033 |        |
| Min        |       |      |      | 12       | -4      | -81.3    | -75.2    |   6.7    |        |
| Max        |       |      |      | 45       | 97      | 100      | 110.9    |  95.5    |        |

*Full data available in CSV/Excel files*
