# EPM-Q Evaluation Report

**Results**: `seed-1.6_20251225_161259`

## 🏆 EPM-Q Scoreboard

### **EPM-Index: 43.12**
*(scientific baseline: 100.0)*

| Dimension (Weight) | Score | Details |
| :--- | :--- | :--- |
| **Outcome** (0.4) | **41.50** | RDI: 28.3 | E_tot: 21.6 | S_net: 74.6 |
| **Efficiency** (0.3) | **20.95** | Rho: 8.4 | S_proj: 8.1 | Tau: 46.4 |
| **Stability** (0.3) | **55.82** | R_pos: 48.4 | Align: 57.5 | Pen: 61.6 |

---

## 📊 Summary Statistics

### Overall Performance

- **Total cases**: 30
- **Success**: 2
- **Failure**: 28
- **Success rate**: 6.7%

### Successful Cases

- **Avg turns**: 23.5
- **Median turns**: 23.5
- **Fastest**: 21 turns
- **Slowest**: 26 turns
- **Avg net score**: 53.0
- **Avg net score/turn**: 2.26
- **Avg positive energy ratio**: 83.5%
- **Avg alignment**: 0.702
- **Avg penalty rate**: 0.23

### Failed Cases Analysis

- **Avg turns**: 28.79
- **Avg distance improvement**: -59.2%
- **Avg energy achievement**: -15.0%
- **Avg positive energy ratio**: 45.9%

**Failure type distribution**:

- Direction Collapse: 17 cases
- Timeout: 10 cases
- Stagnation: 1 cases

### By Dominant Axis

| Dominant Axis | Cases | Success Rate |
|-------|-------|-------|
| C | 10 | 10.0% |
| A | 10 | 10.0% |
| P | 10 | 0.0% |

### By Difficulty

| Difficulty | Cases | Success Rate |
|-----|-------|-------|
| Easy | 4 | 25.0% |
| Medium | 10 | 10.0% |
| Hard | 11 | 0.0% |
| Very Hard | 5 | 0.0% |

---

## 📋 Detailed Data Table

| Case_ID       | Dominant_Axis   | Difficulty   | Success   |      Turns |      Total_Net_Score |    Distance_Improvement% |     Energy_Achievement% |   Positive_Energy_Ratio% | Failure_Type   |
|:-----------|:------|:-----|:-----|--------:|---------:|----------:|-----------:|---------:|:-------|
| script_003 | A     | Medium   | No    | 18      |  19      |  -30.5    |  -11.6     |  52.6    | Direction Collapse   |
| script_010 | A     | Medium   | No    | 45      |  67      |    8.3    |   49.1     |  65.2    | Timeout     |
| script_011 | P     | Very Hard   | No    | 12      |   0      |  -65.8    |  -50.4     |  15.4    | Direction Collapse   |
| script_020 | A     | Easy   | No    | 45      |  71      |  -59.8    |   30.4     |  65.2    | Timeout     |
| script_021 | C     | Easy   | No    | 18      |  19      |  -46.8    |  -12.9     |  52.6    | Direction Collapse   |
| script_029 | C     | Easy   | Yes    | 21      |  49      |   91      |  103       |  81.8    | -      |
| script_042 | A     | Medium   | Yes    | 26      |  57      |   76.8    |  103.3     |  85.2    | -      |
| script_059 | C     | Hard   | No    | 45      |  87      |   37.2    |   97.4     |  76.1    | Timeout     |
| script_063 | P     | Hard   | No    | 13      | -16      | -122.6    |  -95.3     |  14.3    | Direction Collapse   |
| script_081 | C     | Medium   | No    | 22      |   8      | -101.4    |  -59.8     |  34.8    | Direction Collapse   |
| script_095 | P     | Hard   | No    | 45      |  32      |  -85.2    |  -36.1     |  60.9    | Timeout     |
| script_128 | A     | Hard   | No    | 23      |  -2      | -134.5    | -109.3     |  33.3    | Direction Collapse   |
| script_161 | C     | Medium   | No    | 41      |  36      | -154.3    |  -24.3     |  42.9    | Direction Collapse   |
| script_195 | P     | Medium   | No    | 24      |  24      |  -84.2    |  -24.4     |  44      | Direction Collapse   |
| script_215 | C     | Hard   | No    | 12      |  12      |  -16.4    |   -4.2     |  46.2    | Direction Collapse   |
| script_222 | C     | Hard   | No    | 45      |  37      |  -96.1    |  -42.9     |  58.7    | Timeout     |
| script_238 | A     | Hard   | No    | 23      |  12      |  -81.7    |  -58.3     |  37.5    | Direction Collapse   |
| script_243 | A     | Hard   | No    | 21      |  12      |  -71.4    |  -52.5     |  40.9    | Direction Collapse   |
| script_262 | P     | Medium   | No    | 45      |  75      |   23.4    |   85.7     |  71.7    | Timeout     |
| script_263 | P     | Medium   | No    | 16      |   4      | -100.6    |  -57       |  29.4    | Direction Collapse   |
| script_269 | C     | Easy   | No    | 45      |  73      |  -44.9    |   68.6     |  65.2    | Timeout     |
| script_282 | A     | Hard   | No    | 34      |  46      |   45.8    |   44.6     |  65.7    | Stagnation   |
| script_288 | C     | Hard   | No    | 31      |  30      |  -36.4    |  -10.6     |  53.1    | Direction Collapse   |
| script_304 | P     | Medium   | No    | 12      |   1      |  -95.3    |  -54.2     |   7.7    | Direction Collapse   |
| script_327 | P     | Very Hard   | No    | 12      |   3      |  -50.1    |  -32.4     |  23.1    | Direction Collapse   |
| script_349 | P     | Very Hard   | No    | 45      |  31      | -174.9    |  -80.1     |  41.3    | Timeout     |
| script_355 | C     | Hard   | No    | 12      |  -4      |  -87.8    |  -63.1     |  23.1    | Direction Collapse   |
| script_363 | P     | Very Hard   | No    | 45      |  82      |   17.7    |   72.6     |  73.9    | Timeout     |
| script_366 | A     | Medium   | No    | 12      |   2      |  -88.7    |  -66.3     |  23.1    | Direction Collapse   |
| script_391 | A     | Very Hard   | No    | 45      |  78      |   39.6    |   77.2     |  67.4    | Timeout     |
| Mean        |       |      |      | 28.4333 |  31.5    |  -49.6533 |   -7.12667 |  48.41   |        |
| Std        |       |      |      | 13.6551 |  30.2344 |   67.2818 |   63.7717  |  21.2857 |        |
| Min        |       |      |      | 12      | -16      | -174.9    | -109.3     |   7.7    |        |
| Max        |       |      |      | 45      |  87      |   91      |  103.3     |  85.2    |        |

*Full data available in CSV/Excel files*
