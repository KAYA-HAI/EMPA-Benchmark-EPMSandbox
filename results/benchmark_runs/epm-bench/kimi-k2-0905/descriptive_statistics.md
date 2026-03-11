# EPM-Q Evaluation Report

**Results**: `kimi-k2-0905_resampled`

## 🏆 EPM-Q Scoreboard

### **EPM-Index: 86.20**
*(scientific baseline: 100.0)*

| Dimension (Weight) | Score | Details |
| :--- | :--- | :--- |
| **Outcome** (0.4) | **99.04** | RDI: 87.3 | E_tot: 86.6 | S_net: 123.2 |
| **Efficiency** (0.3) | **70.34** | Rho: 72.6 | S_proj: 68.3 | Tau: 70.2 |
| **Stability** (0.3) | **81.29** | R_pos: 80.1 | Align: 81.6 | Pen: 82.1 |

---

## 📊 Summary Statistics

### Overall Performance

- **Total cases**: 30
- **Success**: 27
- **Failure**: 3
- **Success rate**: 90.0%

### Successful Cases

- **Avg turns**: 17.89
- **Median turns**: 16.0
- **Fastest**: 12 turns
- **Slowest**: 33 turns
- **Avg net score**: 55.48
- **Avg net score/turn**: 3.21
- **Avg positive energy ratio**: 83.6%
- **Avg alignment**: 0.696
- **Avg penalty rate**: 0.4

### Failed Cases Analysis

- **Avg turns**: 40.67
- **Avg distance improvement**: -81.2%
- **Avg energy achievement**: -23.5%
- **Avg positive energy ratio**: 49.0%

**Failure type distribution**:

- Timeout: 2 cases
- Direction Collapse: 1 cases

### By Dominant Axis

| Dominant Axis | Cases | Success Rate |
|-------|-------|-------|
| C | 10 | 100.0% |
| A | 10 | 90.0% |
| P | 10 | 80.0% |

### By Difficulty

| Difficulty | Cases | Success Rate |
|-----|-------|-------|
| Easy | 4 | 100.0% |
| Medium | 10 | 100.0% |
| Hard | 11 | 90.9% |
| Very Hard | 5 | 60.0% |

---

## 📋 Detailed Data Table

| Case_ID       | Dominant_Axis   | Difficulty   | Success   |      Turns |      Total_Net_Score |    Distance_Improvement% |    Energy_Achievement% |   Positive_Energy_Ratio% | Failure_Type   |
|:-----------|:------|:-----|:-----|--------:|---------:|----------:|----------:|---------:|:-------|
| script_003 | A     | Medium   | Yes    | 12      |  47      |  100      |  122.5    |  92.3    | -      |
| script_010 | A     | Medium   | Yes    | 23      |  63      |   86.8    |  102.1    |  79.2    | -      |
| script_011 | P     | Very Hard   | No    | 32      |  14      | -156.1    | -119      |  27.3    | Direction Collapse   |
| script_020 | A     | Easy   | Yes    | 12      |  39      |  100      |  115.5    |  92.3    | -      |
| script_021 | C     | Easy   | Yes    | 12      |  44      |   95.7    |  117.9    |  92.3    | -      |
| script_029 | C     | Easy   | Yes    | 17      |  46      |   81.9    |  103.4    |  83.3    | -      |
| script_042 | A     | Medium   | Yes    | 23      |  65      |   80.2    |  101.9    |  75      | -      |
| script_059 | C     | Hard   | Yes    | 26      |  71      |   56      |  104.6    |  70.4    | -      |
| script_063 | P     | Hard   | Yes    | 23      |  63      |   87.1    |  100.8    |  70.8    | -      |
| script_081 | C     | Medium   | Yes    | 18      |  52      |   86.2    |  100.1    |  73.7    | -      |
| script_095 | P     | Hard   | Yes    | 33      |  84      |   30      |  106.1    |  67.6    | -      |
| script_128 | A     | Hard   | No    | 45      |  63      | -122.3    |  -45.7    |  50      | Timeout     |
| script_161 | C     | Medium   | Yes    | 24      |  62      |   92.5    |  106.1    |  80      | -      |
| script_195 | P     | Medium   | Yes    | 13      |  48      |  100      |  105.3    |  92.9    | -      |
| script_215 | C     | Hard   | Yes    | 15      |  50      |  100      |  101.7    |  93.8    | -      |
| script_222 | C     | Hard   | Yes    | 27      |  68      |   70.7    |  101.4    |  67.9    | -      |
| script_238 | A     | Hard   | Yes    | 13      |  50      |   94.2    |  101.3    |  92.9    | -      |
| script_243 | A     | Hard   | Yes    | 16      |  56      |   93.8    |  109.8    |  88.2    | -      |
| script_262 | P     | Medium   | Yes    | 14      |  44      |  100      |  104.3    |  93.3    | -      |
| script_263 | P     | Medium   | Yes    | 16      |  48      |  100      |  106.2    |  88.2    | -      |
| script_269 | C     | Easy   | Yes    | 16      |  49      |  100      |  106.2    |  82.4    | -      |
| script_282 | A     | Hard   | Yes    | 15      |  53      |   87.2    |  102.1    |  87.5    | -      |
| script_288 | C     | Hard   | Yes    | 16      |  56      |   94.1    |  101.5    |  88.2    | -      |
| script_304 | P     | Medium   | Yes    | 15      |  52      |  100      |  105.7    |  81.2    | -      |
| script_327 | P     | Very Hard   | Yes    | 18      |  61      |  100      |  104.8    |  73.7    | -      |
| script_349 | P     | Very Hard   | No    | 45      | 102      |   34.7    |   94.1    |  69.6    | Timeout     |
| script_355 | C     | Hard   | Yes    | 17      |  56      |   90.4    |  104.8    |  88.9    | -      |
| script_363 | P     | Very Hard   | Yes    | 20      |  64      |   97.2    |  104.5    |  85.7    | -      |
| script_366 | A     | Medium   | Yes    | 16      |  53      |   86.6    |  105.1    |  82.4    | -      |
| script_391 | A     | Very Hard   | Yes    | 13      |  54      |   94.5    |  106.5    |  92.9    | -      |
| Mean        |       |      |      | 20.1667 |  55.9    |   72.0467 |   92.72   |  80.13   |        |
| Std        |       |      |      |  8.8008 |  14.9097 |   60.2945 |   48.8548 |  14.4805 |        |
| Min        |       |      |      | 12      |  14      | -156.1    | -119      |  27.3    |        |
| Max        |       |      |      | 45      | 102      |  100      |  122.5    |  93.8    |        |

*Full data available in CSV/Excel files*
