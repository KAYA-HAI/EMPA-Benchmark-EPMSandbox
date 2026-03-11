# EPM-Q Evaluation Report

**Results**: `gemini-3-pro-preview_20251225_163236`

## 🏆 EPM-Q Scoreboard

### **EPM-Index: 99.77**
*(scientific baseline: 100.0)*

| Dimension (Weight) | Score | Details |
| :--- | :--- | :--- |
| **Outcome** (0.4) | **104.10** | RDI: 98.1 | E_tot: 100.3 | S_net: 113.9 |
| **Efficiency** (0.3) | **103.50** | Rho: 111.4 | S_proj: 103.4 | Tau: 95.8 |
| **Stability** (0.3) | **93.58** | R_pos: 90.7 | Align: 92.2 | Pen: 97.8 |

---

## 📊 Summary Statistics

### Overall Performance

- **Total cases**: 30
- **Success**: 30
- **Failure**: 0
- **Success rate**: 100.0%

### Successful Cases

- **Avg turns**: 13.33
- **Median turns**: 12.0
- **Fastest**: 12 turns
- **Slowest**: 20 turns
- **Avg net score**: 51.43
- **Avg net score/turn**: 3.9
- **Avg positive energy ratio**: 90.7%
- **Avg alignment**: 0.844
- **Avg penalty rate**: 0.06

### By Dominant Axis

| Dominant Axis | Cases | Success Rate |
|-------|-------|-------|
| C | 10 | 100.0% |
| A | 10 | 100.0% |
| P | 10 | 100.0% |

### By Difficulty

| Difficulty | Cases | Success Rate |
|-----|-------|-------|
| Easy | 4 | 100.0% |
| Medium | 10 | 100.0% |
| Hard | 11 | 100.0% |
| Very Hard | 5 | 100.0% |

---

## 📋 Detailed Data Table

| Case_ID       | Dominant_Axis   | Difficulty   | Success   |       Turns |      Total_Net_Score |    Distance_Improvement% |   Energy_Achievement% |   Positive_Energy_Ratio% | Failure_Type   |
|:-----------|:------|:-----|:-----|---------:|---------:|----------:|---------:|---------:|:-------|
| script_003 | A     | Medium   | Yes    | 12       | 50       | 100       | 132      | 92.3     | -      |
| script_010 | A     | Medium   | Yes    | 13       | 45       |  96.7     | 100.1    | 85.7     | -      |
| script_011 | P     | Very Hard   | Yes    | 20       | 67       |  63.2     | 101.5    | 81       | -      |
| script_020 | A     | Easy   | Yes    | 12       | 50       | 100       | 165.5    | 92.3     | -      |
| script_021 | C     | Easy   | Yes    | 15       | 45       |  91.3     | 105      | 93.8     | -      |
| script_029 | C     | Easy   | Yes    | 13       | 43       | 100       | 112.3    | 92.9     | -      |
| script_042 | A     | Medium   | Yes    | 12       | 48       | 100       | 107.7    | 92.3     | -      |
| script_059 | C     | Hard   | Yes    | 13       | 49       |  90.6     | 100.7    | 92.9     | -      |
| script_063 | P     | Hard   | Yes    | 12       | 50       | 100       | 112.8    | 92.3     | -      |
| script_081 | C     | Medium   | Yes    | 15       | 50       | 100       | 104.3    | 93.8     | -      |
| script_095 | P     | Hard   | Yes    | 12       | 50       |  94.2     | 104      | 84.6     | -      |
| script_128 | A     | Hard   | Yes    | 14       | 54       | 100       | 114.3    | 86.7     | -      |
| script_161 | C     | Medium   | Yes    | 15       | 49       |  96.3     | 104      | 93.8     | -      |
| script_195 | P     | Medium   | Yes    | 12       | 49       | 100       | 112.4    | 92.3     | -      |
| script_215 | C     | Hard   | Yes    | 12       | 57       | 100       | 139.6    | 92.3     | -      |
| script_222 | C     | Hard   | Yes    | 12       | 58       | 100       | 135      | 92.3     | -      |
| script_238 | A     | Hard   | Yes    | 15       | 53       |  88       | 100.5    | 81.2     | -      |
| script_243 | A     | Hard   | Yes    | 15       | 52       | 100       | 101.4    | 93.8     | -      |
| script_262 | P     | Medium   | Yes    | 13       | 45       | 100       | 106.2    | 92.9     | -      |
| script_263 | P     | Medium   | Yes    | 12       | 46       | 100       | 117.8    | 92.3     | -      |
| script_269 | C     | Easy   | Yes    | 12       | 42       |  96       | 104      | 92.3     | -      |
| script_282 | A     | Hard   | Yes    | 12       | 53       | 100       | 123.4    | 92.3     | -      |
| script_288 | C     | Hard   | Yes    | 12       | 55       | 100       | 119.2    | 92.3     | -      |
| script_304 | P     | Medium   | Yes    | 12       | 56       | 100       | 136.7    | 92.3     | -      |
| script_327 | P     | Very Hard   | Yes    | 16       | 56       |  91.5     | 104.3    | 82.4     | -      |
| script_349 | P     | Very Hard   | Yes    | 15       | 57       |  97.3     | 102.7    | 93.8     | -      |
| script_355 | C     | Hard   | Yes    | 16       | 55       |  93.9     | 103      | 94.1     | -      |
| script_363 | P     | Very Hard   | Yes    | 12       | 51       |  93.7     | 102.9    | 92.3     | -      |
| script_366 | A     | Medium   | Yes    | 12       | 50       |  93.3     | 117.4    | 92.3     | -      |
| script_391 | A     | Very Hard   | Yes    | 12       | 58       | 100       | 122.4    | 84.6     | -      |
| Mean        |       |      |      | 13.3333  | 51.4333  |  96.2     | 113.77   | 90.6733  |        |
| Std        |       |      |      |  1.89979 |  5.33488 |   7.20306 |  15.2159 |  4.06244 |        |
| Min        |       |      |      | 12       | 42       |  63.2     | 100.1    | 81       |        |
| Max        |       |      |      | 20       | 67       | 100       | 165.5    | 94.1     |        |

*Full data available in CSV/Excel files*
