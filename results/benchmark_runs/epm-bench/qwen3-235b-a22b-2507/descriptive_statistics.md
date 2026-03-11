# EPM-Q Evaluation Report

**Results**: `qwen3-235b-a22b-2507_resampled`

## 🏆 EPM-Q Scoreboard

### **EPM-Index: 89.58**
*(scientific baseline: 100.0)*

| Dimension (Weight) | Score | Details |
| :--- | :--- | :--- |
| **Outcome** (0.4) | **101.65** | RDI: 92.0 | E_tot: 91.7 | S_net: 121.3 |
| **Efficiency** (0.3) | **81.63** | Rho: 88.3 | S_proj: 82.5 | Tau: 74.0 |
| **Stability** (0.3) | **81.49** | R_pos: 80.1 | Align: 82.0 | Pen: 82.3 |

---

## 📊 Summary Statistics

### Overall Performance

- **Total cases**: 30
- **Success**: 29
- **Failure**: 1
- **Success rate**: 96.7%

### Successful Cases

- **Avg turns**: 16.34
- **Median turns**: 15.0
- **Fastest**: 12 turns
- **Slowest**: 37 turns
- **Avg net score**: 54.34
- **Avg net score/turn**: 3.48
- **Avg positive energy ratio**: 81.5%
- **Avg alignment**: 0.666
- **Avg penalty rate**: 0.47

### Failed Cases Analysis

- **Avg turns**: 45.0
- **Avg distance improvement**: -121.1%
- **Avg energy achievement**: -60.6%
- **Avg positive energy ratio**: 41.3%

**Failure type distribution**:

- Timeout: 1 cases

### By Dominant Axis

| Dominant Axis | Cases | Success Rate |
|-------|-------|-------|
| C | 10 | 100.0% |
| A | 10 | 100.0% |
| P | 10 | 90.0% |

### By Difficulty

| Difficulty | Cases | Success Rate |
|-----|-------|-------|
| Easy | 4 | 100.0% |
| Medium | 10 | 100.0% |
| Hard | 11 | 100.0% |
| Very Hard | 5 | 80.0% |

---

## 📋 Detailed Data Table

| Case_ID       | Dominant_Axis   | Difficulty   | Success   |       Turns |     Total_Net_Score |    Distance_Improvement% |   Energy_Achievement% |   Positive_Energy_Ratio% | Failure_Type   |
|:-----------|:------|:-----|:-----|---------:|--------:|----------:|---------:|---------:|:-------|
| script_003 | A     | Medium   | Yes    | 12       | 49      |  100      | 127.4    |  84.6    | -      |
| script_010 | A     | Medium   | Yes    | 12       | 48      |  100      | 108.3    |  84.6    | -      |
| script_011 | P     | Very Hard   | No    | 45       | 56      | -121.1    | -60.6    |  41.3    | Timeout     |
| script_020 | A     | Easy   | Yes    | 16       | 46      |   65      | 101.3    |  76.5    | -      |
| script_021 | C     | Easy   | Yes    | 21       | 57      |   74      | 108.3    |  72.7    | -      |
| script_029 | C     | Easy   | Yes    | 17       | 50      |  100      | 115.5    |  77.8    | -      |
| script_042 | A     | Medium   | Yes    | 12       | 47      |  100      | 109.5    |  84.6    | -      |
| script_059 | C     | Hard   | Yes    | 15       | 51      |  100      | 101.5    |  87.5    | -      |
| script_063 | P     | Hard   | Yes    | 18       | 59      |   93.7    | 104.4    |  68.4    | -      |
| script_081 | C     | Medium   | Yes    | 17       | 52      |  100      | 100.7    |  72.2    | -      |
| script_095 | P     | Hard   | Yes    | 16       | 57      |   65      | 103.4    |  82.4    | -      |
| script_128 | A     | Hard   | Yes    | 16       | 58      |  100      | 114.6    |  76.5    | -      |
| script_161 | C     | Medium   | Yes    | 37       | 83      |   58.8    | 104.7    |  71.1    | -      |
| script_195 | P     | Medium   | Yes    | 13       | 48      |   93.3    | 105.1    |  92.9    | -      |
| script_215 | C     | Hard   | Yes    | 14       | 51      |   90.2    | 104      |  80      | -      |
| script_222 | C     | Hard   | Yes    | 12       | 55      |  100      | 126.5    |  92.3    | -      |
| script_238 | A     | Hard   | Yes    | 13       | 51      |   88.3    | 105.3    |  85.7    | -      |
| script_243 | A     | Hard   | Yes    | 13       | 50      |   87.5    | 106.1    |  85.7    | -      |
| script_262 | P     | Medium   | Yes    | 29       | 70      |   50.2    | 104.7    |  63.3    | -      |
| script_263 | P     | Medium   | Yes    | 12       | 45      |  100      | 118.2    |  92.3    | -      |
| script_269 | C     | Easy   | Yes    | 15       | 46      |  100      | 102.3    |  75      | -      |
| script_282 | A     | Hard   | Yes    | 13       | 48      |   96.8    | 101.6    |  92.9    | -      |
| script_288 | C     | Hard   | Yes    | 16       | 55      |   97.1    | 101.8    |  88.2    | -      |
| script_304 | P     | Medium   | Yes    | 14       | 51      |   96.7    | 106.5    |  86.7    | -      |
| script_327 | P     | Very Hard   | Yes    | 16       | 57      |   94.3    | 103.1    |  76.5    | -      |
| script_349 | P     | Very Hard   | Yes    | 22       | 69      |   83.7    | 103.4    |  73.9    | -      |
| script_355 | C     | Hard   | Yes    | 23       | 64      |   87.9    | 102      |  66.7    | -      |
| script_363 | P     | Very Hard   | Yes    | 14       | 56      |  100      | 110.7    |  93.3    | -      |
| script_366 | A     | Medium   | Yes    | 12       | 49      |  100      | 118.9    |  92.3    | -      |
| script_391 | A     | Very Hard   | Yes    | 14       | 54      |   94.5    | 100.3    |  86.7    | -      |
| Mean        |       |      |      | 17.3     | 54.4    |   83.1967 | 101.983  |  80.1533 |        |
| Std        |       |      |      |  7.58015 |  8.2696 |   40.9778 |  31.5557 |  11.2886 |        |
| Min        |       |      |      | 12       | 45      | -121.1    | -60.6    |  41.3    |        |
| Max        |       |      |      | 45       | 83      |  100      | 127.4    |  93.3    |        |

*Full data available in CSV/Excel files*
