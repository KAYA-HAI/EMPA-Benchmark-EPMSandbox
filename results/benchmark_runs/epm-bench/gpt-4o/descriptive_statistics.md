# EPM-Q Evaluation Report

**Results**: `gpt-4o_20251224_133845`

## 🏆 EPM-Q Scoreboard

### **EPM-Index: 33.73**
*(scientific baseline: 100.0)*

| Dimension (Weight) | Score | Details |
| :--- | :--- | :--- |
| **Outcome** (0.4) | **31.44** | RDI: 18.7 | E_tot: 14.3 | S_net: 61.4 |
| **Efficiency** (0.3) | **23.16** | Rho: 5.7 | S_proj: 5.5 | Tau: 58.4 |
| **Stability** (0.3) | **41.30** | R_pos: 38.2 | Align: 47.0 | Pen: 38.7 |

---

## 📊 Summary Statistics

### Overall Performance

- **Total cases**: 30
- **Success**: 4
- **Failure**: 26
- **Success rate**: 13.3%

### Successful Cases

- **Avg turns**: 29.75
- **Median turns**: 27.0
- **Fastest**: 24 turns
- **Slowest**: 41 turns
- **Avg net score**: 67.25
- **Avg net score/turn**: 2.28
- **Avg positive energy ratio**: 76.6%
- **Avg alignment**: 0.593
- **Avg penalty rate**: 0.62

### Failed Cases Analysis

- **Avg turns**: 22.31
- **Avg distance improvement**: -91.5%
- **Avg energy achievement**: -60.1%
- **Avg positive energy ratio**: 32.3%

**Failure type distribution**:

- Direction Collapse: 24 cases
- Timeout: 2 cases

### By Dominant Axis

| Dominant Axis | Cases | Success Rate |
|-------|-------|-------|
| C | 10 | 20.0% |
| A | 10 | 10.0% |
| P | 10 | 10.0% |

### By Difficulty

| Difficulty | Cases | Success Rate |
|-----|-------|-------|
| Easy | 4 | 50.0% |
| Medium | 10 | 20.0% |
| Hard | 11 | 0.0% |
| Very Hard | 5 | 0.0% |

---

## 📋 Detailed Data Table

| Case_ID       | Dominant_Axis   | Difficulty   | Success   |      Turns |      Total_Net_Score |    Distance_Improvement% |    Energy_Achievement% |   Positive_Energy_Ratio% | Failure_Type   |
|:-----------|:------|:-----|:-----|--------:|---------:|----------:|----------:|---------:|:-------|
| script_003 | A     | Medium   | No    | 17      |   2      | -158.9    | -119.7    |  22.2    | Direction Collapse   |
| script_010 | A     | Medium   | No    | 22      |   8      | -106.1    |  -88.3    |  34.8    | Direction Collapse   |
| script_011 | P     | Very Hard   | No    | 12      | -10      |  -94.4    |  -84.7    |   7.7    | Direction Collapse   |
| script_020 | A     | Easy   | No    | 45      |  78      |  -74.8    |   17.9    |  67.4    | Timeout     |
| script_021 | C     | Easy   | Yes    | 24      |  58      |   69.7    |  101.5    |  76      | -      |
| script_029 | C     | Easy   | Yes    | 29      |  66      |   63.9    |  104.1    |  73.3    | -      |
| script_042 | A     | Medium   | Yes    | 41      |  88      |   73.5    |  101.3    |  76.2    | -      |
| script_059 | C     | Hard   | No    | 32      |  42      | -105      |  -35.2    |  45.5    | Direction Collapse   |
| script_063 | P     | Hard   | No    | 12      |  -6      |  -93.6    |  -81.3    |  15.4    | Direction Collapse   |
| script_081 | C     | Medium   | No    | 36      |  27      | -144.8    |  -71.5    |  37.8    | Direction Collapse   |
| script_095 | P     | Hard   | No    | 28      |  23      |  -55.2    |  -39.9    |  48.3    | Direction Collapse   |
| script_128 | A     | Hard   | No    | 12      |  -8      | -101.4    |  -89      |   7.7    | Direction Collapse   |
| script_161 | C     | Medium   | No    | 31      |  26      | -122.4    |  -57.2    |  43.8    | Direction Collapse   |
| script_195 | P     | Medium   | No    | 26      |  26      |  -91.4    |  -51.6    |  44.4    | Direction Collapse   |
| script_215 | C     | Hard   | No    | 20      |  -9      | -154.5    | -128.1    |  14.3    | Direction Collapse   |
| script_222 | C     | Hard   | No    | 38      |  32      |  -73.1    |  -51.4    |  38.5    | Direction Collapse   |
| script_238 | A     | Hard   | No    | 19      |  15      |  -76.2    |  -48.1    |  40      | Direction Collapse   |
| script_243 | A     | Hard   | No    | 17      |  -9      | -136.3    | -116.5    |  16.7    | Direction Collapse   |
| script_262 | P     | Medium   | No    | 45      |  80      |  -11.7    |   55.8    |  63      | Timeout     |
| script_263 | P     | Medium   | Yes    | 25      |  57      |   61.7    |  100.4    |  80.8    | -      |
| script_269 | C     | Easy   | No    | 22      |  24      |  -85.1    |  -48.3    |  43.5    | Direction Collapse   |
| script_282 | A     | Hard   | No    | 13      |   4      |  -75.1    |  -65      |  14.3    | Direction Collapse   |
| script_288 | C     | Hard   | No    | 15      |   4      |  -85.1    |  -66.8    |  18.8    | Direction Collapse   |
| script_304 | P     | Medium   | No    | 28      |  36      |  -92.7    |  -41.5    |  44.8    | Direction Collapse   |
| script_327 | P     | Very Hard   | No    | 12      |  -2      |  -70.7    |  -63.6    |  23.1    | Direction Collapse   |
| script_349 | P     | Very Hard   | No    | 12      |  -2      |  -77.7    |  -67.3    |  23.1    | Direction Collapse   |
| script_355 | C     | Hard   | No    | 19      |  11      |  -83.7    |  -66.2    |  35      | Direction Collapse   |
| script_363 | P     | Very Hard   | No    | 12      |   2      |  -70.7    |  -54      |  23.1    | Direction Collapse   |
| script_366 | A     | Medium   | No    | 12      |   8      |  -70.3    |  -54.6    |  38.5    | Direction Collapse   |
| script_391 | A     | Very Hard   | No    | 23      |  17      |  -67.3    |  -46.3    |  29.2    | Direction Collapse   |
| Mean        |       |      |      | 23.3    |  22.9333 |  -70.3133 |  -38.5033 |  38.24   |        |
| Std        |       |      |      | 10.2626 |  28.6849 |   62.4846 |   66.1306 |  21.2471 |        |
| Min        |       |      |      | 12      | -10      | -158.9    | -128.1    |   7.7    |        |
| Max        |       |      |      | 45      |  88      |   73.5    |  104.1    |  80.8    |        |

*Full data available in CSV/Excel files*
