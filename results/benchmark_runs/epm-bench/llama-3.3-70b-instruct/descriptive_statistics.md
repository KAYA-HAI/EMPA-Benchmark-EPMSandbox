# EPM-Q Evaluation Report

**Results**: `llama-3.3-70b-instruct_20251224_143751`

## 🏆 EPM-Q Scoreboard

### **EPM-Index: 38.55**
*(scientific baseline: 100.0)*

| Dimension (Weight) | Score | Details |
| :--- | :--- | :--- |
| **Outcome** (0.4) | **37.67** | RDI: 27.0 | E_tot: 10.0 | S_net: 76.0 |
| **Efficiency** (0.3) | **13.47** | Rho: 5.2 | S_proj: 5.0 | Tau: 30.1 |
| **Stability** (0.3) | **51.98** | R_pos: 48.2 | Align: 55.5 | Pen: 52.2 |

---

## 📊 Summary Statistics

### Overall Performance

- **Total cases**: 30
- **Success**: 1
- **Failure**: 29
- **Success rate**: 3.3%

### Successful Cases

- **Avg turns**: 20.0
- **Median turns**: 20.0
- **Fastest**: 20 turns
- **Slowest**: 20 turns
- **Avg net score**: 58.0
- **Avg net score/turn**: 2.9
- **Avg positive energy ratio**: 90.5%
- **Avg alignment**: 0.787
- **Avg penalty rate**: 0.19

### Failed Cases Analysis

- **Avg turns**: 28.1
- **Avg distance improvement**: -59.2%
- **Avg energy achievement**: -27.3%
- **Avg positive energy ratio**: 46.8%

**Failure type distribution**:

- Direction Collapse: 24 cases
- Timeout: 4 cases
- Stagnation: 1 cases

### By Dominant Axis

| Dominant Axis | Cases | Success Rate |
|-------|-------|-------|
| C | 10 | 0.0% |
| A | 10 | 0.0% |
| P | 10 | 10.0% |

### By Difficulty

| Difficulty | Cases | Success Rate |
|-----|-------|-------|
| Easy | 4 | 0.0% |
| Medium | 10 | 10.0% |
| Hard | 11 | 0.0% |
| Very Hard | 5 | 0.0% |

---

## 📋 Detailed Data Table

| Case_ID       | Dominant_Axis   | Difficulty   | Success   |      Turns |     Total_Net_Score |    Distance_Improvement% |    Energy_Achievement% |   Positive_Energy_Ratio% | Failure_Type   |
|:-----------|:------|:-----|:-----|--------:|--------:|----------:|----------:|---------:|:-------|
| script_003 | A     | Medium   | No    | 41      | 73      |  -37.6    |   32.1    |  61.9    | Direction Collapse   |
| script_010 | A     | Medium   | No    | 20      |  9      | -103.7    |  -81      |  33.3    | Direction Collapse   |
| script_011 | P     | Very Hard   | No    | 12      | -3      |  -73.3    |  -64      |   7.7    | Direction Collapse   |
| script_020 | A     | Easy   | No    | 18      | 32      |  -10.5    |   13.4    |  57.9    | Direction Collapse   |
| script_021 | C     | Easy   | No    | 23      | 14      | -146.3    |  -95.9    |  45.8    | Direction Collapse   |
| script_029 | C     | Easy   | No    | 17      | 18      |  -70.1    |  -33.4    |  50      | Direction Collapse   |
| script_042 | A     | Medium   | No    | 39      | 67      |  -35.7    |   22.8    |  65      | Direction Collapse   |
| script_059 | C     | Hard   | No    | 45      | 90      |   18.3    |   73.8    |  71.7    | Timeout     |
| script_063 | P     | Hard   | No    | 13      | 17      |   -5.5    |    2.3    |  42.9    | Direction Collapse   |
| script_081 | C     | Medium   | No    | 33      | 25      | -115.8    |  -68.1    |  41.2    | Direction Collapse   |
| script_095 | P     | Hard   | No    | 45      | 63      |  -86.9    |   -2.9    |  54.3    | Timeout     |
| script_128 | A     | Hard   | No    | 12      | -4      |  -69.1    |  -59.4    |  15.4    | Direction Collapse   |
| script_161 | C     | Medium   | No    | 24      | 33      |   22.8    |   27.7    |  60      | Stagnation   |
| script_195 | P     | Medium   | No    | 27      | 38      |  -22.4    |   11.1    |  60.7    | Direction Collapse   |
| script_215 | C     | Hard   | No    | 35      | 19      | -103.8    |  -87.8    |  36.1    | Direction Collapse   |
| script_222 | C     | Hard   | No    | 32      | 42      |  -38.3    |   -6.6    |  48.5    | Direction Collapse   |
| script_238 | A     | Hard   | No    | 27      | 33      |  -29.8    |  -22.7    |  50      | Direction Collapse   |
| script_243 | A     | Hard   | No    | 29      | 19      |  -89.1    |  -79      |  36.7    | Direction Collapse   |
| script_262 | P     | Medium   | No    | 22      |  7      | -104.4    |  -88      |  34.8    | Direction Collapse   |
| script_263 | P     | Medium   | No    | 45      | 42      | -178.2    |  -82.6    |  50      | Timeout     |
| script_269 | C     | Easy   | No    | 42      | 34      | -193.5    | -105.6    |  41.9    | Direction Collapse   |
| script_282 | A     | Hard   | No    | 12      |  1      |  -84.8    |  -73.7    |  15.4    | Direction Collapse   |
| script_288 | C     | Hard   | No    | 37      | 51      |  -30.3    |  -10.3    |  55.3    | Direction Collapse   |
| script_304 | P     | Medium   | Yes    | 20      | 58      |   90      |  101.7    |  90.5    | -      |
| script_327 | P     | Very Hard   | No    | 16      | 18      |  -23.4    |  -17.1    |  35.3    | Direction Collapse   |
| script_349 | P     | Very Hard   | No    | 23      | 31      |  -24.6    |  -14.5    |  41.7    | Direction Collapse   |
| script_355 | C     | Hard   | No    | 18      | 29      |    6.9    |   10.1    |  63.2    | Direction Collapse   |
| script_363 | P     | Very Hard   | No    | 37      | 67      |   -7.5    |   31.7    |  63.2    | Direction Collapse   |
| script_366 | A     | Medium   | No    | 26      | 45      |   -8.1    |   14.2    |  63      | Direction Collapse   |
| script_391 | A     | Very Hard   | No    | 45      | 55      |  -73.4    |  -38.4    |  54.3    | Timeout     |
| Mean        |       |      |      | 27.8333 | 34.1    |  -54.27   |  -23.0033 |  48.2567 |        |
| Std        |       |      |      | 11.1234 | 23.6896 |   61.0518 |   52.7631 |  17.4277 |        |
| Min        |       |      |      | 12      | -4      | -193.5    | -105.6    |   7.7    |        |
| Max        |       |      |      | 45      | 90      |   90      |  101.7    |  90.5    |        |

*Full data available in CSV/Excel files*
