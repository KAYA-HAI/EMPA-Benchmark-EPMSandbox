# EPM-Q Evaluation Report

**Results**: `doubao-1.5-character_resampled`

## 🏆 EPM-Q Scoreboard

### **EPM-Index: 30.24**
*(scientific baseline: 100.0)*

| Dimension (Weight) | Score | Details |
| :--- | :--- | :--- |
| **Outcome** (0.4) | **27.44** | RDI: 23.8 | E_tot: 12.3 | S_net: 46.3 |
| **Efficiency** (0.3) | **19.36** | Rho: 5.2 | S_proj: 5.0 | Tau: 47.9 |
| **Stability** (0.3) | **38.49** | R_pos: 36.5 | Align: 41.1 | Pen: 37.8 |

---

## 📊 Summary Statistics

### Overall Performance

- **Total cases**: 30
- **Success**: 4
- **Failure**: 26
- **Success rate**: 13.3%

### Successful Cases

- **Avg turns**: 30.25
- **Median turns**: 30.5
- **Fastest**: 23 turns
- **Slowest**: 37 turns
- **Avg net score**: 65.25
- **Avg net score/turn**: 2.17
- **Avg positive energy ratio**: 77.5%
- **Avg alignment**: 0.571
- **Avg penalty rate**: 0.6

### Failed Cases Analysis

- **Avg turns**: 24.62
- **Avg distance improvement**: -91.8%
- **Avg energy achievement**: -81.5%
- **Avg positive energy ratio**: 30.2%

**Failure type distribution**:

- Direction Collapse: 18 cases
- Stagnation: 5 cases
- Timeout: 3 cases

### By Dominant Axis

| Dominant Axis | Cases | Success Rate |
|-------|-------|-------|
| C | 10 | 40.0% |
| A | 10 | 0.0% |
| P | 10 | 0.0% |

### By Difficulty

| Difficulty | Cases | Success Rate |
|-----|-------|-------|
| Easy | 4 | 50.0% |
| Medium | 10 | 10.0% |
| Hard | 11 | 9.1% |
| Very Hard | 5 | 0.0% |

---

## 📋 Detailed Data Table

| Case_ID       | Dominant_Axis   | Difficulty   | Success   |      Turns |      Total_Net_Score |    Distance_Improvement% |    Energy_Achievement% |   Positive_Energy_Ratio% | Failure_Type   |
|:-----------|:------|:-----|:-----|--------:|---------:|----------:|----------:|---------:|:-------|
| script_003 | A     | Medium   | No    | 14      |   9      |  -39.5    |  -36.9    |  33.3    | Direction Collapse   |
| script_010 | A     | Medium   | No    | 12      |  -2      |  -58.5    |  -54.2    |  15.4    | Direction Collapse   |
| script_011 | P     | Very Hard   | No    | 12      | -19      | -104.5    |  -99.1    |   0      | Direction Collapse   |
| script_020 | A     | Easy   | No    | 45      |  56      |  -20.3    |   -7.2    |  58.7    | Timeout     |
| script_021 | C     | Easy   | Yes    | 37      |  72      |   86.3    |  100.2    |  73.7    | -      |
| script_029 | C     | Easy   | Yes    | 23      |  53      |   81.9    |  101.6    |  75      | -      |
| script_042 | A     | Medium   | No    | 39      |   7      | -148.1    | -139.9    |  42.5    | Stagnation   |
| script_059 | C     | Hard   | Yes    | 32      |  75      |   90.6    |  103.6    |  87.9    | -      |
| script_063 | P     | Hard   | No    | 12      | -21      | -115.1    | -107.9    |   0      | Direction Collapse   |
| script_081 | C     | Medium   | No    | 32      | -10      | -161.9    | -148.2    |  30.3    | Direction Collapse   |
| script_095 | P     | Hard   | No    | 35      | -10      | -185      | -152.8    |  30.6    | Direction Collapse   |
| script_128 | A     | Hard   | No    | 12      | -25      | -127.1    | -120.2    |   0      | Direction Collapse   |
| script_161 | C     | Medium   | Yes    | 29      |  61      |   25.1    |  105.8    |  73.3    | -      |
| script_195 | P     | Medium   | No    | 45      |  38      | -115.5    |  -78.9    |  45.7    | Timeout     |
| script_215 | C     | Hard   | No    | 15      | -28      | -170.3    | -155.8    |   6.2    | Direction Collapse   |
| script_222 | C     | Hard   | No    | 31      |  24      |  -39.4    |  -35.9    |  50      | Stagnation   |
| script_238 | A     | Hard   | No    | 15      |   3      |  -75.5    |  -65.2    |  18.8    | Direction Collapse   |
| script_243 | A     | Hard   | No    | 12      |   4      |  -47.6    |  -42.5    |  30.8    | Direction Collapse   |
| script_262 | P     | Medium   | No    | 12      |   4      |  -59.2    |  -51.5    |  23.1    | Direction Collapse   |
| script_263 | P     | Medium   | No    | 17      |  21      |    1.1    |    2.3    |  55.6    | Stagnation   |
| script_269 | C     | Easy   | No    | 33      |  37      |  -33.4    |  -15.2    |  50      | Direction Collapse   |
| script_282 | A     | Hard   | No    | 45      |  -1      | -207.9    | -196.3    |  32.6    | Timeout     |
| script_288 | C     | Hard   | No    | 40      |  48      |   -3.8    |    1.1    |  51.2    | Stagnation   |
| script_304 | P     | Medium   | No    | 28      |  15      |  -87.5    |  -70.1    |  44.8    | Direction Collapse   |
| script_327 | P     | Very Hard   | No    | 17      |  -2      |  -70.8    |  -65.5    |  22.2    | Direction Collapse   |
| script_349 | P     | Very Hard   | No    | 12      | -11      |  -78.8    |  -73.5    |  23.1    | Direction Collapse   |
| script_355 | C     | Hard   | No    | 24      |  -5      | -121      | -109.9    |  28      | Direction Collapse   |
| script_363 | P     | Very Hard   | No    | 16      |   3      |  -44.8    |  -41.9    |  35.3    | Direction Collapse   |
| script_366 | A     | Medium   | No    | 41      |  19      | -143.6    | -134.5    |  38.1    | Stagnation   |
| script_391 | A     | Very Hard   | No    | 24      | -19      | -127.8    | -120.2    |  20      | Direction Collapse   |
| Mean        |       |      |      | 25.3667 |  13.2    |  -70.0633 |  -56.9567 |  36.54   |        |
| Std        |       |      |      | 11.8307 |  29.4049 |   77.9067 |   81.0193 |  22.8991 |        |
| Min        |       |      |      | 12      | -28      | -207.9    | -196.3    |   0      |        |
| Max        |       |      |      | 45      |  75      |   90.6    |  105.8    |  87.9    |        |

*Full data available in CSV/Excel files*
