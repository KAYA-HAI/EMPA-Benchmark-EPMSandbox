# EPM-Q Evaluation Report

**Results**: `deepseek-chat-v3-0324_20251224_141021`

## 🏆 EPM-Q Scoreboard

### **EPM-Index: 78.44**
*(scientific baseline: 100.0)*

| Dimension (Weight) | Score | Details |
| :--- | :--- | :--- |
| **Outcome** (0.4) | **94.26** | RDI: 84.3 | E_tot: 78.8 | S_net: 119.7 |
| **Efficiency** (0.3) | **57.44** | Rho: 58.4 | S_proj: 55.3 | Tau: 58.5 |
| **Stability** (0.3) | **73.12** | R_pos: 71.5 | Align: 73.8 | Pen: 74.0 |

---

## 📊 Summary Statistics

### Overall Performance

- **Total cases**: 30
- **Success**: 25
- **Failure**: 5
- **Success rate**: 83.3%

### Successful Cases

- **Avg turns**: 21.08
- **Median turns**: 19.0
- **Fastest**: 13 turns
- **Slowest**: 43 turns
- **Avg net score**: 58.52
- **Avg net score/turn**: 2.92
- **Avg positive energy ratio**: 76.8%
- **Avg alignment**: 0.57
- **Avg penalty rate**: 0.59

### Failed Cases Analysis

- **Avg turns**: 23.6
- **Avg distance improvement**: -24.6%
- **Avg energy achievement**: -16.6%
- **Avg positive energy ratio**: 45.4%

**Failure type distribution**:

- Direction Collapse: 3 cases
- Stagnation: 1 cases
- Timeout: 1 cases

### By Dominant Axis

| Dominant Axis | Cases | Success Rate |
|-------|-------|-------|
| C | 10 | 100.0% |
| A | 10 | 90.0% |
| P | 10 | 60.0% |

### By Difficulty

| Difficulty | Cases | Success Rate |
|-----|-------|-------|
| Easy | 4 | 100.0% |
| Medium | 10 | 80.0% |
| Hard | 11 | 90.9% |
| Very Hard | 5 | 60.0% |

---

## 📋 Detailed Data Table

| Case_ID       | Dominant_Axis   | Difficulty   | Success   |       Turns |     Total_Net_Score |   Distance_Improvement% |   Energy_Achievement% |   Positive_Energy_Ratio% | Failure_Type   |
|:-----------|:------|:-----|:-----|---------:|--------:|---------:|---------:|---------:|:-------|
| script_003 | A     | Medium   | Yes    | 17       | 50      |  100     | 106.8    |  72.2    | -      |
| script_010 | A     | Medium   | Yes    | 43       | 97      |   60.3   | 110.5    |  59.1    | -      |
| script_011 | P     | Very Hard   | No    | 30       | 19      |  -78.9   | -71.9    |  32.3    | Stagnation   |
| script_020 | A     | Easy   | Yes    | 14       | 40      |   90     | 101.7    |  86.7    | -      |
| script_021 | C     | Easy   | Yes    | 14       | 44      |   87     | 104.2    |  80      | -      |
| script_029 | C     | Easy   | Yes    | 15       | 44      |   95.5   | 100.4    |  68.8    | -      |
| script_042 | A     | Medium   | Yes    | 17       | 51      |   93.4   | 104.7    |  88.9    | -      |
| script_059 | C     | Hard   | Yes    | 15       | 52      |  100     | 103.1    |  87.5    | -      |
| script_063 | P     | Hard   | Yes    | 22       | 61      |  100     | 103.3    |  78.3    | -      |
| script_081 | C     | Medium   | Yes    | 23       | 60      |   93.1   | 103.3    |  70.8    | -      |
| script_095 | P     | Hard   | Yes    | 22       | 62      |   59.2   | 101.5    |  73.9    | -      |
| script_128 | A     | Hard   | No    | 12       | -2      |  -70.7   | -64.4    |  30.8    | Direction Collapse   |
| script_161 | C     | Medium   | Yes    | 28       | 61      |   66.3   | 100.1    |  75.9    | -      |
| script_195 | P     | Medium   | No    | 19       | 37      |   26.4   |  27.3    |  60      | Direction Collapse   |
| script_215 | C     | Hard   | Yes    | 27       | 68      |   86.9   | 104.1    |  67.9    | -      |
| script_222 | C     | Hard   | Yes    | 22       | 62      |   90.7   | 102.3    |  69.6    | -      |
| script_238 | A     | Hard   | Yes    | 22       | 63      |  100     | 103.9    |  73.9    | -      |
| script_243 | A     | Hard   | Yes    | 35       | 77      |   75     | 102.1    |  61.1    | -      |
| script_262 | P     | Medium   | No    | 45       | 70      |   30.5   |  52.3    |  65.2    | Timeout     |
| script_263 | P     | Medium   | Yes    | 19       | 54      |  100     | 113.2    |  80      | -      |
| script_269 | C     | Easy   | Yes    | 35       | 71      |   67.8   | 105      |  66.7    | -      |
| script_282 | A     | Hard   | Yes    | 19       | 56      |   90.4   | 103.7    |  75      | -      |
| script_288 | C     | Hard   | Yes    | 17       | 55      |   97.1   | 103.1    |  83.3    | -      |
| script_304 | P     | Medium   | Yes    | 18       | 54      |   85.8   | 100.9    |  78.9    | -      |
| script_327 | P     | Very Hard   | No    | 12       | 11      |  -30.1   | -26.3    |  38.5    | Direction Collapse   |
| script_349 | P     | Very Hard   | Yes    | 19       | 63      |   88.8   | 103.5    |  80      | -      |
| script_355 | C     | Hard   | Yes    | 14       | 51      |   97     | 101.8    |  93.3    | -      |
| script_363 | P     | Very Hard   | Yes    | 23       | 62      |   65.9   | 102.1    |  75      | -      |
| script_366 | A     | Medium   | Yes    | 14       | 50      |   93.3   | 104.8    |  86.7    | -      |
| script_391 | A     | Very Hard   | Yes    | 13       | 55      |  100     | 109.2    |  85.7    | -      |
| Mean        |       |      |      | 21.5     | 53.2667 |   68.69  |  83.8767 |  71.5333 |        |
| Std        |       |      |      |  8.68907 | 19.0696 |   48.148 |  50.1432 |  15.5074 |        |
| Min        |       |      |      | 12       | -2      |  -78.9   | -71.9    |  30.8    |        |
| Max        |       |      |      | 45       | 97      |  100     | 113.2    |  93.3    |        |

*Full data available in CSV/Excel files*
